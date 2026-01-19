"""
Comprehensive tests for accounts app forms.

This module tests all forms in apps/accounts/forms.py, covering:
- Form field customization and attributes
- Validation logic and error messages
- Password verification and authentication
- File upload validation
- Edge cases and security concerns
"""

import pytest
from unittest.mock import Mock, patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import authenticate

from apps.accounts.forms import (
    ProfileUpdateForm,
    GoalsUpdateForm,
    PrivacySettingsForm,
    EmailChangeForm,
    AccountDeleteForm,
)
from apps.accounts.tests.factories import UserFactory


# ============================================
# PROFILE UPDATE FORM TESTS
# ============================================


@pytest.mark.unit
@pytest.mark.forms
class TestProfileUpdateForm:
    """Test suite for ProfileUpdateForm."""

    def test_profile_form_fields(self):
        """
        Test that profile form includes correct fields.

        Why: Users should be able to update their bio and avatar.
        """
        form = ProfileUpdateForm()
        assert 'bio' in form.fields
        assert 'avatar' in form.fields

    def test_profile_form_field_labels(self):
        """
        Test that profile form has Czech labels.

        Why: Ensures proper localization for Czech users.
        """
        form = ProfileUpdateForm()
        assert form.fields['bio'].label == 'O mně'
        assert form.fields['avatar'].label == 'Profilový obrázek'

    def test_profile_form_bio_max_length(self):
        """
        Test that bio textarea has maxlength attribute.
        
        Why: Prevents users from exceeding the 500 character limit
        with client-side validation.
        """
        form = ProfileUpdateForm()
        assert form.fields['bio'].widget.attrs['maxlength'] == '500'

    def test_profile_form_avatar_accept_attribute(self):
        """
        Test that avatar field only accepts image files.
        
        Why: Improves UX by filtering file picker to images only.
        """
        form = ProfileUpdateForm()
        assert form.fields['avatar'].widget.attrs['accept'] == 'image/*'

    def test_profile_form_valid_data(self, sample_avatar):
        """
        Test that form validates with correct data including avatar.

        Why: Ensures valid profile updates are accepted.
        """
        user = UserFactory()
        form = ProfileUpdateForm(
            data={
                'bio': 'Miluji psaní.',
            },
            files={'avatar': sample_avatar},
            instance=user
        )

        assert form.is_valid(), form.errors

    def test_profile_form_avatar_size_validation_pass(self, sample_avatar):
        """
        Test that small avatars pass validation.

        Why: Valid images under 2MB should be accepted.
        """
        user = UserFactory()
        form = ProfileUpdateForm(
            data={'bio': 'Test bio'},
            files={'avatar': sample_avatar},
            instance=user
        )

        assert form.is_valid()

    def test_profile_form_avatar_size_validation_fail(self, large_avatar):
        """
        Test that avatars over 2MB are rejected.

        Why: Prevents excessive storage usage and ensures reasonable
        file sizes for web display.
        """
        user = UserFactory()
        form = ProfileUpdateForm(
            data={'bio': 'Test bio'},
            files={'avatar': large_avatar},
            instance=user
        )

        assert not form.is_valid()
        assert 'avatar' in form.errors
        assert 'příliš velký' in str(form.errors['avatar']).lower()

    def test_profile_form_avatar_type_validation(self):
        """
        Test that only valid image types are accepted.
        
        Why: Ensures security by rejecting non-image files and only
        allowing safe image formats (JPEG, PNG, WebP).
        """
        user = UserFactory()
        
        # Invalid file type (text file)
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"not an image",
            content_type="text/plain"
        )
        
        form = ProfileUpdateForm(
            data={'bio': 'Test bio'},
            files={'avatar': invalid_file},
            instance=user
        )
        
        assert not form.is_valid()
        assert 'avatar' in form.errors
        # Django's ImageField validates the file is a valid image first
        assert 'platný obrázek' in str(form.errors['avatar']).lower()

    def test_profile_form_avatar_valid_types(self):
        """
        Test that all valid image types are accepted.
        
        Why: Ensures JPEG, PNG, and WebP formats are all allowed.
        """
        user = UserFactory()
        valid_types = [
            ('image/jpeg', 'test.jpg'),
            ('image/png', 'test.png'),
            ('image/jpg', 'test.jpeg'),
            ('image/webp', 'test.webp'),
        ]
        
        for content_type, filename in valid_types:
            # Use minimal valid JPEG data for all (validation only checks content_type)
            jpeg_data = (
                b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
                b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c'
                b'\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c'
                b'\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00'
                b'\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00'
                b'\x08\x01\x01\x00\x00?\x00\x7f\x00\xff\xd9'
            )
            
            image_file = SimpleUploadedFile(filename, jpeg_data, content_type=content_type)
            form = ProfileUpdateForm(
                data={'bio': 'Test bio'},
                files={'avatar': image_file},
                instance=user
            )
            
            assert form.is_valid(), f"Failed for {content_type}: {form.errors}"

    def test_profile_form_no_avatar_is_valid(self):
        """
        Test that form is valid without avatar upload.

        Why: Avatar should be optional - users can update profile
        without changing their avatar.
        """
        user = UserFactory()
        form = ProfileUpdateForm(
            data={
                'bio': 'Updated bio',
            },
            instance=user
        )

        assert form.is_valid()


