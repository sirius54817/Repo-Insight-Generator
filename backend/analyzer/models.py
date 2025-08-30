from django.db import models
import uuid


class RepositoryAnalysis(models.Model):
    """Model to store repository analysis results"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    repository_url = models.URLField(max_length=500)
    repository_name = models.CharField(max_length=200)
    owner = models.CharField(max_length=100)
    
    # Analysis results
    summary = models.TextField()
    tech_stack = models.JSONField(default=dict)
    file_structure = models.JSONField(default=dict)
    setup_instructions = models.TextField()
    
    # Metadata
    stars = models.IntegerField(default=0)
    forks = models.IntegerField(default=0)
    language = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField(blank=True, null=True, default='')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Analysis status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('analyzing', 'Analyzing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Repository Analysis'
        verbose_name_plural = 'Repository Analyses'
    
    def __str__(self):
        return f"{self.repository_name} - {self.status}"


class ExportFile(models.Model):
    """Model to track generated export files"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey(RepositoryAnalysis, on_delete=models.CASCADE, related_name='exports')
    
    FORMAT_CHOICES = [
        ('md', 'Markdown'),
        ('txt', 'Text'),
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
    ]
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['analysis', 'format']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.analysis.repository_name} - {self.format.upper()}"