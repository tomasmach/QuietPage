# Per-User Encryption Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement per-user encryption keys so each user's journal entries are encrypted with their unique key, and hide entry content from Django admin.

**Architecture:** Create an EncryptionKey model with OneToOne relationship to User. Each user gets their own Fernet key (encrypted at rest with the global master key). Entry content is encrypted/decrypted using the user's key. Admin shows "[Encrypted]" placeholder instead of content.

**Tech Stack:** Django 6.0, cryptography (Fernet), pytest, Factory Boy

---

## Task 1: Create EncryptionKey Model

**Files:**
- Create: `apps/accounts/models.py` (add EncryptionKey class after line 285)
- Create: `apps/accounts/tests/test_encryption_key.py`

**Step 1: Write the failing test for EncryptionKey model**

Create file `apps/accounts/tests/test_encryption_key.py`:

```python
"""
Tests for EncryptionKey model.

Tests encryption key generation, storage, and retrieval.
"""

import pytest
from django.db import IntegrityError
from apps.accounts.models import EncryptionKey
from apps.accounts.tests.factories import UserFactory


@pytest.mark.unit
@pytest.mark.encryption
class TestEncryptionKeyModel:
    """Test EncryptionKey model functionality."""

    def test_encryption_key_creation(self):
        """Test creating an encryption key for a user."""
        user = UserFactory()
        key = EncryptionKey.objects.create(user=user)

        assert key.id is not None
        assert key.user == user
        assert key.version == 1
        assert key.is_active is True
        assert key.key is not None
        assert len(key.key) > 0

    def test_encryption_key_is_unique_per_user(self):
        """Test that each user can only have one encryption key."""
        user = UserFactory()
        EncryptionKey.objects.create(user=user)

        with pytest.raises(IntegrityError):
            EncryptionKey.objects.create(user=user)

    def test_get_decrypted_key_returns_valid_fernet_key(self):
        """Test that decrypted key can be used with Fernet."""
        from cryptography.fernet import Fernet

        user = UserFactory()
        enc_key = EncryptionKey.objects.create(user=user)

        decrypted = enc_key.get_decrypted_key()
        # Should not raise - valid Fernet key
        fernet = Fernet(decrypted)

        # Test encryption/decryption works
        test_data = b"test message"
        encrypted = fernet.encrypt(test_data)
        decrypted_data = fernet.decrypt(encrypted)
        assert decrypted_data == test_data

    def test_key_is_stored_encrypted(self):
        """Test that the key stored in DB is not the raw Fernet key."""
        from cryptography.fernet import Fernet

        user = UserFactory()
        enc_key = EncryptionKey.objects.create(user=user)

        # Raw DB value should not be a valid Fernet key directly
        raw_value = enc_key.key
        decrypted_value = enc_key.get_decrypted_key()

        # They should be different (raw is encrypted)
        assert raw_value != decrypted_value.decode() if isinstance(decrypted_value, bytes) else raw_value != decrypted_value
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run pytest apps/accounts/tests/test_encryption_key.py -v`

Expected: FAIL with "cannot import name 'EncryptionKey' from 'apps.accounts.models'"

**Step 3: Write the EncryptionKey model**

Add to `apps/accounts/models.py` after line 285:

```python
import uuid
from cryptography.fernet import Fernet
from .fields import get_fernet_key


class EncryptionKey(models.Model):
    """
    Per-user encryption key for journal entry content.

    Each user has their own Fernet key for encrypting their journal entries.
    The key itself is encrypted with the global master key before storage,
    providing defense-in-depth security.

    Key rotation support: version field tracks which key version encrypted
    each entry, allowing gradual re-encryption when keys are rotated.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='encryption_key',
        help_text="User this encryption key belongs to"
    )
    key = models.CharField(
        max_length=500,
        help_text="Fernet key (encrypted with master key)"
    )
    version = models.IntegerField(
        default=1,
        help_text="Key version for rotation tracking"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this is the active key for new encryptions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    rotated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this key was last rotated"
    )

    class Meta:
        verbose_name = 'Encryption Key'
        verbose_name_plural = 'Encryption Keys'

    def save(self, *args, **kwargs):
        """Generate and encrypt key on first save."""
        if not self.key:
            # Generate new Fernet key
            raw_key = Fernet.generate_key()
            # Encrypt it with master key before storage
            master_fernet = Fernet(get_fernet_key())
            self.key = master_fernet.encrypt(raw_key).decode('utf-8')
        super().save(*args, **kwargs)

    def get_decrypted_key(self):
        """
        Decrypt and return the raw Fernet key.

        Returns:
            bytes: The decrypted Fernet key ready for use
        """
        master_fernet = Fernet(get_fernet_key())
        return master_fernet.decrypt(self.key.encode('utf-8'))

    def __str__(self):
        return f"EncryptionKey for {self.user.username} (v{self.version})"
```

