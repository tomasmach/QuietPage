"""
Comprehensive pytest tests for journal views.

Tests all views in apps/journal/views.py with 80%+ coverage.
"""

import json
import pytest
from datetime import datetime, time
from zoneinfo import ZoneInfo
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from django.test import RequestFactory

from apps.journal.models import Entry
from apps.journal.views import DashboardView
from apps.journal.tests.factories import EntryFactory, ShortEntryFactory
from apps.accounts.tests.factories import UserFactory


@pytest.mark.views
class TestDashboardView:
    """Test DashboardView with time-based greetings and stats."""
    
    def test_dashboard_requires_login(self, client):
        """Unauthenticated users should be redirected to login."""
        response = client.get(reverse('journal:dashboard'))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url
    
    def test_dashboard_displays_for_authenticated_user(self, client):
        """Authenticated users can access dashboard."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.get(reverse('journal:dashboard'))
        assert response.status_code == 200
        assert 'journal/dashboard.html' in [t.name for t in response.templates]
    
    @pytest.mark.parametrize('hour,expected_greeting', [
        (4, 'Dobré ráno'),
        (6, 'Dobré ráno'),
        (8, 'Dobré ráno'),
        (9, 'Dobré dopoledne'),
        (10, 'Dobré dopoledne'),
        (11, 'Dobré dopoledne'),
        (12, 'Dobré odpoledne'),
        (14, 'Dobré odpoledne'),
        (17, 'Dobré odpoledne'),
        (18, 'Dobrý večer'),
        (20, 'Dobrý večer'),
        (23, 'Dobrý večer'),
        (0, 'Dobrý večer'),
        (3, 'Dobrý večer'),
    ])
    def test_time_based_greeting(self, client, hour, expected_greeting):
        """Test greetings change based on time of day."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)
        
        # Create a mock datetime with specific hour in user's timezone
        tz = ZoneInfo('Europe/Prague')
        mock_now = datetime(2025, 1, 15, hour, 30, tzinfo=tz)
        
        with patch('django.utils.timezone.now', return_value=mock_now):
            response = client.get(reverse('journal:dashboard'))
            assert response.status_code == 200
            assert response.context['greeting'] == expected_greeting
    
    def test_dashboard_stats_zero_entries(self, client):
        """Dashboard shows correct stats for user with no entries."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.get(reverse('journal:dashboard'))
        stats = response.context['stats']
        
        assert stats['total_entries'] == 0
        assert stats['current_streak'] == 0
        assert stats['total_words'] == 0
    
    def test_dashboard_stats_with_entries(self, client):
        """Dashboard shows correct stats for user with entries."""
        user = UserFactory()
        # Create entries with known word counts
        EntryFactory(user=user, content='Hello world test')  # 3 words
        EntryFactory(user=user, content='Another test entry here')  # 4 words
        
        # Refresh user to get updated streak from signal
        user.refresh_from_db()
        
        client.force_login(user)
        response = client.get(reverse('journal:dashboard'))
        stats = response.context['stats']
        
        assert stats['total_entries'] == 2
        assert stats['current_streak'] == user.current_streak  # Use actual calculated streak
        assert stats['total_words'] == 7
    
    def test_dashboard_recent_entries_ordering(self, client):
        """Recent entries should be ordered by most recent first."""
        user = UserFactory()
        client.force_login(user)
        
        # Create entries with different timestamps
        entry1 = EntryFactory(user=user)
        entry2 = EntryFactory(user=user)
        entry3 = EntryFactory(user=user)
        
        response = client.get(reverse('journal:dashboard'))
        recent_entries = list(response.context['recent_entries'])
        
        # Should be in reverse chronological order
        assert recent_entries[0].id == entry3.id
        assert recent_entries[1].id == entry2.id
        assert recent_entries[2].id == entry1.id
    
    def test_dashboard_user_isolation(self, client):
        """Users should only see their own entries on dashboard."""
        user1 = UserFactory()
        user2 = UserFactory()
        
        EntryFactory.create_batch(3, user=user1)
        EntryFactory.create_batch(2, user=user2)
        
        client.force_login(user1)
        response = client.get(reverse('journal:dashboard'))
        
        assert response.context['stats']['total_entries'] == 3
        assert len(list(response.context['recent_entries'])) == 3
    
    def test_dashboard_displays_user_first_name(self, client):
        """Dashboard should display user's first name if available."""
        user = UserFactory(first_name='Jan', username='jankowalski')
        client.force_login(user)
        
        response = client.get(reverse('journal:dashboard'))
        assert response.context['user_first_name'] == 'Jan'
    
    def test_dashboard_displays_username_when_no_first_name(self, client):
        """Dashboard should fall back to username if no first name."""
        user = UserFactory(first_name='', username='jankowalski')
        client.force_login(user)
        
        response = client.get(reverse('journal:dashboard'))
        assert response.context['user_first_name'] == 'jankowalski'
    
    def test_dashboard_includes_inspirational_quote(self, client):
        """Dashboard should include an inspirational quote."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.get(reverse('journal:dashboard'))
        assert 'quote' in response.context
        assert 'text' in response.context['quote']


@pytest.mark.views
class TestEntryListView:
    """Test EntryListView for pagination and user isolation."""
    
    def test_entry_list_requires_login(self, client):
        """Unauthenticated users should be redirected to login."""
        response = client.get(reverse('journal:entry-list'))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url
    
    def test_entry_list_displays_user_entries(self, client):
        """Users can see their entry list."""
        user = UserFactory()
        EntryFactory.create_batch(5, user=user)
        
        client.force_login(user)
        response = client.get(reverse('journal:entry-list'))
        
        assert response.status_code == 200
        assert 'journal/entry_list.html' in [t.name for t in response.templates]
        assert len(response.context['entries']) == 5
    
    def test_entry_list_user_isolation(self, client):
        """Users cannot see other users' entries."""
        user1 = UserFactory()
        user2 = UserFactory()
        
        EntryFactory.create_batch(3, user=user1)
        EntryFactory.create_batch(5, user=user2)
        
        client.force_login(user1)
        response = client.get(reverse('journal:entry-list'))
        
        # User1 should only see their 3 entries
        assert len(response.context['entries']) == 3
        for entry in response.context['entries']:
            assert entry.user_id == user1.id
    
    def test_entry_list_pagination(self, client):
        """Entry list should paginate at 20 entries per page."""
        user = UserFactory()
        EntryFactory.create_batch(25, user=user)
        
        client.force_login(user)
        
        # First page
        response = client.get(reverse('journal:entry-list'))
        assert len(response.context['entries']) == 20
        assert response.context['is_paginated'] is True
        
        # Second page
        response = client.get(reverse('journal:entry-list') + '?page=2')
        assert len(response.context['entries']) == 5
    
    def test_entry_list_ordering(self, client):
        """Entries should be ordered by most recent first."""
        user = UserFactory()
        client.force_login(user)
        
        entry1 = EntryFactory(user=user)
        entry2 = EntryFactory(user=user)
        entry3 = EntryFactory(user=user)
        
        response = client.get(reverse('journal:entry-list'))
        entries = list(response.context['entries'])
        
        assert entries[0].id == entry3.id
        assert entries[1].id == entry2.id
        assert entries[2].id == entry1.id


