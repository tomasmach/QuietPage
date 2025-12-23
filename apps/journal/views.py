"""
Journal views for QuietPage.

CRUD operations for journal entries with privacy and user isolation.
"""

import json
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.shortcuts import redirect

from .models import Entry
from .utils import get_random_quote

# Logger for this module
logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard after login.
    
    Features:
    - Time-based greeting (4-9, 9-12, 12-18, 18-4)
    - Recent entries overview
    - Statistics (total entries, current streak, word count)
    - Quick action button for new entry
    """
    template_name = 'journal/dashboard.html'
    
    def get_greeting(self):
        """Return time-based greeting in Czech."""
        # Get current hour in user's timezone
        user_tz = ZoneInfo(str(self.request.user.timezone))  # type: ignore
        now = timezone.now().astimezone(user_tz)
        hour = now.hour
        
        if 4 <= hour < 9:
            return "Dobré ráno"
        elif 9 <= hour < 12:
            return "Dobré dopoledne"
        elif 12 <= hour < 18:
            return "Dobré odpoledne"
        else:  # 18-4
            return "Dobrý večer"
    
    def get_context_data(self, **kwargs):
        """Add dashboard data to context."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Time-based greeting
        context['greeting'] = self.get_greeting()
        context['user_first_name'] = user.first_name or user.username
        
        # Recent entries (all entries for MVP) - only select needed fields to avoid decryption issues
        context['recent_entries'] = Entry.objects.filter(  # type: ignore
            user=user
        ).only('id', 'title', 'created_at', 'mood_rating', 'word_count').order_by('-created_at')
        
        # Statistics - use aggregation to avoid loading encrypted content
        context['stats'] = {
            'total_entries': Entry.objects.filter(user=user).count(),  # type: ignore
            'current_streak': user.current_streak,  # type: ignore
            'total_words': Entry.objects.filter(user=user).aggregate(  # type: ignore
                total=Sum('word_count')
            )['total'] or 0,
        }
        
        # Inspirational quote for empty state
        context['quote'] = get_random_quote()
        
        return context


class EntryListView(LoginRequiredMixin, ListView):
    """
    Full list of user's journal entries.
    
    - Displays only entries belonging to the logged-in user
    - Ordered by most recent first
    - Paginated (20 per page)
    """
    model = Entry
    template_name = 'journal/entry_list.html'
    context_object_name = 'entries'
    paginate_by = 20
    
    def get_queryset(self):
        """Filter entries to show only current user's entries - avoid loading encrypted content."""
        return Entry.objects.filter(  # type: ignore
            user=self.request.user
        ).only('id', 'title', 'created_at', 'mood_rating', 'word_count').order_by('-created_at')


class EntryCreateView(LoginRequiredMixin, CreateView):
    """
    Create new journal entry.
    
    - Auto-assigns entry to current user
    - Calculates word count automatically (in model save method)
    - Shows success message after creation
    """
    model = Entry
    template_name = 'journal/entry_form.html'
    fields = ['title', 'content', 'mood_rating', 'tags']
    
    def form_valid(self, form):
        """Assign the entry to the current user before saving."""
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Show success message
        messages.success(
            self.request,
            'Záznam byl úspěšně vytvořen.'
        )
        
        return response
    
    def get_success_url(self):
        """Redirect directly to edit view to avoid redirect chain."""
        return reverse('journal:entry-update', kwargs={'pk': self.object.pk})  # type: ignore


class EntryDetailView(LoginRequiredMixin, DetailView):
    """
    View single journal entry - redirects to edit for MVP.
    
    - Only shows entries belonging to the current user (404 otherwise)
    - For MVP, we redirect directly to edit mode instead of showing read-only view
    """
    model = Entry
    
    def get_queryset(self):
        """Ensure user can only view their own entries."""
        return Entry.objects.filter(user=self.request.user)  # type: ignore
    
    def get(self, request, *args, **kwargs):
        """Redirect to edit view for MVP simplicity."""
        self.object = self.get_object()
        return redirect('journal:entry-update', pk=self.object.pk)


class EntryUpdateView(LoginRequiredMixin, UpdateView):
    """
    Edit existing journal entry.
    
    - Only allows editing user's own entries (404 otherwise)
    - Shows success message after update
    """
    model = Entry
    template_name = 'journal/entry_form.html'
    fields = ['title', 'content', 'mood_rating', 'tags']
    context_object_name = 'entry'
    
    def get_queryset(self):
        """Ensure user can only edit their own entries."""
        return Entry.objects.filter(user=self.request.user)  # type: ignore
    
    def form_valid(self, form):
        """Show success message after update."""
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            'Záznam byl úspěšně upraven.'
        )
        
        return response
    
    def get_success_url(self):
        """Redirect to dashboard after successful update."""
        return reverse('journal:dashboard')


class EntryDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete journal entry.
    
    - Only allows deleting user's own entries (404 otherwise)
    - Shows success message after deletion
    - Redirects to dashboard after deletion
    """
    model = Entry
    template_name = 'journal/entry_confirm_delete.html'
    context_object_name = 'entry'
    success_url = reverse_lazy('journal:dashboard')
    
    def get_queryset(self):
        """Ensure user can only delete their own entries."""
        return Entry.objects.filter(user=self.request.user)  # type: ignore
    
    def delete(self, request, *args, **kwargs):
        """Show success message after deletion."""
        messages.success(
            self.request,
            'Záznam byl úspěšně smazán.'
        )
        return super().delete(request, *args, **kwargs)


@login_required
@require_POST
def autosave_entry(request):
    """
    AJAX endpoint for auto-saving journal entries.
    
    Creates a new entry or updates existing one based on entry_id.
    Returns JSON response with status and entry ID.
    """
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        mood_rating = data.get('mood_rating', None)
        tags_str = data.get('tags', '').strip()
        entry_id = data.get('entry_id', None)
        
        # Content is required for saving
        if not content:
            return JsonResponse({
                'status': 'error',
                'message': 'Obsah nemůže být prázdný'
            }, status=400)
        
        # Update existing entry or create new one
        if entry_id:
            try:
                entry = Entry.objects.get(id=entry_id, user=request.user)  # type: ignore
                entry.title = title
                entry.content = content
                entry.mood_rating = mood_rating
                entry.save()
                
                # Update tags (clear if empty, set if provided)
                entry.tags.set([tag.strip() for tag in tags_str.split(',') if tag.strip()])  # type: ignore
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Uloženo',
                    'entry_id': str(entry.id),
                    'is_new': False
                })
            except Entry.DoesNotExist:  # type: ignore
                return JsonResponse({
                    'status': 'error',
                    'message': 'Záznam nenalezen'
                }, status=404)
        else:
            # Create new entry
            entry = Entry.objects.create(  # type: ignore
                user=request.user,
                title=title,
                content=content,
                mood_rating=mood_rating
            )
            
            # Add tags if provided
            if tags_str:
                entry.tags.set([tag.strip() for tag in tags_str.split(',') if tag.strip()])  # type: ignore
            
            return JsonResponse({
                'status': 'success',
                'message': 'Uloženo',
                'entry_id': str(entry.id),
                'is_new': True
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Neplatná data'
        }, status=400)
    except Exception:
        # Log the full exception with stack trace on the server
        logger.exception('Unexpected error during auto-save')
        
        # Return generic error message to the client (don't expose internal details)
        return JsonResponse({
            'status': 'error',
            'message': 'Chyba při ukládání.'
        }, status=500)
