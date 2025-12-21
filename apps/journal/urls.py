"""
URL configuration for journal app.
"""

from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    # Placeholder URLs - will be implemented in next task
    path('', views.EntryListView.as_view(), name='entry-list'),
    path('new/', views.EntryCreateView.as_view(), name='entry-create'),
    path('<uuid:pk>/', views.EntryDetailView.as_view(), name='entry-detail'),
    path('<uuid:pk>/edit/', views.EntryUpdateView.as_view(), name='entry-update'),
    path('<uuid:pk>/delete/', views.EntryDeleteView.as_view(), name='entry-delete'),
]