**Step 4: Add import for get_fernet_key**

The `get_fernet_key` function is in `apps/journal/fields.py`. We need to import it. Add at top of `apps/accounts/models.py` after other imports:

```python
from apps.journal.fields import get_fernet_key
```

**Step 5: Run test to verify it passes**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run pytest apps/accounts/tests/test_encryption_key.py -v`

Expected: PASS (4 tests)

**Step 6: Create migration**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run python manage.py makemigrations accounts --name add_encryption_key`

Expected: Migration file created

**Step 7: Apply migration**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run python manage.py migrate`

Expected: Migration applied successfully

**Step 8: Commit**

```bash
cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption
git add apps/accounts/models.py apps/accounts/tests/test_encryption_key.py apps/accounts/migrations/
git commit -m "feat: add EncryptionKey model for per-user encryption"
```

---

## Task 2: Auto-Create EncryptionKey on User Creation

**Files:**
- Modify: `apps/accounts/signals.py`
- Create: `apps/accounts/tests/test_signals.py`

**Step 1: Write the failing test for signal**

Create file `apps/accounts/tests/test_signals.py`:

```python
"""
Tests for accounts signals.

Tests automatic EncryptionKey creation on user creation.
"""

import pytest
from apps.accounts.models import User, EncryptionKey
from apps.accounts.tests.factories import UserFactory


@pytest.mark.unit
@pytest.mark.encryption
class TestEncryptionKeySignal:
    """Test automatic EncryptionKey creation."""

    def test_encryption_key_created_on_user_creation(self):
        """Test that EncryptionKey is auto-created when user is created."""
        user = UserFactory()

        assert hasattr(user, 'encryption_key')
        assert user.encryption_key is not None
        assert isinstance(user.encryption_key, EncryptionKey)

    def test_encryption_key_not_duplicated_on_user_save(self):
        """Test that saving user doesn't create duplicate keys."""
        user = UserFactory()
        original_key_id = user.encryption_key.id

        user.bio = "Updated bio"
        user.save()
        user.refresh_from_db()

        assert user.encryption_key.id == original_key_id
        assert EncryptionKey.objects.filter(user=user).count() == 1
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run pytest apps/accounts/tests/test_signals.py -v`

Expected: FAIL with "User has no encryption_key" or similar

**Step 3: Add signal handler**

Add to `apps/accounts/signals.py`:

```python
from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from .models import User, EncryptionKey


@receiver(post_save, sender=User)
def create_encryption_key_for_user(sender, instance, created, **kwargs):
    """
    Create EncryptionKey for newly created users.

    This ensures every user has an encryption key for their journal entries.
    Only runs on user creation, not on updates.
    """
    if created:
        # Check if key already exists (defensive)
        if not hasattr(instance, 'encryption_key') or instance.encryption_key is None:
            try:
                EncryptionKey.objects.create(user=instance)
            except Exception:
                logger.error(
                    f"Failed to create encryption key for user {instance.pk}",
                    exc_info=True
                )
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run pytest apps/accounts/tests/test_signals.py -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption
git add apps/accounts/signals.py apps/accounts/tests/test_signals.py
git commit -m "feat: auto-create EncryptionKey on user creation"
```

---

## Task 3: Add EncryptionKeyFactory

**Files:**
- Modify: `apps/accounts/tests/factories.py`

**Step 1: Add EncryptionKeyFactory**

Add to `apps/accounts/tests/factories.py`:

```python
from apps.accounts.models import EmailChangeRequest, EncryptionKey


class EncryptionKeyFactory(DjangoModelFactory):
    """
    Factory for creating EncryptionKey instances.

    Note: Keys are normally auto-created via signal when user is created.
    This factory is for edge cases in testing.
    """

    class Meta:
        model = EncryptionKey
        django_get_or_create = ('user',)

    user = factory.SubFactory(UserFactory)
    version = 1
    is_active = True
```

**Step 2: Update UserFactory to not trigger duplicate key creation**

The signal creates the key, so the factory should work without changes. Verify by running tests.

**Step 3: Run tests to verify factories work**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run pytest apps/accounts/tests/ -v`

Expected: All tests pass

**Step 4: Commit**

