"""
Views for user account settings.

This module provides views for managing user profiles, goals, privacy settings,
and account security (password change, email change).
"""

from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db import transaction
from django.db.models import Sum, Count
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import UpdateView, RedirectView, FormView, TemplateView, View
from datetime import timedelta

from .forms import (
    ProfileUpdateForm,
    GoalsUpdateForm,
    PrivacySettingsForm,
    EmailChangeForm,
    AccountDeleteForm,
)
from .models import User, EmailChangeRequest
from .utils import resize_avatar, send_email_verification, verify_email_change_token
from .middleware import log_security_event


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
        # Check if user wants to remove avatar (takes priority over upload)
        if self.request.POST.get('remove_avatar') == 'true':
            if form.instance.avatar:
                form.instance.avatar.delete(save=False)
            form.instance.avatar = None

        # Check if avatar was uploaded
        elif 'avatar' in self.request.FILES:
            avatar_file = self.request.FILES['avatar']
            # Resize avatar to 512x512px
            resized_avatar = resize_avatar(avatar_file)
            form.instance.avatar = resized_avatar
        
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
        stats = Entry.objects.filter(user=user).aggregate(
            total_entries=Count('id'),
            total_words=Sum('word_count')
        )
        
        context['stats'] = {
            'account_created': user.created_at,
            'total_entries': stats['total_entries'] or 0,
            'total_words': stats['total_words'] or 0,
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

        # Log security event
        log_security_event('PASSWORD_CHANGE', self.request.user, self.request)

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
    
    This view creates a pending email change request and sends a verification
    email to the new address. The email is not changed until the user clicks
    the verification link.
    """
    template_name = 'accounts/settings/email_change.html'
    form_class = EmailChangeForm
    success_url = reverse_lazy('accounts:settings-email')
    
    def get_form_kwargs(self):
        """
        Pass current user to form.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """
        Create email change request and send verification email.

        Uses atomic transaction to prevent race condition where multiple
        requests could be created simultaneously.
        """
        new_email = form.cleaned_data['new_email']
        user = self.request.user

        # Atomic transaction to prevent duplicate pending requests
        with transaction.atomic():
            # Cancel any existing pending requests for this user
            EmailChangeRequest.objects.filter(
                user=user,
                is_verified=False
            ).delete()

            # Create new email change request
            EmailChangeRequest.objects.create(
                user=user,
                new_email=new_email
            )

        # Send verification email (outside transaction - email sending can be slow)
        email_sent = send_email_verification(user, new_email, self.request)

        if email_sent:
            # Log security event
            log_security_event(
                'EMAIL_CHANGE_REQUEST',
                user,
                self.request,
                {'new_email': new_email}
            )

            messages.success(
                self.request,
                f'Poslali jsme verifikační odkaz na {new_email}. '
                f'Zkontrolujte svou e-mailovou schránku a klikněte na odkaz pro potvrzení změny.'
            )
        else:
            messages.error(
                self.request,
                'Nepodařilo se odeslat verifikační e-mail. Zkuste to prosím znovu později.'
            )

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """
        Add active section, current email, and pending request to context.
        """
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'email'
        context['current_email'] = self.request.user.email
        
        # Check for pending email change request
        pending_request = EmailChangeRequest.objects.filter(
            user=self.request.user,
            is_verified=False
        ).order_by('-created_at').first()
        
        if pending_request and not pending_request.is_expired():
            context['pending_request'] = pending_request
        
        return context


class EmailVerifyView(TemplateView):
    """
    View for verifying email change via token link.
    
    This view is accessed when user clicks the verification link in their email.
    It validates the token, checks expiry, and atomically updates the user's email.
    """
    template_name = 'accounts/settings/email_verification_result.html'
    
    def get(self, request, token):
        """
        Process the email verification token.
        """
        # Verify and decode the token
        user_id, new_email = verify_email_change_token(token, max_age=86400)  # 24 hours
        
        if not user_id or not new_email:
            return self.render_to_response({
                'success': False,
                'error': 'expired',
                'message': 'Tento odkaz již vypršel. Požádejte prosím o nový verifikační odkaz.'
            })
        
        # Get the user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return self.render_to_response({
                'success': False,
                'error': 'invalid',
                'message': 'Neplatný verifikační odkaz.'
            })
        
        # Find the corresponding email change request
        email_request = EmailChangeRequest.objects.filter(
            user=user,
            new_email=new_email,
            is_verified=False
        ).order_by('-created_at').first()
        
        if not email_request:
            return self.render_to_response({
                'success': False,
                'error': 'invalid',
                'message': 'Tento odkaz již byl použit nebo je neplatný.'
            })
        
        # Check if request has expired
        if email_request.is_expired():
            return self.render_to_response({
                'success': False,
                'error': 'expired',
                'message': 'Tento odkaz již vypršel. Požádejte prosím o nový verifikační odkaz.'
            })

        # Atomically update user email and mark request as verified
        # Uniqueness check MUST be inside transaction to prevent TOCTOU vulnerability
        with transaction.atomic():
            # Re-check if new email is still available (prevent race condition)
            if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                # Delete the request since email is no longer available
                email_request.delete()
                return self.render_to_response({
                    'success': False,
                    'error': 'taken',
                    'message': 'Tento e-mail je již používán jiným účtem.'
                })

            user.email = new_email
            user.save(update_fields=['email'])

            email_request.is_verified = True
            email_request.verified_at = timezone.now()
            email_request.save(update_fields=['is_verified', 'verified_at'])

        # Log security event
        log_security_event(
            'EMAIL_CHANGE_VERIFIED',
            user,
            request,
            {'new_email': new_email}
        )

        return self.render_to_response({
            'success': True,
            'new_email': new_email,
            'message': f'E-mail byl úspěšně změněn na {new_email}.'
        })


