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

# Import Redis at module level for test mocking
try:
    from redis import Redis
    import redis.exceptions
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None
    redis = None


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
            # PostgreSQL: Use pg_dump with streaming to avoid OOM
            backup_path = backup_dir / f'db_backup_{timestamp}.sql.gz'

            # Timeout for pg_dump (1 hour should be sufficient for most databases)
            backup_timeout = getattr(settings, 'BACKUP_TIMEOUT_SECONDS', 3600)

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

            # Stream pg_dump directly to gzip to avoid loading entire dump into memory
            with open(backup_path, 'wb') as f:
                pg_dump_proc = subprocess.Popen(
                    pg_dump_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )

                gzip_proc = subprocess.Popen(
                    ['gzip'],
                    stdin=pg_dump_proc.stdout,
                    stdout=f,
                    stderr=subprocess.PIPE
                )

                # Allow pg_dump to receive SIGPIPE if gzip exits
                pg_dump_proc.stdout.close()

                try:
                    # Wait for gzip to complete (it will finish when pg_dump closes its stdout)
                    gzip_stderr = gzip_proc.communicate(timeout=backup_timeout)[1]
                    gzip_returncode = gzip_proc.returncode

                    # Also wait for pg_dump to fully complete and get its stderr
                    pg_dump_stderr = pg_dump_proc.communicate(timeout=60)[1]
                    pg_dump_returncode = pg_dump_proc.returncode

                except subprocess.TimeoutExpired:
                    # Kill both processes on timeout
                    pg_dump_proc.kill()
                    gzip_proc.kill()
                    pg_dump_proc.wait()
                    gzip_proc.wait()
                    # Clean up partial backup
                    if backup_path.exists():
                        backup_path.unlink()
                    error_msg = f"Backup timed out after {backup_timeout} seconds"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                if pg_dump_returncode != 0:
                    # Clean up partial backup
                    if backup_path.exists():
                        backup_path.unlink()
                    error_msg = f"pg_dump failed with return code {pg_dump_returncode}: {pg_dump_stderr.decode()}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                if gzip_returncode != 0:
                    # Clean up partial backup
                    if backup_path.exists():
                        backup_path.unlink()
                    error_msg = f"gzip compression failed with return code {gzip_returncode}: {gzip_stderr.decode()}"
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
        # Only retry when running as a Celery task, not when called directly
        if not self.request.called_directly:
            raise self.retry(exc=e)
        raise


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
                    try:
                        backup_file.unlink()
                        deleted += 1
                        logger.info(f"Deleted old backup: {backup_file.name}")
                    except PermissionError as e:
                        logger.error(f"Permission denied deleting backup {backup_file.name}: {e}")
                        errors += 1
                    except Exception as e:
                        logger.error(f"Failed to delete backup {backup_file.name}: {e}")
                        errors += 1

            except Exception as e:
                logger.error(f"Failed to process backup {backup_file.name}: {e}")
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
    if REDIS_AVAILABLE:
        redis_client = None
        try:
            # Use dedicated Redis URL if available
            redis_url = getattr(settings, 'REDIS_URL', None) or getattr(settings, 'CACHE_REDIS_URL', None)

            if not redis_url:
                logger.debug("Redis health check: Skipped (no Redis URL configured)")
            elif redis_url.startswith('redis://'):
                redis_client = Redis.from_url(
                    redis_url,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                redis_client.ping()
                health_status['redis'] = True
                logger.debug("Redis health check: OK")
            else:
                logger.debug("Redis health check: Skipped (invalid Redis URL)")
        except (redis.exceptions.RedisError, ConnectionError, TimeoutError) as e:
            logger.error(f"Redis health check failed: {e}")
            health_status['redis'] = False
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            health_status['redis'] = False
        finally:
            if redis_client:
                try:
                    redis_client.close()
                except Exception as e:
                    logger.warning(f"Failed to close Redis connection: {e}")
    else:
        logger.debug("Redis health check: Skipped (Redis not available)")

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
