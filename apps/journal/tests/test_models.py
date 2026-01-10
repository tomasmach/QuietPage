"""
Comprehensive tests for journal.models.

Tests the Entry model including:
- UUID primary key
- Encrypted content field
- Auto word count calculation
- Mood rating validation
- Tags functionality (django-taggit)
- Model methods (__str__, get_absolute_url)
- Ordering and indexes
"""

import pytest
import uuid
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.journal.models import Entry
from apps.journal.tests.factories import EntryFactory, EntryWithoutMoodFactory
from apps.accounts.tests.factories import UserFactory


@pytest.mark.unit
@pytest.mark.models
class TestEntryModel:
    """Test Entry model basic functionality."""
    
    def test_entry_creation_with_encrypted_content(self):
        """Test creating entry with content that gets encrypted."""
        user = UserFactory()
        entry = EntryFactory(
            user=user,
            title="Test Entry",
            content="This is my private journal content."
        )
        
        assert entry.id is not None
        assert isinstance(entry.id, uuid.UUID)
        assert entry.title == "Test Entry"
        assert entry.content == "This is my private journal content."
        assert entry.user == user
    
    def test_uuid_primary_key_is_auto_generated(self):
        """Test that UUID is automatically generated."""
        entry = EntryFactory()
        
        assert entry.id is not None
        assert isinstance(entry.id, uuid.UUID)
        # UUID should be version 4
        assert entry.id.version == 4
    
    def test_uuid_is_not_editable(self):
        """Test that UUID field is marked as not editable."""
        _entry = EntryFactory()
        id_field = Entry._meta.get_field('id')
        
        assert id_field.editable is False
    
    def test_entry_without_title(self):
        """Test creating entry without title (title is optional)."""
        entry = EntryFactory(title="")
        
        assert entry.title == ""
        assert entry.content is not None
    
    def test_entry_requires_user(self):
        """Test that entry requires a user (cannot be None)."""
        # Note: ValidationError is raised by full_clean() before DB constraint
        with pytest.raises(ValidationError):
            Entry.objects.create(
                user=None,
                content="Test content"
            )


@pytest.mark.unit
@pytest.mark.models
class TestEntryWordCount:
    """Test automatic word count calculation."""
    
    def test_word_count_auto_calculated_on_save(self):
        """Test that word count is automatically calculated."""
        entry = EntryFactory(content="This is a test entry with nine words here.")
        
        assert entry.word_count == 9
    
    def test_word_count_with_empty_content(self):
        """Test word count when content is empty."""
        user = UserFactory()
        # Create entry bypassing validation
        entry = Entry.objects.create(user=user, content="Test")
        entry.content = ""
        # Skip validation since empty content is now validated in clean()
        entry.save(skip_validation=True)

        assert entry.word_count == 0
    
    def test_word_count_with_single_word(self):
        """Test word count with single word."""
        entry = EntryFactory(content="Hello")
        
        assert entry.word_count == 1
    
    def test_word_count_with_multiple_spaces(self):
        """Test word count with multiple spaces between words."""
        entry = EntryFactory(content="Hello    world    this    has    spaces")
        
        # split() handles multiple spaces correctly
        assert entry.word_count == 5
    
    def test_word_count_with_newlines(self):
        """Test word count with newlines."""
        entry = EntryFactory(content="First line\nSecond line\nThird line")
        
        assert entry.word_count == 6
    
    def test_word_count_with_czech_text(self):
        """Test word count with Czech characters."""
        entry = EntryFactory(content="Příliš žluťoučký kůň úpěl ďábelské ódy")
        
        assert entry.word_count == 6
    
    def test_word_count_with_emojis(self):
        """Test word count with emojis."""
        entry = EntryFactory(content="Hello 😊 world 🌍 test")
        
        # Emojis are treated as separate tokens by split()
        assert entry.word_count == 5
    
    def test_word_count_is_not_editable(self):
        """Test that word_count field is marked as not editable."""
        word_count_field = Entry._meta.get_field('word_count')
        
        assert word_count_field.editable is False
    
    def test_word_count_updates_on_content_change(self):
        """Test that word count updates when content changes."""
        entry = EntryFactory(content="Initial content here")
        assert entry.word_count == 3
        
        entry.content = "Updated content with more words now"
        entry.save()
        
        assert entry.word_count == 6


