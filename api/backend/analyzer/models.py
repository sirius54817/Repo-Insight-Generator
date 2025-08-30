"""
Django Models for Repository Analysis

This module defines the data models for storing repository analysis results
and export files in the database.
"""

import uuid
import os
from django.db import models
from django.conf import settings


class RepositoryAnalysis(models.Model):
    """Model for storing repository analysis results."""
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    github_url = models.URLField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    repository_data = models.JSONField(null=True, blank=True)  # Store GitHub + AI analysis data
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'repository_analyses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analysis {self.id} - {self.github_url} ({self.status})"
    
    @property
    def repository_name(self):
        """Extract repository name from GitHub URL."""
        if self.repository_data:
            owner = self.repository_data.get('owner', 'unknown')
            repo = self.repository_data.get('repo', 'unknown')
            return f"{owner}/{repo}"
        return "unknown/unknown"


class ExportFile(models.Model):
    """Model for storing exported analysis files."""
    
    FORMAT_CHOICES = [
        ('md', 'Markdown'),
        ('txt', 'Plain Text'),
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey(RepositoryAnalysis, on_delete=models.CASCADE, related_name='export_files')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(default=0)  # Size in bytes
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'export_files'
        unique_together = ['analysis', 'format']  # One file per format per analysis
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.analysis.id} - {self.format} - {self.filename}"
    
    def get_file_path(self):
        """Get the file system path for storing the export file."""
        exports_dir = os.path.join(settings.MEDIA_ROOT, 'exports', str(self.analysis.id))
        os.makedirs(exports_dir, exist_ok=True)
        return os.path.join(exports_dir, self.filename)
    
    def save_content(self, content: bytes):
        """Save file content to the file system."""
        file_path = self.get_file_path()
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Update file size
        self.file_size = len(content)
        self.save()
    
    def get_content(self):
        """Retrieve file content from the file system."""
        file_path = self.get_file_path()
        
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return None
    
    def delete_file(self):
        """Delete the physical file from the file system."""
        file_path = self.get_file_path()
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass  # Ignore file deletion errors
    
    def delete(self, *args, **kwargs):
        """Override delete to remove the physical file."""
        self.delete_file()
        super().delete(*args, **kwargs)