class EmailResendVerificationView(LoginRequiredMixin, View):
    """
    View for resending email verification link.
    
    Allows users to request a new verification email if they didn't receive
    the original or if the link expired.
    """
    
    def post(self, request):
        """
        Resend verification email for the most recent pending request.
        """
        # Get the most recent pending request
        pending_request = EmailChangeRequest.objects.filter(
            user=request.user,
            is_verified=False
        ).order_by('-created_at').first()
        
        if not pending_request:
            messages.error(request, 'Nebyly nalezeny žádné nevyřízené žádosti o změnu e-mailu.')
            return redirect('accounts:settings-email')
        
        # Check rate limiting: max 3 requests per hour
        recent_requests = EmailChangeRequest.objects.filter(
            user=request.user,
            new_email=pending_request.new_email,
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        if recent_requests >= 3:
            messages.error(
                request,
                'Příliš mnoho pokusů. Zkuste to prosím znovu později.'
            )
            return redirect('accounts:settings-email')
        
        # Send verification email
        email_sent = send_email_verification(
            request.user,
            pending_request.new_email,
            request
        )
        
        if email_sent:
            messages.success(
                request,
                f'Verifikační odkaz byl znovu odeslán na {pending_request.new_email}.'
            )
        else:
            messages.error(
                request,
                'Nepodařilo se odeslat e-mail. Zkuste to prosím znovu později.'
            )
        
        return redirect('accounts:settings-email')


class EmailCancelChangeView(LoginRequiredMixin, View):
    """
    View for canceling a pending email change request.
    
    Allows users to cancel their email change request if they made a mistake
    or changed their mind.
    """
    
    def post(self, request):
        """
        Cancel any pending email change requests for the current user.
        """
        deleted_count = EmailChangeRequest.objects.filter(
            user=request.user,
            is_verified=False
        ).delete()[0]
        
        if deleted_count > 0:
            messages.success(request, 'Žádost o změnu e-mailu byla zrušena.')
        else:
            messages.info(request, 'Nebyly nalezeny žádné nevyřízené žádosti.')
        
        return redirect('accounts:settings-email')


class AccountDeleteView(LoginRequiredMixin, FormView):
    """
    View for deleting user account with password and text confirmation.
    
    GET - Renders the deletion confirmation form with user statistics
    POST - Validates password and confirmation text, then deletes the account
    """
    template_name = 'accounts/settings/delete_account.html'
    form_class = AccountDeleteForm
    success_url = '/'
    
    def get_form_kwargs(self):
        """
        Pass current user to form.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """
        Delete the user account and log them out.
        """
        user = self.request.user
        
        # Log security event before deletion
        log_security_event('ACCOUNT_DELETION', user, self.request)
        
        # Delete the user (cascades to all related data)
        user.delete()
        
        # Logout the user (session will be invalid after user deletion)
        logout(self.request)
        
        messages.success(self.request, 'Váš účet byl trvale smazán.')
        return redirect('/')
    
    def get_context_data(self, **kwargs):
        """
        Add user statistics to context.
        """
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'delete'
        
        # Get total entries count for the user
        from apps.journal.models import Entry
        total_entries = Entry.objects.filter(user=self.request.user).count()
        context['total_entries'] = total_entries
        
        return context


