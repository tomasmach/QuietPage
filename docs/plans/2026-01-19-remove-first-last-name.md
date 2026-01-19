# Remove First and Last Name Fields Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove first_name and last_name fields from the entire application, keeping only username for user identification.

**Architecture:** Since the User model extends Django's AbstractUser (which includes first_name and last_name as inherited fields), we cannot remove them from the database schema without major refactoring. Instead, we'll stop exposing and using these fields throughout the application by removing them from serializers, forms, admin, frontend UI, email templates, and all tests.

**Tech Stack:** Django REST Framework, React, TypeScript, pytest

---

## Task 1: Remove from Backend API Serializers

**Files:**
- Modify: `apps/api/serializers.py:27-28`
- Modify: `apps/api/settings_serializers.py:27,41-42`
- Modify: `apps/api/settings_views.py:46,49`

**Step 1: Update UserSerializer**

Remove first_name and last_name from the UserSerializer fields list.

```python
# In apps/api/serializers.py, modify the Meta.fields list (around line 23-42)
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.

    Includes profile information, writing goals, streak data, and preferences.
    """
    avatar = serializers.SerializerMethodField()
    timezone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            # REMOVE: 'first_name',
            # REMOVE: 'last_name',
            'avatar',
            'bio',
            'timezone',
            'daily_word_goal',
            'current_streak',
            'longest_streak',
            'email_notifications',
            'preferred_writing_time',
            'reminder_enabled',
            'reminder_time',
            'preferred_language',
            'preferred_theme',
            'onboarding_completed',
        ]
        read_only_fields = ['id', 'current_streak', 'longest_streak']
```

**Step 2: Update ProfileSettingsSerializer**

Remove first_name and last_name from ProfileSettingsSerializer.

```python
# In apps/api/settings_serializers.py, modify around lines 23-48
class ProfileSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for profile settings (GET/PATCH).

    Handles: bio, avatar
    """
    avatar = serializers.SerializerMethodField(read_only=True)
    avatar_upload = serializers.ImageField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="Avatar image file (will be resized to 512x512)"
    )

    class Meta:
        model = User
        fields = [
            # REMOVE: 'first_name',
            # REMOVE: 'last_name',
            'bio',
            'avatar',
            'avatar_upload',
            'preferred_language',
            'preferred_theme',
        ]
```

**Step 3: Update settings_views.py docstrings**

```python
# In apps/api/settings_views.py, update the ProfileSettingsView docstring (around line 46-49)
    """
    Profile settings endpoint.
    - GET: Returns profile settings (bio, avatar, preferred_language, preferred_theme)
    - Returns: bio, avatar (URL), preferred_language, preferred_theme

    - PATCH: Updates profile settings
    - Updates: bio, avatar_upload (file), preferred_language, preferred_theme
    - Returns: Updated profile settings
    """
```

**Step 4: Run backend tests to verify serializer changes**

Run: `uv run pytest apps/api/tests/test_settings_views.py -v -k profile`

Expected: Some tests will FAIL because they still reference first_name/last_name. We'll fix these in Task 3.

**Step 5: Commit**

```bash
git add apps/api/serializers.py apps/api/settings_serializers.py apps/api/settings_views.py
git commit -m "refactor: remove first_name and last_name from API serializers"
```

---

## Task 2: Remove from Backend Forms and Admin

**Files:**
- Modify: `apps/accounts/forms.py:27,29-33,49-50,55-56`
- Modify: `apps/accounts/admin.py:25-26,43-44`

**Step 1: Update UserProfileForm**

Remove first_name and last_name from the form.

```python
# In apps/accounts/forms.py, modify UserProfileForm (around lines 18-62)
class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""

    class Meta:
        model = User
        fields = ['bio', 'avatar']
        widgets = {
            # REMOVE first_name and last_name widgets
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Napište něco o sobě...'
            }),
        }
        labels = {
            # REMOVE first_name and last_name labels
            'bio': 'O mně',
        }
        help_texts = {
            # REMOVE first_name and last_name help_texts
            'bio': 'Volitelné',
        }
```

