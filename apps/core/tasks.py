"""
Core infrastructure tasks for QuietPage.

This module contains Celery tasks for system-level operations:
- Database backups
- Backup cleanup
- Health monitoring

These tasks are scheduled to run periodically via Celery Beat.
"""

import os
import logging
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.db import connection
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def database_backup(self):
    """
    Create a database backup using Django's dumpdata command.

    For SQLite (development), creates a copy of the database file.
    For PostgreSQL (production), uses dumpdata to create JSON backup.

    Backups are stored in BASE_DIR/backups/ with timestamp.

    Returns:
        str: Path to the created backup file

    Raises:
        Exception: If backup fails (task will retry up to 3 times)
    """
    try:
        # Create backups directory if it doesn't exist
        backup_dir = settings.BACKUPS_DIR
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_config = settings.DATABASES['default']

        # Determine backup method based on database engine
        if 'sqlite3' in db_config['ENGINE']:
            # SQLite: Simple file copy
            db_path = Path(db_config['NAME'])
            backup_path = backup_dir / f'db_backup_{timestamp}.sqlite3'
            shutil.copy2(db_path, backup_path)
            logger.info(f"SQLite backup created: {backup_path}")

        elif 'postgres' in db_config['ENGINE'].lower():
            # PostgreSQL: Use pg_dump
            backup_path = backup_dir / f'db_backup_{timestamp}.sql.gz'

            pg_dump_cmd = [
                'pg_dump',
                '-h', db_config.get('HOST', 'localhost'),
                '-p', str(db_config.get('PORT', 5432)),
                '-U', db_config.get('USER', 'postgres'),
                '-d', db_config['NAME'],
                '--no-password',
            ]

            # Set up environment with password
            env = os.environ.copy()
            if db_config.get('PASSWORD'):
                env['PGPASSWORD'] = db_config['PASSWORD']

            # Run pg_dump
            pg_dump_result = subprocess.run(
                pg_dump_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )

            if pg_dump_result.returncode != 0:
                error_msg = f"pg_dump failed with return code {pg_dump_result.returncode}: {pg_dump_result.stderr.decode()}"
                logger.error(error_msg)
                raise Exception(error_msg)

            # Compress and write to file
            with open(backup_path, 'wb') as f:
                gzip_result = subprocess.run(
                    ['gzip'],
                    input=pg_dump_result.stdout,
                    stdout=f,
                    stderr=subprocess.PIPE
                )

                if gzip_result.returncode != 0:
                    error_msg = f"gzip compression failed with return code {gzip_result.returncode}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

            logger.info(f"PostgreSQL backup created: {backup_path}")

        else:
            # Other databases: Use dumpdata as fallback
            backup_path = backup_dir / f'db_backup_{timestamp}.json'
            with open(backup_path, 'w') as f:
                call_command('dumpdata', stdout=f, indent=2)
            logger.info(f"Database backup (dumpdata) created: {backup_path}")

        return str(backup_path)

    except Exception as e:
        logger.error(f"Database backup failed: {e}", exc_info=True)
        # Retry the task
        raise self.retry(exc=e)


@shared_task(bind=True)
def cleanup_old_backups(self, days=30):
    """
    Remove database backups older than specified number of days.

    Args:
        days (int): Delete backups older than this many days (default: 30)

    Returns:
        dict: {'deleted': int, 'errors': int}
    """
    try:
        backup_dir = settings.BACKUPS_DIR

        if not backup_dir.exists():
            logger.warning(f"Backup directory does not exist: {backup_dir}")
            return {'deleted': 0, 'errors': 0}

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted = 0
        errors = 0

        for backup_file in backup_dir.glob('db_backup_*'):
            try:
                # Get file modification time
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)

                if file_time < cutoff_date:
                    backup_file.unlink()
                    deleted += 1
                    logger.info(f"Deleted old backup: {backup_file.name}")

            except Exception as e:
                logger.error(f"Failed to delete backup {backup_file.name}: {e}")
                errors += 1

        logger.info(f"Backup cleanup complete: {deleted} deleted, {errors} errors")
        return {'deleted': deleted, 'errors': errors}

    except Exception as e:
        logger.error(f"Backup cleanup failed: {e}", exc_info=True)
        return {'deleted': 0, 'errors': 1}


@shared_task(bind=True, ignore_result=True)
def health_check(self):
    """
    Perform system health checks.

    Checks:
    - Database connectivity
    - Redis connectivity
    - Disk space availability

    Logs warnings if any checks fail.
    This task runs hourly to monitor system health.

    Returns:
        dict: Health check results
    """
    health_status = {
        'timestamp': datetime.now().isoformat(),
        'database': False,
        'redis': False,
        'disk_space': False,
    }

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['database'] = True
        logger.debug("Database health check: OK")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")

    # Check Redis connection
    try:
        from redis import Redis
        import redis.exceptions

        # Use dedicated Redis URL if available
        redis_url = getattr(settings, 'REDIS_URL', None) or getattr(settings, 'CACHE_REDIS_URL', None)

        if redis_url and redis_url.startswith('redis://'):
            redis_client = Redis.from_url(
                redis_url,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            redis_client.ping()
            health_status['redis'] = True
            logger.debug("Redis health check: OK")
        else:
            logger.debug("Redis health check: Skipped (no Redis URL configured)")
    except (redis.exceptions.RedisError, ConnectionError, TimeoutError) as e:
        logger.error(f"Redis health check failed: {e}")
        health_status['redis'] = False
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status['redis'] = False

    # Check disk space (warn if < 1GB free)
    try:
        disk_usage = shutil.disk_usage(settings.BASE_DIR)
        free_gb = disk_usage.free / (1024 ** 3)
        health_status['disk_space'] = free_gb > 1.0

        if free_gb < 1.0:
            logger.warning(f"Low disk space: {free_gb:.2f} GB free")
        else:
            logger.debug(f"Disk space health check: OK ({free_gb:.2f} GB free)")

    except Exception as e:
        logger.error(f"Disk space health check failed: {e}")

    # Log overall health status
    all_healthy = all(health_status.values())
    if all_healthy:
        logger.info("System health check: All systems operational")
    else:
        failed_checks = [k for k, v in health_status.items() if not v and k != 'timestamp']
        logger.warning(f"System health check: Failed checks: {', '.join(failed_checks)}")

    return health_status
