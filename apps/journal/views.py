"""
Journal views for QuietPage.

CRUD operations for journal entries with privacy and user isolation.
"""

from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Entry


class EntryListView(LoginRequiredMixin, ListView):
    """
    Dashboard - list of user's journal entries.
    
    - Displays only entries belonging to the logged-in user
    - Ordered by most recent first
    - Paginated (20 per page)
    """
    model = Entry
    template_name = 'journal/entry_list.html'
    context_object_name = 'entries'
    paginate_by = 20
    
    def get_queryset(self):
        """Filter entries to show only current user's entries."""
        return Entry.objects.filter(user=self.request.user).order_by('-created_at')  # type: ignore


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
        """Redirect to the newly created entry's detail page."""
        return self.object.get_absolute_url()  # type: ignore


class EntryDetailView(LoginRequiredMixin, DetailView):
    """
    View single journal entry.
    
    - Only shows entries belonging to the current user (404 otherwise)
    """
    model = Entry
    template_name = 'journal/entry_detail.html'
    context_object_name = 'entry'
    
    def get_queryset(self):
        """Ensure user can only view their own entries."""
        return Entry.objects.filter(user=self.request.user)  # type: ignore


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
        """Redirect to the updated entry's detail page."""
        return self.object.get_absolute_url()  # type: ignore


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
    success_url = reverse_lazy('journal:entry-list')
    
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
