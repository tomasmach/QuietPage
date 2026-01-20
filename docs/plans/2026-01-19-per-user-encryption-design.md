# Per-User Encryption Design

## Overview

Implement per-user encryption keys so that journal entries are encrypted with each user's unique key rather than a global application key. Additionally, hide entry content from Django admin to protect user privacy.

## Goals

1. **Per-user isolation** - Each user's entries encrypted with their own Fernet key
2. **Admin privacy** - Content hidden in Django admin (shows "[Encrypted]" placeholder)
3. **Zero user impact** - No changes to user experience, login, or workflows
4. **Statistics compatibility** - All existing statistics continue working

## Data Model

### New Model: EncryptionKey

Location: `apps/accounts/models.py`

```python
class EncryptionKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='encryption_key')
    key = models.CharField(max_length=500)  # Encrypted with global master key
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rotated_at = models.DateTimeField(null=True, blank=True)
```

The user's Fernet key is itself encrypted with the global `FIELD_ENCRYPTION_KEY` before storage - defense in depth.

### Entry Model Changes

Location: `apps/journal/models.py`

```python
class Entry(models.Model):
    # ... existing fields ...
    key_version = models.IntegerField(null=True, blank=True)  # Track which key version encrypted this entry
```

## Encryption Flow

### Writing an Entry

1. User saves entry via API
2. `Entry.save()` calculates `word_count` from plaintext content
3. System fetches user's active `EncryptionKey`
4. Content encrypted with user's Fernet key
5. `key_version` stored on entry
6. Encrypted content saved to DB

### Reading an Entry

1. Entry fetched from DB (content still encrypted as raw text)
2. System looks up user's `EncryptionKey` (version matching `entry.key_version` if key rotation exists)
3. Decrypts content with that key
4. Returns plaintext to authorized user

### Key Generation

- New users: Key generated automatically on user creation (signal)
- Existing users: Migration creates keys for all existing users

## Implementation Approach

Replace `EncryptedTextField` on Entry with explicit encryption in the model:

```python
class Entry(models.Model):
    content = models.TextField(blank=True)  # Plain TextField, encryption handled manually
    key_version = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate word count from plaintext
        if self.content:
            self.word_count = len(self.content.split())

        # Encrypt content with user's key before save
        if self.content and not self._is_encrypted():
            self._encrypt_content()

        super().save(*args, **kwargs)

    def _encrypt_content(self):
        key = self.user.encryption_key
        fernet = Fernet(key.get_decrypted_key())
        self.content = fernet.encrypt(self.content.encode()).decode()
        self.key_version = key.version

    @property
    def decrypted_content(self):
        if not self.content:
            return self.content
        key = self.user.encryption_key
        fernet = Fernet(key.get_decrypted_key())
        return fernet.decrypt(self.content.encode()).decode()
```

## Admin Changes

Location: `apps/journal/admin.py`

```python
@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'title_preview', 'mood_rating', 'word_count', 'created_at']
    readonly_fields = ['id', 'word_count', 'created_at', 'updated_at', 'content_display']

    fieldsets = (
        ('Entry Information', {
            'fields': ('user', 'title', 'content_display')
        }),
        ('Metadata', {
            'fields': ('mood_rating', 'tags', 'word_count')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def content_display(self, obj):
        return "[Encrypted - User's private data]"
    content_display.short_description = "Content"

    # Exclude actual content field from form
    exclude = ['content', 'key_version']
```

## Migration Strategy

### Step 1: Add EncryptionKey model
- Create model and migration
- Generate keys for all existing users

### Step 2: Add key_version to Entry
- Add nullable field to Entry model

### Step 3: Re-encrypt existing entries
- One-time data migration
- For each entry: decrypt with global key, re-encrypt with user's key
- Update key_version

### Step 4: Update Entry model
- Replace EncryptedTextField with TextField
- Add encryption/decryption methods
- Update serializers to use decrypted_content

### Step 5: Update admin
- Hide content, show placeholder

## Statistics Compatibility

Statistics remain fully functional because they use:
- `word_count` - Calculated before encryption, stored as plain integer
- `mood_rating` - Plain integer field
- `tags` - Separate django-taggit relation
- `created_at` / timestamps - Plain datetime fields
- `title` - Used in personal records, decrypts with user's key (API already filters by user)

No changes needed to statistics views.

## Security Considerations

1. **Key storage** - User keys encrypted with global master key before DB storage
2. **Key access** - Only decrypted when needed for encrypt/decrypt operations
3. **Admin access** - Content completely hidden in admin UI
4. **API isolation** - API already filters entries by authenticated user
5. **Future key rotation** - `key_version` field enables future key rotation support

## Files to Modify

1. `apps/accounts/models.py` - Add EncryptionKey model
2. `apps/accounts/signals.py` - Auto-create key on user creation
3. `apps/accounts/admin.py` - Register EncryptionKey (optional, for debugging)
4. `apps/journal/models.py` - Update Entry with per-user encryption
5. `apps/journal/admin.py` - Hide content, show placeholder
6. `apps/api/serializers.py` - Use decrypted_content property
7. Migrations for both apps

## Testing

- Unit tests for EncryptionKey model
- Unit tests for Entry encryption/decryption
- Integration test: create entry, verify encrypted in DB, verify decrypts correctly
- Test statistics still work after changes
- Test admin shows placeholder
