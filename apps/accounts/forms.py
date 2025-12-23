"""
Custom authentication forms for QuietPage.

This module customizes django-allauth forms to add Czech translations,
placeholders, help texts, and CSS classes matching our design system.
"""

from allauth.account.forms import LoginForm, SignupForm
from django import forms


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