# ============================================
# GOALS UPDATE FORM TESTS
# ============================================


@pytest.mark.unit
@pytest.mark.forms
class TestGoalsUpdateForm:
    """Test suite for GoalsUpdateForm."""

    def test_goals_form_fields(self):
        """
        Test that goals form includes all writing preference fields.
        
        Why: Users should be able to configure all aspects of their
        writing goals and reminders.
        """
        form = GoalsUpdateForm()
        assert 'daily_word_goal' in form.fields
        assert 'preferred_writing_time' in form.fields
        assert 'reminder_enabled' in form.fields
        assert 'reminder_time' in form.fields
        assert 'timezone' in form.fields

    def test_goals_form_word_goal_widget_attributes(self):
        """
        Test that word goal input has correct min/max/step attributes.
        
        Why: Provides client-side validation and better UX with
        number input controls.
        """
        form = GoalsUpdateForm()
        widget_attrs = form.fields['daily_word_goal'].widget.attrs
        
        assert widget_attrs['min'] == 100
        assert widget_attrs['max'] == 5000
        assert widget_attrs['step'] == 50

    def test_goals_form_valid_word_goal(self):
        """
        Test that valid word goals are accepted.
        
        Why: Ensures goals within 100-5000 range pass validation.
        """
        user = UserFactory()
        
        valid_goals = [100, 750, 2000, 5000]
        for goal in valid_goals:
            form = GoalsUpdateForm(
                data={
                    'daily_word_goal': goal,
                    'preferred_writing_time': 'morning',
                    'reminder_enabled': False,
                    'reminder_time': '08:00',
                    'timezone': 'Europe/Prague',
                },
                instance=user
            )
            assert form.is_valid(), f"Goal {goal} should be valid: {form.errors}"

    def test_goals_form_invalid_word_goal_too_low(self):
        """
        Test that word goals below 100 are rejected.
        
        Why: Minimum goal of 100 words ensures meaningful daily writing
        practice.
        """
        user = UserFactory()
        form = GoalsUpdateForm(
            data={
                'daily_word_goal': 50,
                'preferred_writing_time': 'morning',
                'reminder_enabled': False,
                'reminder_time': '08:00',
                'timezone': 'Europe/Prague',
            },
            instance=user
        )
        
        assert not form.is_valid()
        assert 'daily_word_goal' in form.errors

    def test_goals_form_invalid_word_goal_too_high(self):
        """
        Test that word goals above 5000 are rejected.
        
        Why: Maximum goal of 5000 words prevents unrealistic targets
        that could discourage users.
        """
        user = UserFactory()
        form = GoalsUpdateForm(
            data={
                'daily_word_goal': 10000,
                'preferred_writing_time': 'morning',
                'reminder_enabled': False,
                'reminder_time': '08:00',
                'timezone': 'Europe/Prague',
            },
            instance=user
        )
        
        assert not form.is_valid()
        assert 'daily_word_goal' in form.errors

    def test_goals_form_reminder_time_format(self):
        """
        Test that reminder_time field uses HTML5 time input.
        
        Why: Provides better UX with native time picker on supported browsers.
        """
        form = GoalsUpdateForm()
        # Check either the widget's input_type or the attrs['type']
        assert (form.fields['reminder_time'].widget.input_type == 'time' or 
                form.fields['reminder_time'].widget.attrs.get('type') == 'time')


