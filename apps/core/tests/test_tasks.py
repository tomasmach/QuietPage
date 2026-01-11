"""
Comprehensive tests for core app Celery tasks.

This module tests the infrastructure tasks for:
- Database backups
- Backup cleanup
- Health monitoring
"""

import pytest
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
from freezegun import freeze_time
from io import BytesIO

from django.conf import settings
from django.db import connection
from celery.exceptions import Retry

from apps.core.tasks import (
    database_backup,
    cleanup_old_backups,
    health_check,
)


@pytest.mark.unit
@pytest.mark.celery
class TestDatabaseBackup:
    """Test suite for database_backup task."""

    @patch('apps.core.tasks.shutil.copy2')
    def test_sqlite_backup_success(self, mock_copy, tmp_path, settings):
        """
        Test successful SQLite database backup.

        Why: SQLite backups should use simple file copy for reliability.
        """
        settings.BACKUPS_DIR = tmp_path / "backups"
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': str(tmp_path / 'db.sqlite3'),
            }
        }

        # Create fake database file
        db_path = tmp_path / 'db.sqlite3'
        db_path.write_text("fake db content")

        with freeze_time("2025-01-15 14:30:00"):
            result = database_backup()

        assert "db_backup_20250115_143000.sqlite3" in result
        mock_copy.assert_called_once()

    @patch('apps.core.tasks.subprocess.Popen')
    def test_postgres_backup_success(self, mock_popen, tmp_path, settings):
        """
        Test successful PostgreSQL database backup.

        Why: PostgreSQL backups should use pg_dump with streaming compression.
        """
        settings.BACKUPS_DIR = tmp_path / "backups"
        settings.BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'testdb',
                'USER': 'testuser',
                'PASSWORD': 'testpass',
                'HOST': 'localhost',
                'PORT': 5432,
            }
        }

        # Mock pg_dump process
        mock_pg_dump_proc = Mock()
        mock_pg_dump_proc.stdout = Mock()
        mock_pg_dump_proc.stdout.close = Mock()
        mock_pg_dump_proc.returncode = 0
        mock_pg_dump_proc.communicate.return_value = (b"", b"")

        # Mock gzip process
        mock_gzip_proc = Mock()
        mock_gzip_proc.returncode = 0
        mock_gzip_proc.communicate.return_value = (b"compressed", b"")

        mock_popen.side_effect = [mock_pg_dump_proc, mock_gzip_proc]

        with freeze_time("2025-01-15 14:30:00"):
            result = database_backup()

        assert "db_backup_20250115_143000.sql.gz" in result
        assert mock_popen.call_count == 2

        # Verify pg_dump was called with correct arguments
        pg_dump_call = mock_popen.call_args_list[0]
        assert 'pg_dump' in pg_dump_call[0][0]
        assert '-d' in pg_dump_call[0][0]
        assert 'testdb' in pg_dump_call[0][0]

    @patch('apps.core.tasks.subprocess.Popen')
    def test_postgres_backup_pg_dump_failure(self, mock_popen, tmp_path, settings):
        """
        Test handling of pg_dump failure.

        Why: Task should raise exception if pg_dump fails, allowing retry.
        """
        settings.BACKUPS_DIR = tmp_path / "backups"
        settings.BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'testdb',
                'USER': 'testuser',
                'PASSWORD': 'testpass',
                'HOST': 'localhost',
                'PORT': 5432,
            }
        }

        # Mock pg_dump process that fails
        mock_pg_dump_proc = Mock()
        mock_pg_dump_proc.stdout = Mock()
        mock_pg_dump_proc.stdout.close = Mock()
        mock_pg_dump_proc.returncode = 1
        mock_pg_dump_proc.communicate.return_value = (b"", b"pg_dump: connection failed")

        # Mock gzip process (will still be created)
        mock_gzip_proc = Mock()
        mock_gzip_proc.returncode = 0
        mock_gzip_proc.communicate.return_value = (b"", b"")

        mock_popen.side_effect = [mock_pg_dump_proc, mock_gzip_proc]

        with pytest.raises(Exception) as exc_info:
            database_backup()

        assert "pg_dump failed" in str(exc_info.value)

    @patch('apps.core.tasks.call_command')
    def test_other_database_uses_dumpdata(self, mock_call_command, tmp_path, settings):
        """
        Test backup for other database engines uses dumpdata fallback.

        Why: Unsupported databases should still get basic JSON backup.
        """
        settings.BACKUPS_DIR = tmp_path / "backups"
        settings.BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'testdb',
            }
        }

        with freeze_time("2025-01-15 14:30:00"):
            result = database_backup()

        assert "db_backup_20250115_143000.json" in result
        mock_call_command.assert_called_once_with('dumpdata', stdout=unittest.mock.ANY, indent=2)

    def test_backup_directory_created_if_not_exists(self, tmp_path, settings):
        """
        Test that backup directory is created if it doesn't exist.

        Why: First backup should create directory automatically.
        """
        settings.BACKUPS_DIR = tmp_path / "backups"
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': str(tmp_path / 'db.sqlite3'),
            }
        }

        # Create fake database file
        db_path = tmp_path / 'db.sqlite3'
        db_path.write_text("fake db")

        assert not settings.BACKUPS_DIR.exists()

        with patch('apps.core.tasks.shutil.copy2'):
            database_backup()

        assert settings.BACKUPS_DIR.exists()

    @patch('apps.core.tasks.shutil.copy2')
    def test_backup_retry_on_failure(self, mock_copy, tmp_path, settings):
        """
        Test that task retries on backup failure.

        Why: Transient failures (disk full, permissions) should trigger retry.
        """
        settings.BACKUPS_DIR = tmp_path / "backups"
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': str(tmp_path / 'db.sqlite3'),
            }
        }

        mock_copy.side_effect = Exception("Disk full")

        with pytest.raises(Exception):
            database_backup()