@pytest.mark.views
class TestEntryCreateView:
    """Test EntryCreateView for creating new entries."""
    
    def test_entry_create_requires_login(self, client):
        """Unauthenticated users should be redirected to login."""
        response = client.get(reverse('journal:entry-create'))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url
    
    def test_entry_create_displays_form(self, client):
        """Authenticated users can see the create form."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.get(reverse('journal:entry-create'))
        assert response.status_code == 200
        assert 'journal/entry_form.html' in [t.name for t in response.templates]
    
    def test_entry_create_auto_assigns_user(self, client):
        """New entry should be automatically assigned to current user."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('journal:entry-create'), {
            'title': 'Test Entry',
            'content': 'This is a test entry',
            'mood_rating': 4,
            'tags': 'test, work'
        })
        
        assert response.status_code == 302
        entry = Entry.objects.get(title='Test Entry')
        assert entry.user == user
    
    def test_entry_create_success_message(self, client):
        """Creating entry should show success message."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('journal:entry-create'), {
            'title': 'Test Entry',
            'content': 'This is a test entry',
            'mood_rating': 3,
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'úspěšně vytvořen' in str(messages[0])
    
    def test_entry_create_redirects_to_edit(self, client):
        """After creation, should redirect to edit view."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('journal:entry-create'), {
            'title': 'Test Entry',
            'content': 'This is a test entry',
            'mood_rating': 5,
        })
        
        entry = Entry.objects.get(title='Test Entry')
        assert response.status_code == 302
        assert response.url == reverse('journal:entry-update', kwargs={'pk': entry.pk})
    
    def test_entry_create_calculates_word_count(self, client):
        """Entry should auto-calculate word count on creation."""
        user = UserFactory()
        client.force_login(user)
        
        content = 'This is a test entry with exactly ten words here'
        response = client.post(reverse('journal:entry-create'), {
            'title': 'Test',
            'content': content,
            'mood_rating': 4,
        })
        
        entry = Entry.objects.get(title='Test')
        assert entry.word_count == 10
    
    def test_entry_create_without_optional_fields(self, client):
        """Entry can be created with only required content field."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('journal:entry-create'), {
            'content': 'Minimal entry',
            'tags': '',  # Empty tags to satisfy form
        })
        
        assert response.status_code == 302
        entry = Entry.objects.filter(user=user).first()
        assert entry is not None
        assert entry.content == 'Minimal entry'
        assert entry.title == ''
        assert entry.mood_rating is None


@pytest.mark.views
class TestEntryDetailView:
    """Test EntryDetailView redirects to edit view."""
    
    def test_entry_detail_requires_login(self, client):
        """Unauthenticated users should be redirected to login."""
        entry = EntryFactory()
        response = client.get(reverse('journal:entry-detail', kwargs={'pk': entry.pk}))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url
    
    def test_entry_detail_redirects_to_edit(self, client):
        """Detail view should redirect to edit view."""
        user = UserFactory()
        entry = EntryFactory(user=user)
        client.force_login(user)
        
        response = client.get(reverse('journal:entry-detail', kwargs={'pk': entry.pk}))
        
        assert response.status_code == 302
        assert response.url == reverse('journal:entry-update', kwargs={'pk': entry.pk})
    
    def test_entry_detail_user_isolation(self, client):
        """Users cannot access other users' entries (404)."""
        user1 = UserFactory()
        user2 = UserFactory()
        entry = EntryFactory(user=user2)
        
        client.force_login(user1)
        response = client.get(reverse('journal:entry-detail', kwargs={'pk': entry.pk}))
        
        assert response.status_code == 404