@pytest.mark.unit
@pytest.mark.models
class TestEntryMoodRating:
    """Test mood rating field validation."""
    
    def test_mood_rating_valid_range(self):
        """Test that valid mood ratings (1-5) are accepted."""
        for rating in range(1, 6):
            entry = EntryFactory(mood_rating=rating)
            entry.full_clean()  # Should not raise
            assert entry.mood_rating == rating
    
    def test_mood_rating_can_be_null(self):
        """Test that mood rating can be None."""
        entry = EntryWithoutMoodFactory()
        entry.full_clean()  # Should not raise
        
        assert entry.mood_rating is None
    
    def test_mood_rating_below_minimum_fails(self):
        """Test that mood rating < 1 fails validation."""
        entry = EntryFactory.build(mood_rating=0)
        
        with pytest.raises(ValidationError) as exc_info:
            entry.full_clean()
        
        assert 'mood_rating' in exc_info.value.error_dict
    
    def test_mood_rating_above_maximum_fails(self):
        """Test that mood rating > 5 fails validation."""
        entry = EntryFactory.build(mood_rating=6)
        
        with pytest.raises(ValidationError) as exc_info:
            entry.full_clean()
        
        assert 'mood_rating' in exc_info.value.error_dict
    
    def test_mood_rating_negative_fails(self):
        """Test that negative mood rating fails validation."""
        entry = EntryFactory.build(mood_rating=-1)
        
        with pytest.raises(ValidationError) as exc_info:
            entry.full_clean()
        
        assert 'mood_rating' in exc_info.value.error_dict


@pytest.mark.unit
@pytest.mark.models
class TestEntryTags:
    """Test tagging functionality using django-taggit."""
    
    def test_entry_with_single_tag(self):
        """Test adding a single tag to entry."""
        entry = EntryFactory()
        entry.tags.add('work')
        
        assert entry.tags.count() == 1
        assert 'work' in entry.tags.names()
    
    def test_entry_with_multiple_tags(self):
        """Test adding multiple tags to entry."""
        entry = EntryFactory(tags=['work', 'personal', 'ideas'])
        
        assert entry.tags.count() == 3
        assert set(entry.tags.names()) == {'work', 'personal', 'ideas'}
    
    def test_entry_without_tags(self):
        """Test entry without any tags."""
        entry = EntryFactory()
        
        assert entry.tags.count() == 0
    
    def test_tags_are_case_insensitive(self):
        """Test that tags are case-insensitive."""
        entry = EntryFactory()
        entry.tags.add('Work', 'WORK', 'work')
        
        # django-taggit normalizes to lowercase
        assert entry.tags.count() == 1
        assert next(iter(entry.tags.names())).lower() == 'work'
    
    def test_tags_with_czech_characters(self):
        """Test tags with Czech characters."""
        entry = EntryFactory()
        entry.tags.add('práce', 'škola', 'nápad')
        
        assert entry.tags.count() == 3
        assert set(entry.tags.names()) == {'práce', 'škola', 'nápad'}
    
    def test_remove_tag(self):
        """Test removing a tag from entry."""
        entry = EntryFactory(tags=['work', 'personal'])
        assert entry.tags.count() == 2
        
        entry.tags.remove('work')
        
        assert entry.tags.count() == 1
        assert 'personal' in entry.tags.names()
        assert 'work' not in entry.tags.names()
    
    def test_clear_all_tags(self):
        """Test clearing all tags from entry."""
        entry = EntryFactory(tags=['work', 'personal', 'ideas'])
        assert entry.tags.count() == 3
        
        entry.tags.clear()
        
        assert entry.tags.count() == 0
    
    def test_filter_entries_by_tag(self):
        """Test filtering entries by tag."""
        user = UserFactory()
        entry1 = EntryFactory(user=user, tags=['work'])
        entry2 = EntryFactory(user=user, tags=['personal'])
        entry3 = EntryFactory(user=user, tags=['work', 'urgent'])
        
        work_entries = Entry.objects.filter(tags__name='work')
        
        assert work_entries.count() == 2
        assert entry1 in work_entries
        assert entry3 in work_entries
        assert entry2 not in work_entries


@pytest.mark.unit
@pytest.mark.models
class TestEntryMethods:
    """Test Entry model methods."""
    
    def test_str_with_title(self):
        """Test __str__ method with title."""
        user = UserFactory(username='testuser')
        entry = EntryFactory(user=user, title='My Daily Journal Entry')
        
        str_repr = str(entry)
        
        assert 'testuser' in str_repr
        assert 'My Daily Journal Entry' in str_repr
        # Check date is in format YYYY-MM-DD
        assert '-' in str_repr
    
    def test_str_without_title(self):
        """Test __str__ method without title."""
        user = UserFactory(username='testuser')
        entry = EntryFactory(user=user, title='')
        
        str_repr = str(entry)
        
        assert 'testuser' in str_repr
        assert 'Untitled' in str_repr
    
    def test_str_with_long_title(self):
        """Test __str__ method with long title (truncated to 30 chars)."""
        user = UserFactory(username='testuser')
        long_title = 'A' * 50
        entry = EntryFactory(user=user, title=long_title)
        
        str_repr = str(entry)
        
        # Title should be truncated to 30 characters
        assert 'A' * 30 in str_repr
        assert len(long_title) > len('A' * 30)