@pytest.mark.unit
@pytest.mark.celery
class TestCleanupOldBackups:
    """Test suite for cleanup_old_backups task."""

    def test_cleanup_old_backups_success(self, tmp_path, settings):
        """
        Test successful cleanup of old backups.

        Why: Backups older than retention period should be deleted.
        """
        settings.BACKUPS_DIR = tmp_path / "backups"
        settings.BACKUPS_DIR.mkdir(parents=True)

        # Create old and recent backups
        old_backup = settings.BACKUPS_DIR / "db_backup_20241201_120000.sqlite3"
        recent_backup = settings.BACKUPS_DIR / "db_backup_20250110_120000.sqlite3"
        old_backup.write_text("old")
        recent_backup.write_text("recent")

        # Set modification times
        old_time = (datetime.now() - timedelta(days=35)).timestamp()
        recent_time = (datetime.now() - timedelta(days=5)).timestamp()
        old_backup.touch()
        recent_backup.touch()

        import os
        os.utime(old_backup, (old_time, old_time))
        os.utime(recent_backup, (recent_time, recent_time))

        result = cleanup_old_backups(days=30)

        assert result['deleted'] == 1
        assert result['errors'] == 0
        assert not old_backup.exists()
        assert recent_backup.exists()

    def test_cleanup_no_backups_directory(self, tmp_path, settings):
        """
        Test cleanup when backup directory doesn't exist.

        Why: Task should handle missing directory gracefully.
        """
        settings.BACKUPS_DIR = tmp_path / "nonexistent"

        result = cleanup_old_backups()

        assert result['deleted'] == 0
        assert result['errors'] == 0

    def test_cleanup_empty_directory(self, tmp_path, settings):
        """
        Test cleanup with no backup files.

        Why: Empty directory should not cause errors.
        """
        settings.BACKUPS_DIR = tmp_path / "backups"
        settings.BACKUPS_DIR.mkdir()

        result = cleanup_old_backups()

        assert result['deleted'] == 0
        assert result['errors'] == 0

    def test_cleanup_custom_retention_period(self, tmp_path, settings):
        """
        Test cleanup with custom retention period.

        Why: Administrators should be able to configure retention.
        """
        settings.BACKUPS_DIR = tmp_path / "backups"
        settings.BACKUPS_DIR.mkdir()

        backup = settings.BACKUPS_DIR / "db_backup_20250101_120000.sqlite3"
        backup.write_text("content")

        # Set to 10 days old
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        import os
        os.utime(backup, (old_time, old_time))

        # Should delete with 7-day retention
        result = cleanup_old_backups(days=7)
        assert result['deleted'] == 1

    def test_cleanup_handles_individual_file_errors(self, tmp_path, settings):
        """
        Test that cleanup continues after individual file deletion errors.

        Why: One locked file shouldn't prevent cleanup of other files.
        """
        settings.BACKUPS_DIR = tmp_path / "backups"
        settings.BACKUPS_DIR.mkdir()

        backup1 = settings.BACKUPS_DIR / "db_backup_20241201_120000.sqlite3"
        backup2 = settings.BACKUPS_DIR / "db_backup_20241202_120000.sqlite3"
        backup1.write_text("content1")
        backup2.write_text("content2")

        # Set both to old
        old_time = (datetime.now() - timedelta(days=35)).timestamp()
        import os
        os.utime(backup1, (old_time, old_time))
        os.utime(backup2, (old_time, old_time))

        # Mock unlink to fail on first file
        original_unlink = Path.unlink
        def mock_unlink(self, *args, **kwargs):
            if "20241201" in str(self):
                raise PermissionError("File locked")
            return original_unlink(self, *args, **kwargs)

        with patch.object(Path, 'unlink', mock_unlink):
            result = cleanup_old_backups(days=30)

        assert result['deleted'] == 1
        assert result['errors'] == 1


