"""
Views for user account settings.

This module provides views for managing user profiles, goals, privacy settings,
and account security (password change, email change, account deletion).
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, RedirectView
from .forms import ProfileUpdateForm, GoalsUpdateForm, PrivacySettingsForm
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