# ============================================
# PRIVACY SETTINGS FORM TESTS
# ============================================


@pytest.mark.unit
@pytest.mark.forms
class TestPrivacySettingsForm:
    """Test suite for PrivacySettingsForm."""

    def test_privacy_form_has_email_notifications_field(self):
        """
        Test that privacy form includes email notifications setting.
        
        Why: Users should be able to control email notification preferences.
        """
        form = PrivacySettingsForm()
        assert 'email_notifications' in form.fields

    def test_privacy_form_field_is_checkbox(self):
        """
        Test that email_notifications uses checkbox widget.
        
        Why: Boolean fields should use checkboxes for better UX.
        """
        form = PrivacySettingsForm()
        from django import forms
        assert isinstance(
            form.fields['email_notifications'].widget,
            forms.CheckboxInput
        )


# ============================================
# EMAIL CHANGE FORM TESTS
# ============================================


@pytest.mark.unit
@pytest.mark.forms
class TestEmailChangeForm:
    """Test suite for EmailChangeForm."""

    def test_email_change_form_fields(self):
        """
        Test that email change form has required fields.
        
        Why: Email changes require new email and password confirmation
        for security.
        """
        user = UserFactory()
        form = EmailChangeForm(user=user)
        
        assert 'new_email' in form.fields
        assert 'password' in form.fields

    def test_email_change_form_requires_user(self):
        """
        Test that form requires user instance for initialization.
        
        Why: User context is needed to validate password and check
        current email.
        """
        user = UserFactory()
        form = EmailChangeForm(user=user)
        assert form.user == user

    def test_email_change_form_valid_data(self):
        """
        Test that form accepts valid email change with correct password.
        
        Why: Users with correct credentials should be able to change email.
        """
        user = UserFactory(email='old@example.com')
        
        with patch('apps.accounts.forms.authenticate') as mock_auth:
            mock_auth.return_value = user
            
            form = EmailChangeForm(
                user=user,
                data={
                    'new_email': 'new@example.com',
                    'password': 'correctpassword',
                }
            )
            
            assert form.is_valid(), form.errors

    def test_email_change_form_rejects_same_email(self):
        """
        Test that form rejects new email identical to current email.
        
        Why: Prevents unnecessary email change requests when email
        isn't actually changing.
        """
        user = UserFactory(email='same@example.com')
        form = EmailChangeForm(
            user=user,
            data={
                'new_email': 'same@example.com',
                'password': 'testpass123',
            }
        )
        
        assert not form.is_valid()
        assert 'new_email' in form.errors
        assert 'stejný jako současný' in str(form.errors['new_email']).lower()

    def test_email_change_form_rejects_duplicate_email(self):
        """
        Test that form rejects email already used by another user.
        
        Why: Email uniqueness must be maintained across all users.
        """
        UserFactory(email='taken@example.com')
        user = UserFactory(email='original@example.com')
        
        form = EmailChangeForm(
            user=user,
            data={
                'new_email': 'taken@example.com',
                'password': 'testpass123',
            }
        )
        
        assert not form.is_valid()
        assert 'new_email' in form.errors
        assert 'již používán' in str(form.errors['new_email']).lower()

    def test_email_change_form_password_verification(self):
        """
        Test that form validates password against user account.
        
        Why: Security measure to prevent unauthorized email changes.
        """
        user = UserFactory(email='current@example.com')
        
        with patch('apps.accounts.forms.authenticate') as mock_auth:
            mock_auth.return_value = None  # Authentication failed
            
            form = EmailChangeForm(
                user=user,
                data={
                    'new_email': 'new@example.com',
                    'password': 'wrongpassword',
                }
            )
            
            assert not form.is_valid()
            assert 'password' in form.errors
            assert 'nesprávné heslo' in str(form.errors['password']).lower()

    def test_email_change_form_password_verification_success(self):
        """
        Test that correct password passes validation.
        
        Why: Validates that the authentication mechanism works correctly.
        """
        user = UserFactory(email='current@example.com')
        
        with patch('apps.accounts.forms.authenticate') as mock_auth:
            mock_auth.return_value = user  # Authentication succeeded
            
            form = EmailChangeForm(
                user=user,
                data={
                    'new_email': 'new@example.com',
                    'password': 'correctpassword',
                }
            )
            
            # Should be valid now
            assert form.is_valid(), form.errors
            
            # Verify authenticate was called with correct parameters
            mock_auth.assert_called_once_with(
                username=user.username,
                password='correctpassword'
            )