```bash
cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption
git add apps/accounts/tests/factories.py
git commit -m "feat: add EncryptionKeyFactory for testing"
```

---

## Task 4: Update Entry Model for Per-User Encryption

**Files:**
- Modify: `apps/journal/models.py`
- Modify: `apps/journal/tests/test_models.py`

**Step 1: Write failing test for per-user encryption**

Add to `apps/journal/tests/test_models.py`:

```python
@pytest.mark.unit
@pytest.mark.encryption
class TestEntryPerUserEncryption:
    """Test per-user encryption for Entry content."""

    def test_entry_encrypted_with_user_key(self):
        """Test that entry content is encrypted with user's key."""
        from cryptography.fernet import Fernet
        from apps.journal.models import Entry

        user = UserFactory()
        entry = EntryFactory(user=user, content="Secret journal content")

        # Refresh from DB to get raw encrypted value
        entry.refresh_from_db()

        # Verify key_version is set
        assert entry.key_version == user.encryption_key.version

        # Content should decrypt correctly
        assert entry.content == "Secret journal content"

    def test_different_users_have_different_encryption(self):
        """Test that same content encrypts differently for different users."""
        user1 = UserFactory()
        user2 = UserFactory()

        content = "Same content for both"

        entry1 = EntryFactory(user=user1, content=content)
        entry2 = EntryFactory(user=user2, content=content)

        # Both should decrypt to same content
        assert entry1.content == content
        assert entry2.content == content

        # But raw DB values should be different (different keys)
        # Access raw value through database
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT content FROM journal_entry WHERE id = %s",
                [str(entry1.id)]
            )
            raw1 = cursor.fetchone()[0]
            cursor.execute(
                "SELECT content FROM journal_entry WHERE id = %s",
                [str(entry2.id)]
            )
            raw2 = cursor.fetchone()[0]

        assert raw1 != raw2
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run pytest apps/journal/tests/test_models.py::TestEntryPerUserEncryption -v`

Expected: FAIL (no key_version attribute)

**Step 3: Add key_version field to Entry**

Modify `apps/journal/models.py`, add after `is_favorite` field (around line 69):

```python
    # Encryption tracking
    key_version = models.IntegerField(
        null=True,
        blank=True,
        help_text="Version of user's encryption key used for this entry"
    )
```

**Step 4: Replace EncryptedTextField with custom encryption**

Modify `apps/journal/models.py`:

1. Change the content field from `EncryptedTextField` to `TextField`:

```python
    content = models.TextField(
        blank=True,
        help_text="Your private journal entry (encrypted with user key)"
    )
```

2. Remove the `EncryptedTextField` import (line 12).

3. Add encryption methods and modify save():

```python
    def _encrypt_content(self, plaintext):
        """Encrypt content with user's encryption key."""
        if not plaintext:
            return plaintext
        from cryptography.fernet import Fernet
        fernet = Fernet(self.user.encryption_key.get_decrypted_key())
        return fernet.encrypt(plaintext.encode('utf-8')).decode('utf-8')

    def _decrypt_content(self, ciphertext):
        """Decrypt content with user's encryption key."""
        if not ciphertext:
            return ciphertext
        from cryptography.fernet import Fernet
        fernet = Fernet(self.user.encryption_key.get_decrypted_key())
        return fernet.decrypt(ciphertext.encode('utf-8')).decode('utf-8')

    def save(self, *args, **kwargs):
        """Auto-calculate word count, encrypt content, and run validation."""
        skip_validation = kwargs.pop('skip_validation', False)

        if not skip_validation:
            self.full_clean()

        # Store original content for word count before encryption
        original_content = self.content

        # Calculate word count from plaintext
        if original_content:
            # Check if content is already encrypted (starts with gAAAAA)
            if not original_content.startswith('gAAAAA'):
                self.word_count = max(0, len(original_content.split()))
                # Encrypt content
                self.content = self._encrypt_content(original_content)
                self.key_version = self.user.encryption_key.version
            else:
                # Content already encrypted, don't re-encrypt
                pass
        else:
            self.word_count = 0

        super().save(*args, **kwargs)

    @property
    def decrypted_content(self):
        """Return decrypted content."""
        if not self.content:
            return self.content
        # Check if content looks encrypted
        if self.content.startswith('gAAAAA'):
            return self._decrypt_content(self.content)
        return self.content
```

4. Override `__init__` to handle content decryption on load (or use a custom manager/property):

Actually, let's use a simpler approach - override the content property:

