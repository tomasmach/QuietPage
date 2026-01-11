"""
Comprehensive tests for HealthCheckView.

This module tests the health check endpoint used by:
- Docker health checks
- Load balancers
- Uptime monitoring services
"""

import pytest
from unittest.mock import Mock, patch
from freezegun import freeze_time

from rest_framework import status
from rest_framework.test import APIClient

from django.urls import reverse


@pytest.mark.unit
@pytest.mark.api
class TestHealthCheckView:
    """Test suite for HealthCheckView."""

    def setup_method(self):
        """Set up test client for each test."""
        self.client = APIClient()
        self.url = reverse('health-check')

    def test_health_check_unauthenticated_access(self):
        """
        Test that health check is accessible without authentication.

        Why: Health check must be public for load balancers and monitoring.
        """
        response = self.client.get(self.url)

        # Should not return 401/403
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]

    @patch('apps.api.views.cache')
    def test_health_check_all_healthy(self, mock_cache):
        """
        Test health check when all components are healthy.

        Why: Should return 200 OK when everything is operational.
        """
        mock_cache.get.return_value = 'ok'
        mock_cache.set.return_value = True

        with patch('config.celery.app.control.inspect') as mock_inspect:
            mock_inspect_instance = Mock()
            mock_inspect_instance.active.return_value = {'worker1': []}
            mock_inspect.return_value = mock_inspect_instance

            response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'
        assert response.data['components']['database'] == 'healthy'
        assert response.data['components']['redis'] == 'healthy'
        assert response.data['components']['celery'] == 'healthy'
        assert 'timestamp' in response.data

    @patch('django.db.connection.cursor')
    @patch('apps.api.views.cache')
    def test_health_check_database_unhealthy(self, mock_cache, mock_cursor):
        """
        Test health check when database is down.

        Why: Should return 503 when database is unavailable.
        """
        mock_cursor.side_effect = Exception("Database connection failed")
        mock_cache.get.return_value = 'ok'
        mock_cache.set.return_value = True

        with patch('config.celery.app.control.inspect') as mock_inspect:
            mock_inspect_instance = Mock()
            mock_inspect_instance.active.return_value = {'worker1': []}
            mock_inspect.return_value = mock_inspect_instance

            response = self.client.get(self.url)

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data['status'] == 'unhealthy'
        assert response.data['components']['database'] == 'unhealthy'

    @patch('apps.api.views.cache')
    def test_health_check_redis_unhealthy(self, mock_cache):
        """
        Test health check when Redis cache is down.

        Why: Should return 503 when cache is unavailable.
        """
        mock_cache.set.side_effect = Exception("Redis connection failed")

        with patch('config.celery.app.control.inspect') as mock_inspect:
            mock_inspect_instance = Mock()
            mock_inspect_instance.active.return_value = {'worker1': []}
            mock_inspect.return_value = mock_inspect_instance

            response = self.client.get(self.url)

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data['status'] == 'unhealthy'
        assert response.data['components']['redis'] == 'unhealthy'

    @patch('apps.api.views.cache')
    def test_health_check_redis_read_failure(self, mock_cache):
        """
        Test health check when Redis can write but not read.

        Why: Both read and write must work for healthy cache.
        """
        mock_cache.set.return_value = True
        mock_cache.get.return_value = None  # Read failed

        with patch('config.celery.app.control.inspect') as mock_inspect:
            mock_inspect_instance = Mock()
            mock_inspect_instance.active.return_value = {'worker1': []}
            mock_inspect.return_value = mock_inspect_instance

            response = self.client.get(self.url)

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data['components']['redis'] == 'unhealthy'

    @patch('apps.api.views.cache')
    def test_health_check_celery_no_workers(self, mock_cache):
        """
        Test health check when no Celery workers are active.

        Why: Should mark Celery as degraded when no workers available.
        """
        mock_cache.get.return_value = 'ok'
        mock_cache.set.return_value = True

        with patch('config.celery.app.control.inspect') as mock_inspect:
            mock_inspect_instance = Mock()
            mock_inspect_instance.active.return_value = None  # No workers
            mock_inspect.return_value = mock_inspect_instance

            response = self.client.get(self.url)

        # Should still return 200 since Celery is degraded, not critical
        assert response.status_code == status.HTTP_200_OK
        assert response.data['components']['celery'] == 'degraded'

    @patch('apps.api.views.cache')
    def test_health_check_celery_empty_workers(self, mock_cache):
        """
        Test health check when Celery returns empty workers dict.

        Why: Empty dict means no workers are running.
        """
        mock_cache.get.return_value = 'ok'
        mock_cache.set.return_value = True

        with patch('config.celery.app.control.inspect') as mock_inspect:
            mock_inspect_instance = Mock()
            mock_inspect_instance.active.return_value = {}  # Empty dict
            mock_inspect.return_value = mock_inspect_instance

            response = self.client.get(self.url)

        assert response.data['components']['celery'] == 'degraded'

    @patch('apps.api.views.cache')
    def test_health_check_celery_exception(self, mock_cache):
        """
        Test health check when Celery inspect raises exception.

        Why: Should mark Celery as degraded on connection errors.
        """
        mock_cache.get.return_value = 'ok'
        mock_cache.set.return_value = True

        with patch('config.celery.app.control.inspect') as mock_inspect:
            mock_inspect.side_effect = Exception("Celery connection error")

            response = self.client.get(self.url)

        assert response.data['components']['celery'] == 'degraded'

    @freeze_time("2025-01-15 14:30:00")
    @patch('apps.api.views.cache')
    def test_health_check_timestamp_format(self, mock_cache):
        """
        Test that health check includes ISO formatted timestamp.

        Why: Timestamp helps with debugging and monitoring.
        """
        mock_cache.get.return_value = 'ok'
        mock_cache.set.return_value = True

        with patch('config.celery.app.control.inspect') as mock_inspect:
            mock_inspect_instance = Mock()
            mock_inspect_instance.active.return_value = {'worker1': []}
            mock_inspect.return_value = mock_inspect_instance

            response = self.client.get(self.url)

        assert 'timestamp' in response.data
        # Should be ISO format
        assert '2025-01-15' in response.data['timestamp']
        assert '14:30:00' in response.data['timestamp']

    @patch('apps.api.views.cache')
    def test_health_check_response_structure(self, mock_cache):
        """
        Test that response has expected structure.

        Why: Monitoring tools rely on consistent response format.
        """
        mock_cache.get.return_value = 'ok'
        mock_cache.set.return_value = True

        with patch('config.celery.app.control.inspect') as mock_inspect:
            mock_inspect_instance = Mock()
            mock_inspect_instance.active.return_value = {'worker1': []}
            mock_inspect.return_value = mock_inspect_instance

            response = self.client.get(self.url)

        assert 'status' in response.data
        assert 'timestamp' in response.data
        assert 'components' in response.data
        assert isinstance(response.data['components'], dict)
        assert 'database' in response.data['components']
        assert 'redis' in response.data['components']
        assert 'celery' in response.data['components']

    @patch('django.db.connection.cursor')
    @patch('apps.api.views.cache')
    def test_health_check_multiple_failures(self, mock_cache, mock_cursor):
        """
        Test health check when multiple components fail.

        Why: Should report all failures in components dict.
        """
        mock_cursor.side_effect = Exception("Database down")
        mock_cache.set.side_effect = Exception("Redis down")

        with patch('config.celery.app.control.inspect') as mock_inspect:
            mock_inspect.side_effect = Exception("Celery down")

            response = self.client.get(self.url)

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data['status'] == 'unhealthy'
        assert response.data['components']['database'] == 'unhealthy'
        assert response.data['components']['redis'] == 'unhealthy'
        assert response.data['components']['celery'] == 'degraded'

    @patch('apps.api.views.cache')
    def test_health_check_get_method_only(self, mock_cache):
        """
        Test that health check only accepts GET requests.

        Why: Health checks should be read-only operations.
        """
        mock_cache.get.return_value = 'ok'
        mock_cache.set.return_value = True

        # Try POST
        response = self.client.post(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # Try PUT
        response = self.client.put(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # Try DELETE
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @patch('apps.api.views.cache')
    def test_health_check_database_query(self, mock_cache):
        """
        Test that health check executes simple database query.

        Why: Validates actual database connectivity, not just connection pool.
        """
        mock_cache.get.return_value = 'ok'
        mock_cache.set.return_value = True

        with patch('config.celery.app.control.inspect') as mock_inspect:
            mock_inspect_instance = Mock()
            mock_inspect_instance.active.return_value = {'worker1': []}
            mock_inspect.return_value = mock_inspect_instance

            with patch('django.db.connection.cursor') as mock_cursor:
                mock_cursor_instance = Mock()
                mock_cursor.return_value.__enter__ = Mock(return_value=mock_cursor_instance)
                mock_cursor.return_value.__exit__ = Mock(return_value=False)

                response = self.client.get(self.url)

                # Verify SELECT 1 was executed
                mock_cursor_instance.execute.assert_called_once_with("SELECT 1")

        assert response.data['components']['database'] == 'healthy'

    @patch('apps.api.views.cache')
    def test_health_check_logs_errors(self, mock_cache):
        """
        Test that health check logs component failures.

        Why: Errors should be logged for debugging without exposing details.
        """
        mock_cache.set.side_effect = Exception("Redis connection timeout")

        with patch('apps.api.views.logger') as mock_logger:
            with patch('config.celery.app.control.inspect') as mock_inspect:
                mock_inspect_instance = Mock()
                mock_inspect_instance.active.return_value = {'worker1': []}
                mock_inspect.return_value = mock_inspect_instance

                response = self.client.get(self.url)

            # Verify error was logged
            assert mock_logger.error.called

    @patch('apps.api.views.cache')
    def test_health_check_celery_with_workers(self, mock_cache):
        """
        Test health check with multiple active Celery workers.

        Why: Should recognize healthy state with multiple workers.
        """
        mock_cache.get.return_value = 'ok'
        mock_cache.set.return_value = True

        with patch('config.celery.app.control.inspect') as mock_inspect:
            mock_inspect_instance = Mock()
            mock_inspect_instance.active.return_value = {
                'worker1@host1': [],
                'worker2@host2': [],
                'worker3@host3': []
            }
            mock_inspect.return_value = mock_inspect_instance

            response = self.client.get(self.url)

        assert response.data['components']['celery'] == 'healthy'
