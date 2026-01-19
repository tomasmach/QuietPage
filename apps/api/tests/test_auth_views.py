"""Tests for authentication views."""

import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from apps.accounts.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestRegisterView:
    """Test user registration endpoint."""

    @patch('apps.accounts.tasks.send_welcome_email_async.delay')
    def test_register_success(self, mock_welcome_email, client):
        """Test successful user registration sends welcome email."""
        url = reverse('api:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }

        response = client.post(url, data, content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.json()

        # Verify user was created
        user = User.objects.get(username='newuser')
        assert user.email == 'newuser@example.com'

        # Verify welcome email task was called
        mock_welcome_email.assert_called_once_with(user_id=user.id)

    def test_register_password_mismatch(self, client):
        """Test registration fails when passwords don't match."""
        url = reverse('api:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass123!'
        }

        response = client.post(url, data, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.json()

    def test_register_duplicate_username(self, client):
        """Test registration fails with duplicate username."""
        UserFactory(username='existinguser')
        url = reverse('api:register')
        data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }

        response = client.post(url, data, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.json()

    def test_register_duplicate_email(self, client):
        """Test registration fails with duplicate email."""
        UserFactory(email='existing@example.com')
        url = reverse('api:register')
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }

        response = client.post(url, data, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.json()


@pytest.mark.integration
@pytest.mark.django_db
class TestLoginView:
    """Test user login endpoint."""

    def test_login_with_username(self, client):
        """Test login with username."""
        user = UserFactory(username='testuser')
        user.set_password('TestPass123!')
        user.save()

        url = reverse('api:login')
        data = {
            'username_or_email': 'testuser',
            'password': 'TestPass123!'
        }

        response = client.post(url, data, content_type='application/json')

        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.json()
        assert response.json()['user']['username'] == 'testuser'

    def test_login_with_email(self, client):
        """Test login with email."""
        user = UserFactory(email='test@example.com')
        user.set_password('TestPass123!')
        user.save()

        url = reverse('api:login')
        data = {
            'username_or_email': 'test@example.com',
            'password': 'TestPass123!'
        }

        response = client.post(url, data, content_type='application/json')

        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.json()

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        user = UserFactory(username='testuser')
        user.set_password('TestPass123!')
        user.save()

        url = reverse('api:login')
        data = {
            'username_or_email': 'testuser',
            'password': 'WrongPassword!'
        }

        response = client.post(url, data, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.json()

    def test_login_inactive_user(self, client):
        """Test login fails for inactive user."""
        user = UserFactory(username='testuser', is_active=False)
        user.set_password('TestPass123!')
        user.save()

        url = reverse('api:login')
        data = {
            'username_or_email': 'testuser',
            'password': 'TestPass123!'
        }

        response = client.post(url, data, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.json()


@pytest.mark.integration
@pytest.mark.django_db
class TestLogoutView:
    """Test user logout endpoint."""

    def test_logout_success(self, client):
        """Test successful logout."""
        user = UserFactory()
        client.force_login(user)

        url = reverse('api:logout')
        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.json()

    def test_logout_unauthenticated(self, client):
        """Test logout requires authentication."""
        url = reverse('api:logout')
        response = client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
@pytest.mark.django_db
class TestCurrentUserView:
    """Test current user endpoint."""

    def test_get_current_user(self, client):
        """Test getting current user data."""
        user = UserFactory(username='testuser', email='test@example.com')
        client.force_login(user)

        url = reverse('api:current-user')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.json()
        assert response.json()['user']['username'] == 'testuser'

    def test_get_current_user_unauthenticated(self, client):
        """Test current user endpoint requires authentication."""
        url = reverse('api:current-user')
        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
@pytest.mark.django_db
class TestCSRFTokenView:
    """Test CSRF token endpoint."""

    def test_get_csrf_token(self, client):
        """Test getting CSRF token."""
        url = reverse('api:csrf-token')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'csrfToken' in response.json()
        assert response.json()['csrfToken'] is not None