@pytest.mark.unit
@pytest.mark.celery
class TestHealthCheck:
    """Test suite for health_check task."""

    def test_health_check_all_systems_healthy(self):
        """
        Test health check when all systems are operational.

        Why: Validates complete health check flow with all services up.
        """
        with patch('apps.core.tasks.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis.ping.return_value = True
            mock_redis_class.from_url.return_value = mock_redis

            with patch('apps.core.tasks.shutil.disk_usage') as mock_disk:
                mock_disk.return_value = Mock(free=5 * 1024**3)  # 5 GB free

                result = health_check()

        assert result['database'] is True
        assert result['redis'] is True
        assert result['disk_space'] is True
        assert 'timestamp' in result

    def test_health_check_database_failure(self):
        """
        Test health check when database is down.

        Why: Should detect and log database connectivity issues.
        """
        with patch('apps.core.tasks.connection.cursor') as mock_cursor:
            mock_cursor.side_effect = Exception("Connection refused")

            with patch('apps.core.tasks.Redis') as mock_redis_class:
                mock_redis = Mock()
                mock_redis.ping.return_value = True
                mock_redis_class.from_url.return_value = mock_redis

                with patch('apps.core.tasks.shutil.disk_usage') as mock_disk:
                    mock_disk.return_value = Mock(free=5 * 1024**3)

                    result = health_check()

        assert result['database'] is False
        assert result['redis'] is True

    def test_health_check_redis_failure(self):
        """
        Test health check when Redis is unavailable.

        Why: Should detect Redis connectivity issues without crashing.
        """
        with patch('apps.core.tasks.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis.ping.side_effect = Exception("Connection refused")
            mock_redis_class.from_url.return_value = mock_redis

            with patch('apps.core.tasks.shutil.disk_usage') as mock_disk:
                mock_disk.return_value = Mock(free=5 * 1024**3)

                result = health_check()

        assert result['database'] is True
        assert result['redis'] is False

    def test_health_check_low_disk_space(self):
        """
        Test health check when disk space is low.

        Why: Should warn when free space drops below 1GB threshold.
        """
        with patch('apps.core.tasks.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis.ping.return_value = True
            mock_redis_class.from_url.return_value = mock_redis

            with patch('apps.core.tasks.shutil.disk_usage') as mock_disk:
                mock_disk.return_value = Mock(free=500 * 1024**2)  # 500 MB

                result = health_check()

        assert result['disk_space'] is False

    def test_health_check_no_redis_url_configured(self, settings):
        """
        Test health check when Redis URL is not configured.

        Why: Should skip Redis check gracefully if not configured.
        """
        settings.REDIS_URL = None
        settings.CACHE_REDIS_URL = None

        with patch('apps.core.tasks.shutil.disk_usage') as mock_disk:
            mock_disk.return_value = Mock(free=5 * 1024**3)

            result = health_check()

        # Redis check should be skipped
        assert 'redis' in result

    def test_health_check_timestamp_format(self):
        """
        Test that health check includes ISO formatted timestamp.

        Why: Timestamp helps with monitoring and debugging.
        """
        with freeze_time("2025-01-15 14:30:00"):
            with patch('apps.core.tasks.Redis') as mock_redis_class:
                mock_redis = Mock()
                mock_redis.ping.return_value = True
                mock_redis_class.from_url.return_value = mock_redis

                with patch('apps.core.tasks.shutil.disk_usage') as mock_disk:
                    mock_disk.return_value = Mock(free=5 * 1024**3)

                    result = health_check()

        assert result['timestamp'] == "2025-01-15T14:30:00"

    def test_health_check_handles_redis_timeout(self):
        """
        Test health check when Redis times out.

        Why: Should handle timeout exceptions gracefully.
        """
        import redis.exceptions

        with patch('apps.core.tasks.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis.ping.side_effect = redis.exceptions.TimeoutError("Timeout")
            mock_redis_class.from_url.return_value = mock_redis

            with patch('apps.core.tasks.shutil.disk_usage') as mock_disk:
                mock_disk.return_value = Mock(free=5 * 1024**3)

                result = health_check()

        assert result['redis'] is False


# Import unittest.mock for ANY matcher
import unittest.mock
