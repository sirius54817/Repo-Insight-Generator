from django.urls import path
from . import views

urlpatterns = [
    # Main analysis endpoints
    path('analyze/', views.analyze_repository, name='analyze_repository'),
    path('re-analyze/', views.re_analyze_repository, name='re_analyze_repository'),
    path('analysis/<uuid:analysis_id>/', views.get_analysis, name='get_analysis'),
    path('analyses/', views.list_analyses, name='list_analyses'),
    
    # Export endpoints
    path('export/<str:format_type>/<uuid:analysis_id>/', views.export_analysis, name='export_analysis'),
    path('download/<str:format_type>/<uuid:analysis_id>/', views.download_export, name='download_export'),
    path('analysis/<uuid:analysis_id>/exports/', views.get_analysis_exports, name='get_analysis_exports'),
    
    # Utility endpoints
    path('health/', views.health_check, name='health_check'),
    path('info/', views.api_info, name='api_info'),
]