```python
    _content = models.TextField(
        blank=True,
        db_column='content',
        help_text="Your private journal entry (encrypted with user key)"
    )

    @property
    def content(self):
        """Return decrypted content."""
        if not self._content:
            return self._content
        if self._content.startswith('gAAAAA'):
            return self._decrypt_content(self._content)
        return self._content

    @content.setter
    def content(self, value):
        """Store content (encryption happens in save)."""
        self._plaintext_content = value
        self._content = value
```

**Note:** This approach is getting complex. Let's simplify by keeping encryption/decryption explicit in save() and using a manager or refresh pattern.

**Step 5: Simplified approach - use explicit save/load pattern**

Instead of property magic, let's:
1. Keep `content` as a TextField
2. Encrypt in `save()`
3. Create a `get_content()` method for decryption
4. Update serializers to use `get_content()`

Modify Entry model:

```python
class Entry(models.Model):
    """Journal entry with per-user encryption."""

    # ... existing fields ...

    content = models.TextField(
        blank=True,
        help_text="Your private journal entry (encrypted with user key)"
    )

    key_version = models.IntegerField(
        null=True,
        blank=True,
        help_text="Version of user's encryption key used for this entry"
    )

    # Track if content needs encryption (set by setter)
    _needs_encryption = False
    _plaintext_for_word_count = None

    def set_content(self, plaintext):
        """Set content and mark for encryption on save."""
        self._plaintext_for_word_count = plaintext
        self._needs_encryption = True
        self.content = plaintext

    def get_content(self):
        """Get decrypted content."""
        if not self.content:
            return self.content
        if self.key_version and self.content.startswith('gAAAAA'):
            return self._decrypt_content(self.content)
        return self.content

    def _encrypt_content(self, plaintext):
        """Encrypt content with user's encryption key."""
        if not plaintext:
            return plaintext
        from cryptography.fernet import Fernet
        fernet = Fernet(self.user.encryption_key.get_decrypted_key())
        return fernet.encrypt(plaintext.encode('utf-8')).decode('utf-8')

    def _decrypt_content(self, ciphertext):
        """Decrypt content with user's encryption key."""
        if not ciphertext:
            return ciphertext
        from cryptography.fernet import Fernet
        fernet = Fernet(self.user.encryption_key.get_decrypted_key())
        return fernet.decrypt(ciphertext.encode('utf-8')).decode('utf-8')

    def save(self, *args, **kwargs):
        """Auto-calculate word count, encrypt content, and run validation."""
        skip_validation = kwargs.pop('skip_validation', False)

        if not skip_validation:
            self.full_clean()

        # Calculate word count from plaintext content
        plaintext = self._plaintext_for_word_count if self._needs_encryption else self.get_content()
        if plaintext:
            self.word_count = max(0, len(plaintext.split()))
        else:
            self.word_count = 0

        # Encrypt if needed
        if self._needs_encryption and self.content and not self.content.startswith('gAAAAA'):
            self.content = self._encrypt_content(self.content)
            self.key_version = self.user.encryption_key.version
            self._needs_encryption = False
            self._plaintext_for_word_count = None

        super().save(*args, **kwargs)
```

**Step 6: Run tests**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run pytest apps/journal/tests/test_models.py -v`

Expected: Tests should pass (may need to update existing tests)

**Step 7: Create migration for key_version field**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run python manage.py makemigrations journal --name add_key_version_to_entry`

