"""
Views for user account settings.

This module provides views for managing user profiles, goals, privacy settings,
and account security (password change, email change, account deletion).
"""

from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, RedirectView, FormView
from .forms import (
    ProfileUpdateForm,
    GoalsUpdateForm,
    PrivacySettingsForm,
    EmailChangeForm,
    AccountDeleteForm,
)
from .models import User
from .utils import resize_avatar


class SettingsOverviewView(LoginRequiredMixin, RedirectView):
    """
    Settings overview - redirects to profile page by default.
    """
    pattern_name = 'accounts:settings-profile'
    permanent = False


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating user profile (name, bio, avatar).
    """
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/settings/profile.html'
    success_url = reverse_lazy('accounts:settings-profile')
    
    def get_object(self, queryset=None):
        """
        Return the current logged-in user.
        """
        return self.request.user
    
    def form_valid(self, form):
        """
        Process form submission and resize avatar if uploaded.
        """
        # Check if avatar was uploaded
        if 'avatar' in self.request.FILES:
            avatar_file = self.request.FILES['avatar']
            # Resize avatar to 512x512px
            resized_avatar = resize_avatar(avatar_file)
            form.instance.avatar = resized_avatar
        
        # Check if user wants to remove avatar
        if self.request.POST.get('remove_avatar') == 'true':
            form.instance.avatar.delete(save=False)
            form.instance.avatar = None
        
        messages.success(self.request, 'Profil byl úspěšně aktualizován.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """
        Add extra context for template.
        """
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'profile'
        return context


class GoalsUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating writing goals and preferences.
    """
    model = User
    form_class = GoalsUpdateForm
    template_name = 'accounts/settings/goals.html'
    success_url = reverse_lazy('accounts:settings-goals')
    
    def get_object(self, queryset=None):
        """
        Return the current logged-in user.
        """
        return self.request.user
    
    def form_valid(self, form):
        """
        Process form submission.
        """
        messages.success(self.request, 'Cíle a předvolby byly úspěšně aktualizovány.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """
        Add extra context for template.
        """
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'goals'
        return context


class PrivacySettingsView(LoginRequiredMixin, UpdateView):
    """
    View for updating privacy settings and viewing account statistics.
    """
    model = User
    form_class = PrivacySettingsForm
    template_name = 'accounts/settings/privacy.html'
    success_url = reverse_lazy('accounts:settings-privacy')
    
    def get_object(self, queryset=None):
        """
        Return the current logged-in user.
        """
        return self.request.user
    
    def form_valid(self, form):
        """
        Process form submission.
        """
        messages.success(self.request, 'Nastavení soukromí bylo aktualizováno.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """
        Add extra context including user statistics.
        """
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'privacy'
        
        # Add user statistics
        user = self.request.user
        
        # Get total entries count
        from apps.journal.models import Entry
        total_entries = Entry.objects.filter(user=user).count()
        
        # Get total words written
        total_words = sum(
            Entry.objects.filter(user=user).values_list('word_count', flat=True)
        )
        
        context['stats'] = {
            'account_created': user.created_at,
            'total_entries': total_entries,
            'total_words': total_words,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
        }
        
        return context


# ============================================
# SECURITY VIEWS
# ============================================


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    View for changing user password.
    Uses Django's built-in PasswordChangeView with custom template.
    """
    template_name = 'accounts/settings/password_change.html'
    success_url = reverse_lazy('accounts:settings-password')
    
    def form_valid(self, form):
        """
        Process password change and keep user logged in.
        """
        response = super().form_valid(form)
        # Keep user logged in after password change
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Heslo bylo úspěšně změněno.')
        return response
    
    def get_context_data(self, **kwargs):
        """
        Add active section to context.
        """
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'password'
        return context


class EmailChangeView(LoginRequiredMixin, FormView):
    """
    View for changing user email address with password confirmation.
    """
    template_name = 'accounts/settings/email_change.html'
    form_class = EmailChangeForm
    success_url = reverse_lazy('accounts:settings-profile')
    
    def get_form_kwargs(self):
        """
        Pass current user to form.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """
        Update user email and show success message.
        """
        new_email = form.cleaned_data['new_email']
        self.request.user.email = new_email
        self.request.user.save()
        
        messages.success(
            self.request,
            f'E-mail byl úspěšně změněn na {new_email}.'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """
        Add active section and current email to context.
        """
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'email'
        context['current_email'] = self.request.user.email
        return context


class AccountDeleteView(LoginRequiredMixin, FormView):
    """
    View for permanent account deletion with confirmation.
    Deletes user and all associated data (entries cascade automatically).
    """
    template_name = 'accounts/settings/delete_account.html'
    form_class = AccountDeleteForm
    success_url = reverse_lazy('home')
    
    def get_form_kwargs(self):
        """
        Pass current user to form.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """
        Delete user account and logout.
        """
        user = self.request.user
        username = user.username
        
        # Logout before deleting
        logout(self.request)
        
        # Delete user (CASCADE will delete all entries automatically)
        user.delete()
        
        messages.success(
            self.request,
            f'Účet {username} byl trvale smazán. Děkujeme, že jste s námi byli.'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """
        Add active section and statistics to context.
        """
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'delete'
        
        # Add statistics about what will be deleted
        from apps.journal.models import Entry
        user = self.request.user
        context['total_entries'] = Entry.objects.filter(user=user).count()
        
        return context
