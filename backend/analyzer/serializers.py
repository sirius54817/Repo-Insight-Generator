from rest_framework import serializers
from .models import RepositoryAnalysis, ExportFile


class RepositoryAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for Repository Analysis"""
    
    class Meta:
        model = RepositoryAnalysis
        fields = [
            'id', 'repository_url', 'repository_name', 'owner',
            'summary', 'tech_stack', 'file_structure', 'setup_instructions',
            'stars', 'forks', 'language', 'description',
            'status', 'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'repository_name', 'owner',
            'summary', 'tech_stack', 'file_structure', 'setup_instructions',
            'stars', 'forks', 'language', 'description', 'status', 'error_message'
        ]


class AnalyzeRepositorySerializer(serializers.Serializer):
    """Serializer for repository analysis request"""
    
    repository_url = serializers.URLField(
        help_text="GitHub repository URL to analyze"
    )
    
    def validate_repository_url(self, value):
        """Validate that the URL is a GitHub repository"""
        if 'github.com' not in value.lower():
            raise serializers.ValidationError(
                "Please provide a valid GitHub repository URL"
            )
        return value


class ExportFileSerializer(serializers.ModelSerializer):
    """Serializer for Export File"""
    
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ExportFile
        fields = ['id', 'format', 'file_size', 'download_url', 'created_at']
    
    def get_download_url(self, obj):
        """Generate download URL for the export file"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                f'/api/download/{obj.format}/{obj.analysis.id}/'
            )
        return f'/api/download/{obj.format}/{obj.analysis.id}/'