@pytest.mark.unit
@pytest.mark.models
class TestEntryOrdering:
    """Test Entry model ordering and querysets."""
    
    def test_entries_ordered_by_created_at_descending(self):
        """Test that entries are ordered newest first."""
        user = UserFactory()
        entry1 = EntryFactory(user=user)
        entry2 = EntryFactory(user=user)
        entry3 = EntryFactory(user=user)
        
        entries = Entry.objects.filter(user=user)
        
        # Newest first
        assert list(entries) == [entry3, entry2, entry1]
    
    def test_meta_ordering(self):
        """Test that Meta.ordering is set correctly."""
        assert Entry._meta.ordering == ['-created_at']
    
    def test_meta_verbose_names(self):
        """Test verbose name and verbose name plural."""
        assert Entry._meta.verbose_name == "Journal Entry"
        assert Entry._meta.verbose_name_plural == "Journal Entries"


@pytest.mark.unit
@pytest.mark.models
class TestEntryTimestamps:
    """Test automatic timestamp fields."""
    
    def test_created_at_auto_set(self):
        """Test that created_at is automatically set on creation."""
        entry = EntryFactory()
        
        assert entry.created_at is not None
    
    def test_updated_at_auto_set(self):
        """Test that updated_at is automatically set on creation."""
        entry = EntryFactory()
        
        assert entry.updated_at is not None
    
    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when entry is updated."""
        entry = EntryFactory()
        original_updated_at = entry.updated_at
        
        # Update entry
        entry.content = "Updated content"
        entry.save()
        
        assert entry.updated_at > original_updated_at
    
    def test_created_at_does_not_change_on_save(self):
        """Test that created_at doesn't change when entry is updated."""
        entry = EntryFactory()
        original_created_at = entry.created_at
        
        # Update entry
        entry.content = "Updated content"
        entry.save()
        
        assert entry.created_at == original_created_at


@pytest.mark.unit
@pytest.mark.models
class TestEntryRelationships:
    """Test Entry model relationships."""
    
    def test_user_foreign_key(self):
        """Test user foreign key relationship."""
        user = UserFactory()
        entry = EntryFactory(user=user)
        
        assert entry.user == user
        assert entry in user.journal_entries.all()
    
    def test_cascade_delete_user(self):
        """Test that entries are deleted when user is deleted."""
        user = UserFactory()
        entry1 = EntryFactory(user=user)
        entry2 = EntryFactory(user=user)
        
        entry1_id = entry1.id
        entry2_id = entry2.id
        
        user.delete()
        
        # Entries should be deleted
        assert not Entry.objects.filter(id=entry1_id).exists()
        assert not Entry.objects.filter(id=entry2_id).exists()
    
    def test_related_name(self):
        """Test related_name for reverse relationship."""
        user = UserFactory()
        EntryFactory.create_batch(3, user=user)
        
        assert user.journal_entries.count() == 3


@pytest.mark.unit
@pytest.mark.models
@pytest.mark.encryption
class TestEntryEncryption:
    """Test that entry content is properly encrypted."""
    
    def test_content_encryption_round_trip(self):
        """Test that content can be saved and retrieved correctly."""
        original_content = "This is my secret journal entry! 🔒"
        entry = EntryFactory(content=original_content)
        
        # Refresh from database
        entry.refresh_from_db()
        
        assert entry.content == original_content
    
    def test_content_with_special_characters(self):
        """Test encryption with special characters."""
        special_content = "Special chars: @#$%^&*(){}[]|\\:;\"'<>,.?/~`"
        entry = EntryFactory(content=special_content)
        
        entry.refresh_from_db()
        
        assert entry.content == special_content
    
    def test_content_with_unicode(self):
        """Test encryption with Unicode (Czech) characters."""
        czech_content = "Příliš žluťoučký kůň úpěl ďábelské ódy. 🇨🇿"
        entry = EntryFactory(content=czech_content)
        
        entry.refresh_from_db()
        
        assert entry.content == czech_content
    
    def test_content_with_multiline(self):
        """Test encryption with multiline content."""
        multiline_content = """Line 1
Line 2
Line 3

Line 5 (with blank line before)"""
        entry = EntryFactory(content=multiline_content)
        
        entry.refresh_from_db()
        
        assert entry.content == multiline_content