**Step 2: Update UserAdmin**

Remove first_name and last_name from admin display.

```python
# In apps/accounts/admin.py, modify UserAdmin (around lines 14-45)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model."""

    list_display = [
        'username',
        'email',
        # REMOVE: 'first_name',
        # REMOVE: 'last_name',
        'current_streak',
        'longest_streak',
        'is_staff',
        'date_joined'
    ]

    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']

    search_fields = [
        'username',
        'email',
        # REMOVE: 'first_name',
        # REMOVE: 'last_name'
    ]
```

**Step 3: Run backend tests**

Run: `uv run pytest apps/accounts/tests/test_forms.py -v`

Expected: Tests will FAIL. We'll fix them in Task 3.

**Step 4: Commit**

```bash
git add apps/accounts/forms.py apps/accounts/admin.py
git commit -m "refactor: remove first_name and last_name from forms and admin"
```

---

## Task 3: Fix Backend Tests

**Files:**
- Modify: `apps/api/tests/test_settings_views.py`
- Modify: `apps/accounts/tests/test_forms.py`
- Modify: `apps/accounts/tests/test_signals.py`
- Modify: `apps/accounts/tests/factories.py`
- Modify: `apps/accounts/tests/test_tasks.py`
- Modify: `apps/journal/tests/test_tasks.py`

**Step 1: Update test_settings_views.py**

Remove all first_name/last_name references from profile settings tests.

```python
# In apps/api/tests/test_settings_views.py

# Around line 163, modify test_get_profile_settings:
def test_get_profile_settings(self, authenticated_api_client):
    """Test GET /api/v1/settings/profile/"""
    user = UserFactory(bio='Test bio')  # REMOVE: first_name='Jan', last_name='Novak'
    client = authenticated_api_client(user)

    response = client.get(reverse('api:profile-settings'))
    assert response.status_code == 200

    data = response.json()
    # REMOVE: assert data['first_name'] == 'Jan'
    # REMOVE: assert data['last_name'] == 'Novak'
    assert data['bio'] == 'Test bio'

# Around line 176, modify test_update_profile_settings:
def test_update_profile_settings(self, authenticated_api_client):
    """Test PATCH /api/v1/settings/profile/"""
    user = UserFactory()  # REMOVE: first_name='Old', last_name='Name'
    client = authenticated_api_client(user)

    response = client.patch(
        reverse('api:profile-settings'),
        data=json.dumps({'bio': 'New bio'}),  # REMOVE: 'first_name': 'New', 'last_name': 'Name'
        content_type='application/json'
    )
    assert response.status_code == 200

    user.refresh_from_db()
    # REMOVE: assert user.first_name == 'New'
    # REMOVE: assert user.last_name == 'Name'
    assert user.bio == 'New bio'

# Around line 192, modify test_update_profile_with_avatar:
def test_update_profile_with_avatar(self, authenticated_api_client):
    """Test PATCH /api/v1/settings/profile/ with avatar upload"""
    user = UserFactory()  # REMOVE: first_name='Jan', last_name='Novak'
    client = authenticated_api_client(user)

    # Create a test image
    avatar = create_test_image()

    response = client.patch(
        reverse('api:profile-settings'),
        data={'avatar_upload': avatar},  # REMOVE other fields
        format='multipart'
    )
    assert response.status_code == 200

    user.refresh_from_db()
    # REMOVE: assert user.first_name == 'Jan'
    # REMOVE: assert user.last_name == 'Novak'
    assert user.avatar

# Around line 214, modify test_partial_update_profile:
def test_partial_update_profile(self, authenticated_api_client):
    """Test PATCH /api/v1/settings/profile/ with partial data"""
    user = UserFactory(bio='Old bio')
    client = authenticated_api_client(user)

    response = client.patch(
        reverse('api:profile-settings'),
        data=json.dumps({'bio': 'New bio'}),  # REMOVE: 'first_name': 'Test'
        content_type='application/json'
    )
    assert response.status_code == 200
    assert user.bio != 'Old bio'
```