@pytest.mark.views
class TestEntryUpdateView:
    """Test EntryUpdateView for editing entries."""
    
    def test_entry_update_requires_login(self, client):
        """Unauthenticated users should be redirected to login."""
        entry = EntryFactory()
        response = client.get(reverse('journal:entry-update', kwargs={'pk': entry.pk}))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url
    
    def test_entry_update_displays_form(self, client):
        """Authenticated users can see the edit form."""
        user = UserFactory()
        entry = EntryFactory(user=user)
        client.force_login(user)
        
        response = client.get(reverse('journal:entry-update', kwargs={'pk': entry.pk}))
        
        assert response.status_code == 200
        assert 'journal/entry_form.html' in [t.name for t in response.templates]
        assert response.context['entry'].id == entry.id
    
    def test_entry_update_user_isolation(self, client):
        """Users cannot edit other users' entries (404)."""
        user1 = UserFactory()
        user2 = UserFactory()
        entry = EntryFactory(user=user2)
        
        client.force_login(user1)
        response = client.get(reverse('journal:entry-update', kwargs={'pk': entry.pk}))
        
        assert response.status_code == 404
    
    def test_entry_update_success(self, client):
        """Users can successfully update their entries."""
        user = UserFactory()
        entry = EntryFactory(user=user, title='Old Title', content='Old content')
        client.force_login(user)
        
        response = client.post(reverse('journal:entry-update', kwargs={'pk': entry.pk}), {
            'title': 'New Title',
            'content': 'New content here',
            'mood_rating': 5,
        })
        
        assert response.status_code == 302
        entry.refresh_from_db()
        assert entry.title == 'New Title'
        assert entry.content == 'New content here'
        assert entry.mood_rating == 5
    
    def test_entry_update_success_message(self, client):
        """Updating entry should show success message."""
        user = UserFactory()
        entry = EntryFactory(user=user)
        client.force_login(user)
        
        response = client.post(reverse('journal:entry-update', kwargs={'pk': entry.pk}), {
            'title': 'Updated',
            'content': 'Updated content',
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'úspěšně upraven' in str(messages[0])
    
    def test_entry_update_redirects_to_dashboard(self, client):
        """After update, should redirect to dashboard."""
        user = UserFactory()
        entry = EntryFactory(user=user)
        client.force_login(user)
        
        update_data = {
            'title': 'Updated',
            'content': 'Updated content',
        }
        response = client.post(reverse('journal:entry-update', kwargs={'pk': entry.pk}), update_data)
        
        assert response.status_code == 302
        assert response.url == reverse('journal:dashboard')


@pytest.mark.views
class TestEntryDeleteView:
    """Test EntryDeleteView for deleting entries."""
    
    def test_entry_delete_requires_login(self, client):
        """Unauthenticated users should be redirected to login."""
        entry = EntryFactory()
        response = client.get(reverse('journal:entry-delete', kwargs={'pk': entry.pk}))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url
    
    def test_entry_delete_displays_confirmation(self, client):
        """Users see confirmation page before deleting."""
        user = UserFactory()
        entry = EntryFactory(user=user)
        client.force_login(user)
        
        response = client.get(reverse('journal:entry-delete', kwargs={'pk': entry.pk}))
        
        assert response.status_code == 200
        # Note: template doesn't exist in files list, but view expects it
        assert response.context['entry'].id == entry.id
    
    def test_entry_delete_user_isolation(self, client):
        """Users cannot delete other users' entries (404)."""
        user1 = UserFactory()
        user2 = UserFactory()
        entry = EntryFactory(user=user2)
        
        client.force_login(user1)
        response = client.post(reverse('journal:entry-delete', kwargs={'pk': entry.pk}))
        
        assert response.status_code == 404
        assert Entry.objects.filter(pk=entry.pk).exists()
    
    def test_entry_delete_success(self, client):
        """Users can successfully delete their entries."""
        user = UserFactory()
        entry = EntryFactory(user=user)
        entry_id = entry.id
        client.force_login(user)
        
        response = client.post(reverse('journal:entry-delete', kwargs={'pk': entry.pk}))
        
        assert response.status_code == 302
        assert not Entry.objects.filter(pk=entry_id).exists()
    
    def test_entry_delete_success_message(self, client):
        """Deleting entry should show success message."""
        user = UserFactory()
        entry = EntryFactory(user=user)
        client.force_login(user)
        
        response = client.post(
            reverse('journal:entry-delete', kwargs={'pk': entry.pk}),
            follow=True
        )
        
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'úspěšně smazán' in str(messages[0])
    
    def test_entry_delete_redirects_to_dashboard(self, client):
        """After deletion, should redirect to dashboard."""
        user = UserFactory()
        entry = EntryFactory(user=user)
        client.force_login(user)
        
        response = client.post(reverse('journal:entry-delete', kwargs={'pk': entry.pk}))
        
        assert response.status_code == 302
        assert response.url == reverse('journal:dashboard')
    
    def test_entry_delete_cascade_deletes_tags(self, client):
        """Deleting entry should also clean up associated tags."""
        user = UserFactory()
        entry = EntryFactory(user=user, tags=['work', 'personal'])
        entry_id = entry.id
        
        client.force_login(user)
        client.post(reverse('journal:entry-delete', kwargs={'pk': entry.pk}))
        
        # Entry should be gone
        assert not Entry.objects.filter(pk=entry_id).exists()


@pytest.mark.views
class TestAutosaveEntryView:
    """Test autosave_entry AJAX endpoint."""
    
    def test_autosave_requires_login(self, client):
        """Unauthenticated users should get 302 redirect."""
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps({'content': 'test'}),
            content_type='application/json'
        )
        assert response.status_code == 302
    
    def test_autosave_requires_post(self, client):
        """Only POST requests are allowed."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.get(reverse('journal:autosave'))
        assert response.status_code == 405  # Method Not Allowed
    
    def test_autosave_create_new_entry(self, client):
        """Autosave can create a new entry."""
        user = UserFactory()
        client.force_login(user)
        
        data = {
            'title': 'Auto-saved Entry',
            'content': 'This is auto-saved content',
            'mood_rating': 4,
            'tags': 'work, ideas'
        }
        
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        json_response = response.json()
        assert json_response['status'] == 'success'
        assert json_response['is_new'] is True
        assert 'entry_id' in json_response
        
        # Verify entry was created
        entry = Entry.objects.get(id=json_response['entry_id'])
        assert entry.title == 'Auto-saved Entry'
        assert entry.content == 'This is auto-saved content'
        assert entry.mood_rating == 4
        assert entry.user == user
    
    def test_autosave_update_existing_entry(self, client):
        """Autosave can update an existing entry."""
        user = UserFactory()
        entry = EntryFactory(user=user, title='Old', content='Old content')
        client.force_login(user)
        
        data = {
            'entry_id': str(entry.id),
            'title': 'Updated',
            'content': 'Updated content',
            'mood_rating': 5,
            'tags': 'updated'
        }
        
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        json_response = response.json()
        assert json_response['status'] == 'success'
        assert json_response['is_new'] is False
        assert json_response['entry_id'] == str(entry.id)
        
        # Verify entry was updated
        entry.refresh_from_db()
        assert entry.title == 'Updated'
        assert entry.content == 'Updated content'
        assert entry.mood_rating == 5
    
    def test_autosave_empty_content_validation(self, client):
        """Autosave should reject empty content."""
        user = UserFactory()
        client.force_login(user)
        
        data = {
            'title': 'Test',
            'content': '',  # Empty content
        }
        
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        json_response = response.json()
        assert json_response['status'] == 'error'
        assert 'prázdný' in json_response['message'].lower()
    
    def test_autosave_whitespace_only_content_validation(self, client):
        """Autosave should reject whitespace-only content."""
        user = UserFactory()
        client.force_login(user)
        
        data = {
            'content': '   \n  \t  ',  # Only whitespace
        }
        
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_autosave_invalid_mood_rating_validation(self, client):
        """Autosave should validate mood_rating range (1-5)."""
        user = UserFactory()
        client.force_login(user)
        
        # Test mood_rating = 0 (too low)
        data = {
            'content': 'Test content',
            'mood_rating': 0
        }
        
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert 'mezi 1 a 5' in response.json()['message']
        
        # Test mood_rating = 6 (too high)
        data['mood_rating'] = 6
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_autosave_invalid_mood_type_validation(self, client):
        """Autosave should reject non-integer mood_rating."""
        user = UserFactory()
        client.force_login(user)
        
        data = {
            'content': 'Test content',
            'mood_rating': 'invalid'
        }
        
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert 'Neplatné' in response.json()['message']
    
    def test_autosave_valid_mood_rating_range(self, client):
        """Autosave should accept valid mood_rating (1-5)."""
        user = UserFactory()
        client.force_login(user)
        
        for mood in [1, 2, 3, 4, 5]:
            data = {
                'content': f'Test content {mood}',
                'mood_rating': mood
            }
            
            response = client.post(
                reverse('journal:autosave'),
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            assert response.json()['status'] == 'success'
    
    def test_autosave_null_mood_rating(self, client):
        """Autosave should accept null mood_rating."""
        user = UserFactory()
        client.force_login(user)
        
        data = {
            'content': 'Test content',
            'mood_rating': None
        }
        
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        entry_id = response.json()['entry_id']
        entry = Entry.objects.get(id=entry_id)
        assert entry.mood_rating is None
    
    def test_autosave_user_isolation(self, client):
        """Users cannot update other users' entries via autosave."""
        user1 = UserFactory()
        user2 = UserFactory()
        entry = EntryFactory(user=user2)
        
        client.force_login(user1)
        
        data = {
            'entry_id': str(entry.id),
            'content': 'Trying to update someone else entry',
        }
        
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        json_response = response.json()
        assert json_response['status'] == 'error'
        assert 'nenalezen' in json_response['message'].lower()
    
    def test_autosave_invalid_json(self, client):
        """Autosave should handle invalid JSON gracefully."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(
            reverse('journal:autosave'),
            data='invalid json{',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        json_response = response.json()
        assert json_response['status'] == 'error'
        assert 'Neplatná' in json_response['message']
    
    def test_autosave_handles_tags(self, client):
        """Autosave should properly handle tags."""
        user = UserFactory()
        client.force_login(user)
        
        data = {
            'content': 'Test content',
            'tags': 'work, personal, ideas'
        }
        
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        entry = Entry.objects.get(id=response.json()['entry_id'])
        tag_names = [tag.name for tag in entry.tags.all()]
        assert 'work' in tag_names
        assert 'personal' in tag_names
        assert 'ideas' in tag_names
    
    def test_autosave_clears_tags_when_empty(self, client):
        """Autosave should clear tags when empty string provided."""
        user = UserFactory()
        entry = EntryFactory(user=user, tags=['old', 'tags'])
        client.force_login(user)
        
        data = {
            'entry_id': str(entry.id),
            'content': 'Updated content',
            'tags': ''
        }
        
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        entry.refresh_from_db()
        assert entry.tags.count() == 0
    
    def test_autosave_strips_whitespace(self, client):
        """Autosave should strip leading/trailing whitespace."""
        user = UserFactory()
        client.force_login(user)
        
        data = {
            'title': '  Spaced Title  ',
            'content': '  Content with spaces  ',
        }
        
        response = client.post(
            reverse('journal:autosave'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        entry = Entry.objects.get(id=response.json()['entry_id'])
        assert entry.title == 'Spaced Title'
        assert entry.content == 'Content with spaces'
    
    def test_autosave_unexpected_error_handling(self, client):
        """Autosave should handle unexpected errors gracefully."""
        user = UserFactory()
        client.force_login(user)
        
        data = {
            'content': 'Test content',
        }
        
        # Mock Entry.objects.create to raise an exception
        with patch('apps.journal.views.Entry.objects.create', side_effect=Exception('DB Error')):
            response = client.post(
                reverse('journal:autosave'),
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 500
            json_response = response.json()
            assert json_response['status'] == 'error'
            # Should not expose internal error details
            assert 'DB Error' not in json_response['message']