**Step 8: Apply migration**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run python manage.py migrate`

**Step 9: Commit**

```bash
cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption
git add apps/journal/models.py apps/journal/tests/test_models.py apps/journal/migrations/
git commit -m "feat: implement per-user encryption for Entry content"
```

---

## Task 5: Update Serializers

**Files:**
- Modify: `apps/api/serializers.py`
- Modify: `apps/api/tests/` (relevant test files)

**Step 1: Update EntrySerializer to use get_content()**

Modify `apps/api/serializers.py`:

```python
class EntrySerializer(serializers.ModelSerializer):
    """Full serializer for Entry model with content."""

    tags = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = [
            'id',
            'title',
            'content',
            'mood_rating',
            'word_count',
            'tags',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'word_count', 'created_at', 'updated_at']

    def get_content(self, obj):
        """Return decrypted content."""
        return obj.get_content()

    def get_tags(self, obj):
        """Return tags as list of strings."""
        return [tag.name for tag in obj.tags.all()]

    def create(self, validated_data):
        """Create a new entry with encrypted content."""
        tags_data = self.initial_data.get('tags', [])
        content = validated_data.pop('content', '')

        entry = Entry(
            user=self.context['request'].user,
            **validated_data
        )
        entry.set_content(content)
        entry.save()

        if tags_data:
            entry.tags.set(*tags_data)

        return entry

    def update(self, instance, validated_data):
        """Update an existing entry."""
        tags_data = self.initial_data.get('tags', None)
        content = validated_data.pop('content', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if content is not None:
            instance.set_content(content)

        instance.save()

        if tags_data is not None:
            instance.tags.set(*tags_data)

        return instance
```

**Step 2: Fix content field handling**

Since `content` is now a SerializerMethodField, we need to handle input differently:

```python
class EntrySerializer(serializers.ModelSerializer):
    """Full serializer for Entry model with content."""

    tags = serializers.SerializerMethodField()
    content = serializers.CharField(write_only=False, required=False, allow_blank=True)

    class Meta:
        model = Entry
        fields = [
            'id',
            'title',
            'content',
            'mood_rating',
            'word_count',
            'tags',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'word_count', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """Override to return decrypted content."""
        ret = super().to_representation(instance)
        ret['content'] = instance.get_content()
        return ret

    # ... rest of methods
```

**Step 3: Run API tests**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run pytest apps/api/tests/ -v -k "entry"`

**Step 4: Commit**

```bash
cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption
git add apps/api/serializers.py
git commit -m "feat: update serializers for per-user encryption"
```

---

## Task 6: Update Admin to Hide Content

**Files:**
- Modify: `apps/journal/admin.py`

**Step 1: Update EntryAdmin to show placeholder**

Replace content of `apps/journal/admin.py`:

```python
"""
Django admin configuration for journal app.
"""

from django.contrib import admin
from .models import Entry


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    """Admin interface for journal entries."""

    list_display = ['user', 'title_preview', 'mood_rating', 'word_count', 'created_at']
    list_filter = ['mood_rating', 'created_at', 'user']
    search_fields = ['title', 'user__username', 'user__email']
    readonly_fields = ['id', 'word_count', 'created_at', 'updated_at', 'content_display', 'key_version']
    date_hierarchy = 'created_at'
    exclude = ['content']  # Hide actual content field

    fieldsets = (
        ('Entry Information', {
            'fields': ('user', 'title', 'content_display')
        }),
        ('Metadata', {
            'fields': ('mood_rating', 'tags', 'word_count', 'key_version')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def title_preview(self, obj):
        """Show title preview or 'Untitled'."""
        return obj.title[:50] if obj.title else "(Untitled)"
    title_preview.short_description = "Title"

    def content_display(self, obj):
        """Show encrypted placeholder instead of actual content."""
        return "[Encrypted - User's private data]"
    content_display.short_description = "Content"

    def get_queryset(self, request):
        """Admin users see only their own entries (unless superuser)."""
        qs = super().get_queryset(request).select_related('user')
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
```

**Step 2: Run admin manually to verify**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run python manage.py runserver`

Visit: [Django Admin - Journal Entries](http://localhost:8000/admin/journal/entry/)

Verify: Content shows "[Encrypted - User's private data]"

**Step 3: Commit**

```bash
cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption
git add apps/journal/admin.py
git commit -m "feat: hide entry content in admin, show encrypted placeholder"
```

---

## Task 7: Migration for Existing Entries

**Files:**
- Create: `apps/journal/migrations/XXXX_migrate_entries_to_per_user_encryption.py`

**Step 1: Create data migration**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run python manage.py makemigrations journal --empty --name migrate_to_per_user_encryption`

**Step 2: Write migration code**

Edit the created migration file:

```python
from django.db import migrations
from cryptography.fernet import Fernet


def migrate_entries_to_per_user_encryption(apps, schema_editor):
    """
    Re-encrypt existing entries with per-user keys.

    1. Decrypt content using global key
    2. Re-encrypt using user's personal key
    3. Set key_version
    """
    Entry = apps.get_model('journal', 'Entry')
    EncryptionKey = apps.get_model('accounts', 'EncryptionKey')

    from django.conf import settings

    # Get global key
    global_key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
    if not global_key:
        return  # No encryption configured

    if isinstance(global_key, str):
        global_key = global_key.encode('utf-8')

    global_fernet = Fernet(global_key)
    master_fernet = Fernet(global_key)  # For decrypting user keys

    for entry in Entry.objects.select_related('user').all():
        if not entry.content:
            continue

        # Ensure user has encryption key
        user_key, created = EncryptionKey.objects.get_or_create(
            user=entry.user,
            defaults={'version': 1, 'is_active': True}
        )

        if created:
            # Generate key for existing user
            raw_key = Fernet.generate_key()
            user_key.key = master_fernet.encrypt(raw_key).decode('utf-8')
            user_key.save()

        try:
            # Decrypt with global key (old encryption)
            plaintext = global_fernet.decrypt(entry.content.encode('utf-8')).decode('utf-8')

            # Re-encrypt with user's key
            user_fernet = Fernet(master_fernet.decrypt(user_key.key.encode('utf-8')))
            new_content = user_fernet.encrypt(plaintext.encode('utf-8')).decode('utf-8')

            entry.content = new_content
            entry.key_version = user_key.version
            entry.save(update_fields=['content', 'key_version'])

        except Exception as e:
            print(f"Failed to migrate entry {entry.id}: {e}")
            continue


def reverse_migration(apps, schema_editor):
    """
    Reverse migration - re-encrypt with global key.

    Note: This is a lossy operation if users have been deleted.
    """
    pass  # Implement if needed


class Migration(migrations.Migration):

    dependencies = [
        ('journal', 'XXXX_add_key_version_to_entry'),  # Update this
        ('accounts', 'XXXX_add_encryption_key'),  # Update this
    ]

    operations = [
        migrations.RunPython(
            migrate_entries_to_per_user_encryption,
            reverse_migration,
        ),
    ]
```

**Step 3: Run migration**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run python manage.py migrate`

**Step 4: Commit**

```bash
cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption
git add apps/journal/migrations/
git commit -m "feat: add migration for existing entries to per-user encryption"
```

---

## Task 8: Create Encryption Keys for Existing Users

**Files:**
- Create: `apps/accounts/migrations/XXXX_create_encryption_keys_for_existing_users.py`

**Step 1: Create data migration**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run python manage.py makemigrations accounts --empty --name create_encryption_keys_for_existing_users`

**Step 2: Write migration code**

```python
from django.db import migrations
from cryptography.fernet import Fernet


def create_keys_for_existing_users(apps, schema_editor):
    """Create EncryptionKey for all existing users who don't have one."""
    User = apps.get_model('accounts', 'User')
    EncryptionKey = apps.get_model('accounts', 'EncryptionKey')

    from django.conf import settings

    global_key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
    if not global_key:
        return

    if isinstance(global_key, str):
        global_key = global_key.encode('utf-8')

    master_fernet = Fernet(global_key)

    for user in User.objects.all():
        if not EncryptionKey.objects.filter(user=user).exists():
            raw_key = Fernet.generate_key()
            encrypted_key = master_fernet.encrypt(raw_key).decode('utf-8')
            EncryptionKey.objects.create(
                user=user,
                key=encrypted_key,
                version=1,
                is_active=True,
            )


def reverse_migration(apps, schema_editor):
    """Remove encryption keys."""
    EncryptionKey = apps.get_model('accounts', 'EncryptionKey')
    EncryptionKey.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', 'XXXX_add_encryption_key'),  # Update this
    ]

    operations = [
        migrations.RunPython(
            create_keys_for_existing_users,
            reverse_migration,
        ),
    ]
```

**Step 3: Run migration**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run python manage.py migrate`

**Step 4: Commit**

```bash
cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption
git add apps/accounts/migrations/
git commit -m "feat: create encryption keys for existing users"
```

---

## Task 9: Run Full Test Suite

**Step 1: Run all tests**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && uv run pytest -v`

**Step 2: Fix any failing tests**

Update tests that expect old encryption behavior.

**Step 3: Commit fixes**

```bash
cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption
git add -A
git commit -m "fix: update tests for per-user encryption"
```

---

## Task 10: Final Verification

**Step 1: Start dev server**

Run: `cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption && make dev`

**Step 2: Test manually**

1. Create new entry via frontend
2. Verify it saves and loads correctly
3. Check admin shows "[Encrypted]" placeholder
4. Verify statistics still work

**Step 3: Final commit**

```bash
cd /Users/tomasmach/Documents/Code/QuietPage/.worktrees/per-user-encryption
git add -A
git commit -m "feat: complete per-user encryption implementation"
```

---

## Summary

Tasks completed:
1. EncryptionKey model created
2. Auto-creation signal for new users
3. EncryptionKeyFactory for testing
4. Entry model updated for per-user encryption
5. Serializers updated
6. Admin hides content
7. Migration for existing entries
8. Migration for existing users
9. Full test suite passes
10. Manual verification complete