**Step 2: Update test_forms.py**

Remove all first_name/last_name form tests.

```python
# In apps/accounts/tests/test_forms.py

# Around line 44-45, remove these assertions from test_user_profile_form_fields:
def test_user_profile_form_fields(self):
    """Test that UserProfileForm has correct fields"""
    form = UserProfileForm()
    # REMOVE: assert 'first_name' in form.fields
    # REMOVE: assert 'last_name' in form.fields
    assert 'bio' in form.fields
    assert 'avatar' in form.fields

# Around line 56-57, remove these assertions from test_user_profile_form_labels:
def test_user_profile_form_labels(self):
    """Test that UserProfileForm has correct Czech labels"""
    form = UserProfileForm()
    # REMOVE: assert form.fields['first_name'].label == 'Jméno'
    # REMOVE: assert form.fields['last_name'].label == 'Příjmení'
    assert form.fields['bio'].label == 'O mně'

# Around line 89-90, modify test_user_profile_form_valid_data:
def test_user_profile_form_valid_data(self):
    """Test that UserProfileForm accepts valid data"""
    form = UserProfileForm(
        data={
            # REMOVE: 'first_name': 'Jan',
            # REMOVE: 'last_name': 'Novák',
            'bio': 'Test bio',
        }
    )
    assert form.is_valid()

# Around line 107, 123, 149, 188, 205-206, remove first_name/last_name from all test data
```

**Step 3: Update test_signals.py**

```python
# In apps/accounts/tests/test_signals.py, around line 72
# Remove or modify the test that updates first_name:
# Change it to update a different field like bio instead
user.bio = 'Updated bio'  # REPLACE: user.first_name = 'Updated'
```

**Step 4: Update factories.py**

```python
# In apps/accounts/tests/factories.py, around lines 40-41
# Comment out or remove first_name and last_name from UserFactory:
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')

    # REMOVE these lines:
    # first_name = factory.Faker('first_name', locale='cs_CZ')
    # last_name = factory.Faker('last_name', locale='cs_CZ')
```

**Step 5: Update test_tasks.py (accounts)**

```python
# In apps/accounts/tests/test_tasks.py

# Around line 124, remove first_name parameter:
user = UserFactory(username="testuser")  # REMOVE: first_name=""

# Around line 135-136, update assertion comment:
# Template uses username only
assert "testuser" in mail.outbox[0].body

# Around line 174, remove first_name parameter:
user = UserFactory(username="johndoe")  # REMOVE: first_name="John"

# Around line 181, update comment:
# Template uses username only

# Repeat for lines 360, 461, 503, 645 - remove all first_name parameters
```

**Step 6: Update test_tasks.py (journal)**

```python
# In apps/journal/tests/test_tasks.py, around lines 255-256
# Remove first_name and last_name from user factory call:
user = UserFactory(
    username='testuser',
    # REMOVE: first_name="John",
    # REMOVE: last_name="Doe",
    reminder_enabled=True,
    reminder_time=time(9, 0)
)
```

**Step 7: Run all backend tests**

Run: `uv run pytest apps/api/tests/ apps/accounts/tests/ apps/journal/tests/ -v`

Expected: All tests should PASS now.

**Step 8: Commit**

```bash
git add apps/api/tests/ apps/accounts/tests/ apps/journal/tests/
git commit -m "test: update tests to remove first_name and last_name"
```

---

## Task 4: Update Email Templates

**Files:**
- Modify: `templates/accounts/emails/welcome.txt`
- Modify: `templates/accounts/emails/reminder.txt`
- Modify: `templates/accounts/emails/password_changed.txt`
- Modify: `templates/accounts/emails/email_changed_notification.txt`
- Modify: `templates/accounts/emails/email_verification.txt`
- Modify: `templates/accounts/emails/password_reset_request.txt`