# ============================================
# ACCOUNT DELETE FORM TESTS
# ============================================


@pytest.mark.unit
@pytest.mark.forms
class TestAccountDeleteForm:
    """Test suite for AccountDeleteForm."""

    def test_account_delete_form_fields(self):
        """
        Test that delete form has password and confirmation fields.
        
        Why: Account deletion requires double confirmation for safety.
        """
        user = UserFactory()
        form = AccountDeleteForm(user=user)
        
        assert 'password' in form.fields
        assert 'confirm_text' in form.fields

    def test_account_delete_form_valid_data(self):
        """
        Test that form accepts correct password and "SMAZAT" text.
        
        Why: Valid deletion requests should be accepted.
        """
        user = UserFactory()
        
        with patch('apps.accounts.forms.authenticate') as mock_auth:
            mock_auth.return_value = user
            
            form = AccountDeleteForm(
                user=user,
                data={
                    'password': 'correctpassword',
                    'confirm_text': 'SMAZAT',
                }
            )
            
            assert form.is_valid(), form.errors

    def test_account_delete_form_wrong_password(self):
        """
        Test that form rejects incorrect password.
        
        Why: Prevents unauthorized account deletion.
        """
        user = UserFactory()
        
        with patch('apps.accounts.forms.authenticate') as mock_auth:
            mock_auth.return_value = None
            
            form = AccountDeleteForm(
                user=user,
                data={
                    'password': 'wrongpassword',
                    'confirm_text': 'SMAZAT',
                }
            )
            
            assert not form.is_valid()
            assert 'password' in form.errors

    def test_account_delete_form_wrong_confirm_text(self):
        """
        Test that form rejects incorrect confirmation text.
        
        Why: Ensures users consciously confirm deletion by typing
        exact text "SMAZAT".
        """
        user = UserFactory()
        
        with patch('apps.accounts.forms.authenticate') as mock_auth:
            mock_auth.return_value = user
            
            # Try various wrong texts
            wrong_texts = ['smazat', 'SMAŽAT', 'delete', 'DELETE', 'Smazat', '']
            
            for wrong_text in wrong_texts:
                form = AccountDeleteForm(
                    user=user,
                    data={
                        'password': 'correctpassword',
                        'confirm_text': wrong_text,
                    }
                )
                
                assert not form.is_valid(), f"Should reject '{wrong_text}'"
                assert 'confirm_text' in form.errors

    def test_account_delete_form_confirm_text_case_sensitive(self):
        """
        Test that confirmation text is case-sensitive.
        
        Why: Requires exact "SMAZAT" (uppercase) to ensure deliberate action.
        """
        user = UserFactory()
        
        with patch('apps.accounts.forms.authenticate') as mock_auth:
            mock_auth.return_value = user
            
            # Lowercase should fail
            form = AccountDeleteForm(
                user=user,
                data={
                    'password': 'correctpassword',
                    'confirm_text': 'smazat',
                }
            )
            
            assert not form.is_valid()
            assert 'confirm_text' in form.errors

    def test_account_delete_form_placeholder_text(self):
        """
        Test that form shows helpful placeholder.
        
        Why: Guides users on what text to enter for confirmation.
        """
        user = UserFactory()
        form = AccountDeleteForm(user=user)
        
        placeholder = form.fields['confirm_text'].widget.attrs.get('placeholder')
        assert 'SMAZAT' in placeholder
