"""
Tests for AutosaveView endpoint.

This module tests the autosave endpoint functionality, including
protection against editing past entries.
"""

import pytest
import json
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from apps.journal.models import Entry
from apps.accounts.tests.factories import UserFactory
from apps.journal.tests.factories import EntryFactory


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.integration
class TestAutosaveView:
    """Test suite for AutosaveView."""

    def test_create_new_entry(self, client):
        """Test creating a new entry via autosave."""
        user = UserFactory()
        client.force_login(user)

        data = {
            'title': 'Test Entry',
            'content': 'This is a test entry',
            'mood_rating': 4
        }

        response = client.post(
            reverse('api:entry-autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data['status'] == 'success'
        assert response_data['is_new'] is True
        assert 'entry_id' in response_data

        # Verify entry was created
        entry = Entry.objects.get(id=response_data['entry_id'])
        assert entry.title == 'Test Entry'
        assert entry.content == 'This is a test entry'
        assert entry.mood_rating == 4

    def test_update_todays_entry(self, client):
        """Test updating today's entry via autosave (should succeed)."""
        user = UserFactory()
        client.force_login(user)

        # Create an entry
        entry = EntryFactory(
            user=user,
            title='Original Title',
            content='Original content'
        )

        # Update the entry
        data = {
            'entry_id': str(entry.id),
            'title': 'Updated Title',
            'content': 'Updated content',
            'mood_rating': 5
        }

        response = client.post(
            reverse('api:entry-autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data['status'] == 'success'
        assert response_data['is_new'] is False

        # Verify entry was updated
        entry.refresh_from_db()
        assert entry.title == 'Updated Title'
        assert entry.content == 'Updated content'
        assert entry.mood_rating == 5

    def test_cannot_update_past_entry(self, client):
        """Test that updating a past entry is blocked (403 Forbidden)."""
        user = UserFactory()
        client.force_login(user)

        # Create an entry from 2 days ago
        old_entry = EntryFactory(
            user=user,
            title='Old Entry',
            content='This is an old entry',
            created_at=timezone.now() - timedelta(days=2)
        )

        # Try to update the old entry
        data = {
            'entry_id': str(old_entry.id),
            'title': 'Trying to update',
            'content': 'This should fail',
            'mood_rating': 3
        }

        response = client.post(
            reverse('api:entry-autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_data = response.json()
        assert response_data['status'] == 'error'
        assert response_data['message'] == 'Cannot edit past entries'

        # Verify entry was NOT updated
        old_entry.refresh_from_db()
        assert old_entry.title == 'Old Entry'
        assert old_entry.content == 'This is an old entry'

    def test_empty_content_validation(self, client):
        """Test that empty content is rejected."""
        user = UserFactory()
        client.force_login(user)

        data = {
            'title': 'Test Entry',
            'content': '',
            'mood_rating': 4
        }

        response = client.post(
            reverse('api:entry-autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data['status'] == 'error'

    def test_nonexistent_entry_update(self, client):
        """Test updating a non-existent entry returns 404."""
        user = UserFactory()
        client.force_login(user)

        data = {
            'entry_id': '00000000-0000-0000-0000-000000000000',
            'title': 'Test',
            'content': 'Test content'
        }

        response = client.post(
            reverse('api:entry-autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert response_data['status'] == 'error'

    def test_cannot_update_other_users_entry(self, client):
        """Test that users cannot update entries belonging to other users."""
        user = UserFactory()
        other_user = UserFactory(username='other_user')
        client.force_login(user)

        # Create entry for different user
        other_entry = EntryFactory(
            user=other_user,
            title='Other User Entry',
            content='This belongs to someone else'
        )

        # Try to update other user's entry
        data = {
            'entry_id': str(other_entry.id),
            'title': 'Hacked',
            'content': 'Should not work'
        }

        response = client.post(
            reverse('api:entry-autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify entry was NOT updated
        other_entry.refresh_from_db()
        assert other_entry.title == 'Other User Entry'

    def test_unauthenticated_access(self, client):
        """Test that unauthenticated requests are rejected."""
        data = {
            'title': 'Test',
            'content': 'Test content'
        }

        response = client.post(
            reverse('api:entry-autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