**Step 1: Update all email templates**

Replace all occurrences of `{{ user.first_name|default:user.username }}` with `{{ user.username }}`.

```txt
# templates/accounts/emails/welcome.txt
Vitejte v QuietPage!

Hello {{ user.username }},

Vitame vas v QuietPage...


# templates/accounts/emails/reminder.txt
Cas na psani

Time to write, {{ user.username }}!

Nezapomente...


# templates/accounts/emails/password_changed.txt
Heslo zmeneno

Hello {{ user.username }},

Vase heslo bylo uspesne zmeneno...


# templates/accounts/emails/email_changed_notification.txt
Email zmenen

Hello {{ user.username }},

Vas email byl uspesne zmenen...


# templates/accounts/emails/email_verification.txt
Overeni emailu

Hello {{ user.username }},

Prosim overte vas email...


# templates/accounts/emails/password_reset_request.txt
Obnova hesla

Hello {{ user.username }},

Zadali jste o obnovu hesla...
```

**Step 2: Update tasks.py to remove first_name/last_name from context**

```python
# In apps/journal/tasks.py, around lines 145-146
# Remove first_name and last_name from email context:
context = {
    'user': user,
    'username': user.username,
    # REMOVE: 'first_name': user.first_name,
    # REMOVE: 'last_name': user.last_name,
}
```

**Step 3: Test email sending**

Run: `uv run pytest apps/accounts/tests/test_tasks.py apps/journal/tests/test_tasks.py -v -k email`

Expected: All email tests should PASS.

**Step 4: Commit**

```bash
git add templates/accounts/emails/ apps/journal/tasks.py
git commit -m "refactor: update email templates to use only username"
```

---

## Task 5: Remove from Frontend Types and Contexts

**Files:**
- Modify: `frontend/src/contexts/AuthContext.tsx:13-14`
- Modify: `frontend/src/hooks/useSettings.ts:8-9,113`

**Step 1: Update AuthContext User type**

```typescript
// In frontend/src/contexts/AuthContext.tsx, around lines 8-30
export interface User {
  id: number;
  username: string;
  email: string;
  // REMOVE: first_name?: string;
  // REMOVE: last_name?: string;
  avatar?: string | null;
  bio?: string;
  timezone?: string;
  daily_word_goal?: number;
  current_streak?: number;
  longest_streak?: number;
  email_notifications?: boolean;
  preferred_writing_time?: string;
  reminder_enabled?: boolean;
  reminder_time?: string;
  preferred_language?: string;
  preferred_theme?: string;
  onboarding_completed?: boolean;
}
```

**Step 2: Update useSettings hook types**

```typescript
// In frontend/src/hooks/useSettings.ts, around lines 5-15
export interface ProfileUpdateData {
  // REMOVE: first_name: string;
  // REMOVE: last_name: string;
  bio: string;
}

// Around line 113, update comment:
/**
 * Update profile settings (bio)
 */
```

**Step 3: Run TypeScript check**

Run: `cd frontend && npm run type-check`

Expected: Should have some errors from ProfileSettingsPage.tsx. We'll fix those in the next task.

**Step 4: Commit**

```bash
git add frontend/src/contexts/AuthContext.tsx frontend/src/hooks/useSettings.ts
git commit -m "refactor: remove first_name and last_name from frontend types"
```

---

## Task 6: Remove from Frontend UI

**Files:**
- Modify: `frontend/src/pages/settings/ProfileSettingsPage.tsx:23-24,33-34,121-135`

**Step 1: Update ProfileSettingsPage component**

Remove first_name and last_name fields from the form.

