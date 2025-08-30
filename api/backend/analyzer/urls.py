"""
URL Configuration for Repository Analyzer API

This module defines the URL patterns for the analyzer app:
- Repository analysis endpoint
- Export download endpoints
- Status checking
- Health monitoring
"""

from django.urls import path
from . import views

urlpatterns = [
    # Main analysis endpoint
    path('analyze/', views.analyze_repository, name='analyze_repository'),
    
    # Status and management endpoints
    path('status/<uuid:analysis_id>/', views.get_analysis_status, name='get_analysis_status'),
    path('analyses/', views.list_analyses, name='list_analyses'),
    
    # Export download endpoints
    path('download/<uuid:analysis_id>/<str:format_type>/', views.download_export, name='download_export'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]