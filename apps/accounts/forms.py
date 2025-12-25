"""
Custom authentication forms for QuietPage.

This module customizes django-allauth forms to add Czech translations,
placeholders, help texts, and CSS classes matching our design system.
"""

from allauth.account.forms import LoginForm, SignupForm
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User


class CustomLoginForm(LoginForm):
    """
    Customized login form with Czech placeholders and CSS classes.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize login field (username or email)
        self.fields['login'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'vas@email.cz nebo uzivatelskeJmeno',
            'autocomplete': 'username',
        })
        self.fields['login'].label = 'Uživatelské jméno nebo e-mail'
        
        # Customize password field
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Vaše heslo',
            'autocomplete': 'current-password',
        })
        self.fields['password'].label = 'Heslo'


class CustomSignupForm(SignupForm):
    """
    Customized signup form with Czech placeholders, help texts, and CSS classes.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize username field
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'uzivatelskeJmeno',
            'autocomplete': 'username',
        })
        self.fields['username'].label = 'Uživatelské jméno'
        self.fields['username'].help_text = 'Minimálně 3 znaky, pouze písmena, čísla a @/./+/-/_'
        
        # Customize email field
        self.fields['email'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'vas@email.cz',
            'autocomplete': 'email',
        })
        self.fields['email'].label = 'E-mailová adresa'
        self.fields['email'].help_text = 'Potřebujeme pro obnovení hesla (volitelné potvrzení)'
        
        # Customize password1 field
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Silné heslo',
            'autocomplete': 'new-password',
        })
        self.fields['password1'].label = 'Heslo'
        self.fields['password1'].help_text = 'Minimálně 8 znaků, nesmí být příliš podobné vašim osobním údajům'
        
        # Customize password2 field
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Zadejte heslo znovu',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].label = 'Potvrzení hesla'
        self.fields['password2'].help_text = ''
    
    def save(self, request):
        """
        Save the user and set default preferences.
        """
        user = super().save(request)
        # Any additional setup for new users can go here
        return user


# ============================================
# USER SETTINGS FORMS
# ============================================


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information (name, bio, avatar).
    """
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Vaše jméno',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Vaše příjmení',
            }),
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
            'first_name': 'Jméno',
            'last_name': 'Příjmení',
            'bio': 'O mně',
            'avatar': 'Profilový obrázek',
        }
        help_texts = {
            'first_name': 'Volitelné',
            'last_name': 'Volitelné',
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
        """
        new_email = self.cleaned_data.get('new_email')
        
        # Check if email is the same as current
        if new_email == self.user.email:
            raise ValidationError('Nový e-mail je stejný jako současný.')
        
        # Check if email is already in use by another user
        if User.objects.filter(email=new_email).exists():
            raise ValidationError('Tento e-mail je již používán jiným účtem.')
        
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
