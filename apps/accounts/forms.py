"""
Custom forms for QuietPage user settings.

This module provides forms for user profile management, goals, privacy settings,
and account security operations.
"""

from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import pytz
from .models import User


# ============================================
# USER SETTINGS FORMS
# ============================================


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information (name, bio, avatar).
    """
    
    class Meta:
        model = User
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Krátký text o vás...',
                'rows': 4,
                'maxlength': 500,
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*',
            }),
        }
        labels = {
            'bio': 'O mně',
            'avatar': 'Profilový obrázek',
        }
        help_texts = {
            'bio': 'Maximálně 500 znaků',
            'avatar': 'Max 2MB, doporučeno 512x512px (JPG, PNG)',
        }
    
    def clean_avatar(self):
        """
        Validate avatar file size and type.
        """
        avatar = self.cleaned_data.get('avatar')
        
        if avatar:
            # Only validate if it's a new upload (has content_type attribute)
            # ImageFieldFile from existing avatar doesn't have content_type
            if hasattr(avatar, 'content_type'):
                # Check file size (max 2MB)
                if avatar.size > 2 * 1024 * 1024:
                    raise ValidationError('Soubor je příliš velký. Maximální velikost je 2MB.')
                
                # Check file type
                valid_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
                if avatar.content_type not in valid_types:
                    raise ValidationError('Neplatný formát obrázku. Použijte JPG, PNG nebo WebP.')
        
        return avatar


class GoalsUpdateForm(forms.ModelForm):
    """
    Form for updating writing goals and preferences.
    """

    class Meta:
        model = User
        fields = ['daily_word_goal', 'preferred_writing_time', 'reminder_enabled', 'reminder_time', 'timezone']
        widgets = {
            'daily_word_goal': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 100,
                'max': 5000,
                'step': 50,
            }),
            'preferred_writing_time': forms.Select(attrs={
                'class': 'form-input',
            }),
            'reminder_enabled': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
            'reminder_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time',
            }),
            'timezone': forms.Select(attrs={
                'class': 'form-input',
            }),
        }
        labels = {
            'daily_word_goal': 'Denní cíl slov',
            'preferred_writing_time': 'Preferovaná doba psaní',
            'reminder_enabled': 'Zapnout denní připomínku',
            'reminder_time': 'Čas připomínky',
            'timezone': 'Časové pásmo',
        }
        help_texts = {
            'daily_word_goal': 'Kolik slov chcete psát denně (100-5000)',
            'preferred_writing_time': 'Kdy většinou píšete',
            'reminder_enabled': 'Připomeneme vám psaní každý den',
            'reminder_time': 'V kolik hodin chcete dostat připomínku',
            'timezone': 'Pro správné zobrazení času',
        }

    def clean_timezone(self):
        """
        Validate that timezone is valid according to pytz.
        Belt-and-suspenders validation (TimeZoneField should handle this, but we double-check).
        """
        tz = self.cleaned_data.get('timezone')
        if tz:
            try:
                pytz.timezone(str(tz))
            except pytz.UnknownTimeZoneError:
                raise ValidationError('Neplatná časová zóna.')
        return tz


class PrivacySettingsForm(forms.ModelForm):
    """
    Form for updating privacy settings.
    """
    
    class Meta:
        model = User
        fields = ['email_notifications']
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }
        labels = {
            'email_notifications': 'Povolit e-mailové notifikace',
        }
        help_texts = {
            'email_notifications': 'Zasílat připomínky a novinky na e-mail',
        }


class EmailChangeForm(forms.Form):
    """
    Form for changing user email address with password confirmation.
    """
    
    new_email = forms.EmailField(
        label='Nový e-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'novy@email.cz',
            'autocomplete': 'email',
        }),
        help_text='Zadejte novou e-mailovou adresu',
    )
    
    password = forms.CharField(
        label='Potvrzení hesla',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Vaše současné heslo',
            'autocomplete': 'current-password',
        }),
        help_text='Pro potvrzení změny zadejte své heslo',
    )
    
    def __init__(self, user, *args, **kwargs):
        """
        Initialize form with user instance.
        """
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_new_email(self):
        """
        Validate that new email is different and not already in use.
        Includes additional security checks.
        """
        new_email = self.cleaned_data.get('new_email')

        # Check if email is the same as current
        if new_email == self.user.email:
            raise ValidationError('Nový e-mail je stejný jako současný.')

        # Check if email is already in use by another user
        if User.objects.filter(email=new_email).exists():
            raise ValidationError('Tento e-mail je již používán jiným účtem.')

        # Optional: Block disposable email domains (uncomment if needed)
        # disposable_domains = ['tempmail.com', 'guerrillamail.com', '10minutemail.com']
        # domain = new_email.split('@')[1].lower()
        # if domain in disposable_domains:
        #     raise ValidationError('Dočasné e-mailové adresy nejsou povoleny.')

        return new_email
    
    def clean_password(self):
        """
        Validate that password is correct.
        """
        password = self.cleaned_data.get('password')
        
        # Authenticate user with current password
        user = authenticate(username=self.user.username, password=password)
        if not user:
            raise ValidationError('Nesprávné heslo.')
        
        return password


class AccountDeleteForm(forms.Form):
    """
    Form for account deletion with password and text confirmation.
    """
    
    password = forms.CharField(
        label='Potvrzení hesla',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Vaše heslo',
            'autocomplete': 'current-password',
        }),
        help_text='Zadejte své heslo pro potvrzení',
    )
    
    confirm_text = forms.CharField(
        label='Potvrzovací text',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Napište SMAZAT',
        }),
        help_text='Pro potvrzení napište slovo "SMAZAT" (velkými písmeny)',
    )
    
    def __init__(self, user, *args, **kwargs):
        """
        Initialize form with user instance.
        """
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_password(self):
        """
        Validate that password is correct.
        """
        password = self.cleaned_data.get('password')
        
        # Authenticate user with current password
        user = authenticate(username=self.user.username, password=password)
        if not user:
            raise ValidationError('Nesprávné heslo.')
        
        return password
    
    def clean_confirm_text(self):
        """
        Validate that user typed exactly "SMAZAT".
        """
        confirm_text = self.cleaned_data.get('confirm_text')
        
        if confirm_text != 'SMAZAT':
            raise ValidationError('Musíte napsat "SMAZAT" pro potvrzení smazání účtu.')
        
        return confirm_text
