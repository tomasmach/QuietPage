"""
Journal views for QuietPage.

These are placeholder views - will be implemented in Úkol 1.
"""

from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Entry


class EntryListView(LoginRequiredMixin, ListView):
    """Dashboard - list of user's journal entries."""
    model = Entry
    template_name = 'journal/entry_list.html'
    context_object_name = 'entries'
    paginate_by = 20
    
    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user).order_by('-created_at')


class EntryCreateView(LoginRequiredMixin, CreateView):
    """Create new journal entry."""
    model = Entry
    template_name = 'journal/entry_form.html'
    fields = ['title', 'content', 'mood_rating', 'tags']
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class EntryDetailView(LoginRequiredMixin, DetailView):
    """View single journal entry."""
    model = Entry
    template_name = 'journal/entry_detail.html'
    context_object_name = 'entry'
    
    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)


class EntryUpdateView(LoginRequiredMixin, UpdateView):
    """Edit existing journal entry."""
    model = Entry
    template_name = 'journal/entry_form.html'
    fields = ['title', 'content', 'mood_rating', 'tags']
    context_object_name = 'entry'
    
    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)


class EntryDeleteView(LoginRequiredMixin, DeleteView):
    """Delete journal entry."""
    model = Entry
    template_name = 'journal/entry_confirm_delete.html'
    context_object_name = 'entry'
    success_url = '/journal/'
    
    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)
