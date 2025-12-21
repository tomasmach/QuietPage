"""
URL configuration for journal app.

Routes:
- /journal/ - Dashboard (list of entries)
- /journal/new/ - Create new entry
- /journal/<uuid>/ - View single entry
- /journal/<uuid>/edit/ - Edit entry
- /journal/<uuid>/delete/ - Delete entry (with confirmation)
- /journal/autosave/ - AJAX endpoint for auto-saving entries
"""

from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.EntryListView.as_view(), name='entry-list'),
    path('new/', views.EntryCreateView.as_view(), name='entry-create'),
    path('autosave/', views.autosave_entry, name='autosave'),
    path('<uuid:pk>/', views.EntryDetailView.as_view(), name='entry-detail'),
    path('<uuid:pk>/edit/', views.EntryUpdateView.as_view(), name='entry-update'),
    path('<uuid:pk>/delete/', views.EntryDeleteView.as_view(), name='entry-delete'),
]
