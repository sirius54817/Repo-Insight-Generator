from django.contrib import admin
from .models import RepositoryAnalysis, ExportFile


@admin.register(RepositoryAnalysis)
class RepositoryAnalysisAdmin(admin.ModelAdmin):
    list_display = ['repository_name', 'owner', 'status', 'stars', 'forks', 'created_at']
    list_filter = ['status', 'language', 'created_at']
    search_fields = ['repository_name', 'owner', 'repository_url']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Repository Information', {
            'fields': ('repository_url', 'repository_name', 'owner', 'description', 'language')
        }),
        ('Statistics', {
            'fields': ('stars', 'forks')
        }),
        ('Analysis Status', {
            'fields': ('status', 'error_message')
        }),
        ('Results', {
            'fields': ('summary', 'tech_stack', 'file_structure', 'setup_instructions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ExportFile)
class ExportFileAdmin(admin.ModelAdmin):
    list_display = ['analysis', 'format', 'file_size', 'created_at']
    list_filter = ['format', 'created_at']
    search_fields = ['analysis__repository_name', 'analysis__owner']
    readonly_fields = ['id', 'created_at']