```typescript
// In frontend/src/pages/settings/ProfileSettingsPage.tsx

// Around lines 22-26, remove first_name and last_name from formData:
const [formData, setFormData] = useState({
  // REMOVE: first_name: user?.first_name || '',
  // REMOVE: last_name: user?.last_name || '',
  bio: user?.bio || '',
});

// Around lines 29-42, remove first_name and last_name from handleSubmit:
const handleSubmit = async (e: FormEvent) => {
  e.preventDefault();
  clearMessages();
  const result = await updateProfile({
    // REMOVE: first_name: formData.first_name,
    // REMOVE: last_name: formData.last_name,
    bio: formData.bio,
  });
  if (result) {
    toast.success(t('toast.profileUpdated'));
  } else {
    toast.error(t('toast.saveError'));
  }
};

// Around lines 120-135, remove the Name Fields section entirely:
{/* REMOVE this entire section:
  <div className="grid grid-cols-2 gap-4">
    <Input
      label={t('settings.profile.firstName')}
      value={formData.first_name}
      onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
      disabled={isLoading}
    />
    <Input
      label={t('settings.profile.lastName')}
      value={formData.last_name}
      onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
      disabled={isLoading}
    />
  </div>
*/}

{/* Bio */}
<Textarea
  label={t('settings.profile.bio')}
  value={formData.bio}
  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
  rows={4}
  disabled={isLoading}
  helperText={t('settings.profile.bioHint')}
/>
```

**Step 2: Run frontend type check**

Run: `cd frontend && npm run type-check`

Expected: No TypeScript errors.

**Step 3: Run frontend tests**

Run: `cd frontend && npm run test:run`

Expected: All tests should pass.

**Step 4: Start dev server and manually test**

Run: `cd frontend && npm run dev`

- Navigate to http://localhost:5173/settings
- Verify that first_name and last_name fields are NOT displayed
- Verify that bio field works correctly
- Verify avatar upload works correctly

**Step 5: Commit**

```bash
git add frontend/src/pages/settings/ProfileSettingsPage.tsx
git commit -m "refactor: remove first_name and last_name from profile settings UI"
```

---

## Task 7: Update Documentation

**Files:**
- Modify: `apps/api/AUTH_API_DOCUMENTATION.md`
- Modify: `docs/plans/2026-01-19-resend-email-backend.md` (optional)

**Step 1: Update AUTH_API_DOCUMENTATION.md**

Remove first_name and last_name from all API response examples.

```markdown
# In apps/api/AUTH_API_DOCUMENTATION.md

# Around line 64-65, remove from /me response example:
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  // REMOVE: "first_name": "",
  // REMOVE: "last_name": "",
  "avatar": null,
  "bio": "",
  ...
}

# Around line 154-155, remove from /register response example
# Around line 224-225, remove from /settings/profile/ example
```

**Step 2: Optionally update resend-email-backend plan**

This is optional since it's a historical plan document. If you want to update it for consistency, remove first_name references from the email templates in that document.

**Step 3: Commit**

```bash
git add apps/api/AUTH_API_DOCUMENTATION.md
git commit -m "docs: remove first_name and last_name from API documentation"
```

---

## Task 8: Final Integration Test

**Step 1: Run full backend test suite**

Run: `uv run pytest -v`

Expected: All tests PASS.

**Step 2: Run full frontend test suite**

Run: `cd frontend && npm run test:run`

Expected: All tests PASS.

**Step 3: Run full integration test**

1. Start backend: `make run`
2. Start frontend: `cd frontend && npm run dev`
3. Test complete user flow:
   - Sign up with username, email, password
   - Log in
   - Navigate to Settings → Profile
   - Verify NO first_name/last_name fields displayed
   - Update bio
   - Upload avatar
   - Verify changes are saved
4. Check that emails still work (if you have email configured)

**Step 4: Final commit**

```bash
git add -A
git commit -m "chore: final cleanup for first_name/last_name removal"
```

---

## Summary

This plan removes first_name and last_name from:
- ✅ Backend API serializers
- ✅ Backend forms and admin interface
- ✅ All backend tests
- ✅ All email templates
- ✅ Frontend TypeScript types
- ✅ Frontend UI components
- ✅ API documentation

The fields remain in the database schema (inherited from Django's AbstractUser), but they are no longer exposed or used anywhere in the application. Users will only interact with their username for identification.
