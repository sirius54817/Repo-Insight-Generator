from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
import os
import logging
from .models import RepositoryAnalysis, ExportFile
from .serializers import (
    AnalyzeRepositorySerializer,
    RepositoryAnalysisSerializer,
    ExportFileSerializer
)
from .services.repository_analyzer import RepositoryAnalyzerService
from .services.export_service import ExportService


logger = logging.getLogger(__name__)


@api_view(['POST'])
def analyze_repository(request):
    """
    Analyze a GitHub repository
    
    POST /api/analyze/
    {
        "repository_url": "https://github.com/owner/repo"
    }
    """
    serializer = AnalyzeRepositorySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    repository_url = serializer.validated_data['repository_url']
    
    try:
        # Check if we have a recent analysis
        analyzer_service = RepositoryAnalyzerService()
        existing_analysis = analyzer_service.get_analysis_by_url(repository_url)
        
        if existing_analysis:
            logger.info(f"Returning existing analysis for {repository_url}")
            serializer = RepositoryAnalysisSerializer(existing_analysis)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Perform new analysis
        logger.info(f"Starting new analysis for {repository_url}")
        analysis = analyzer_service.analyze_repository(repository_url)
        
        serializer = RepositoryAnalysisSerializer(analysis)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Analysis failed for {repository_url}: {str(e)}")
        return Response({
            'error': 'Analysis failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_analysis(request, analysis_id):
    """
    Get analysis details by ID
    
    GET /api/analysis/{analysis_id}/
    """
    try:
        analysis = get_object_or_404(RepositoryAnalysis, id=analysis_id)
        serializer = RepositoryAnalysisSerializer(analysis)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            'error': 'Failed to retrieve analysis',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def re_analyze_repository(request):
    """
    Force re-analysis of a repository
    
    POST /api/re-analyze/
    {
        "repository_url": "https://github.com/owner/repo"
    }
    """
    serializer = AnalyzeRepositorySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    repository_url = serializer.validated_data['repository_url']
    
    try:
        analyzer_service = RepositoryAnalyzerService()
        analysis = analyzer_service.re_analyze_repository(repository_url)
        
        serializer = RepositoryAnalysisSerializer(analysis)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Re-analysis failed for {repository_url}: {str(e)}")
        return Response({
            'error': 'Re-analysis failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def export_analysis(request, analysis_id, format_type):
    """
    Export analysis to specified format
    
    POST /api/export/{format}/{analysis_id}/
    """
    if format_type not in ['md', 'txt', 'pdf', 'docx']:
        return Response({
            'error': 'Invalid format',
            'message': f'Format must be one of: md, txt, pdf, docx. Got: {format_type}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        analysis = get_object_or_404(RepositoryAnalysis, id=analysis_id)
        
        if analysis.status != 'completed':
            return Response({
                'error': 'Analysis not completed',
                'message': f'Analysis status is {analysis.status}. Can only export completed analyses.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        export_service = ExportService()
        export_file = export_service.export_analysis(analysis, format_type)
        
        serializer = ExportFileSerializer(export_file, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Export failed for analysis {analysis_id} format {format_type}: {str(e)}")
        return Response({
            'error': 'Export failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def download_export(request, format_type, analysis_id):
    """
    Download exported file
    
    GET /api/download/{format}/{analysis_id}/
    """
    try:
        analysis = get_object_or_404(RepositoryAnalysis, id=analysis_id)
        export_file = get_object_or_404(
            ExportFile, 
            analysis=analysis, 
            format=format_type
        )
        
        export_service = ExportService()
        file_path = export_service.get_export_file_path(export_file)
        
        if not os.path.exists(file_path):
            # File doesn't exist, try to regenerate it
            logger.warning(f"Export file not found, regenerating: {file_path}")
            export_file = export_service.export_analysis(analysis, format_type)
            file_path = export_service.get_export_file_path(export_file)
            
            if not os.path.exists(file_path):
                raise Http404("Export file not found and could not be regenerated")
        
        # Determine content type
        content_types = {
            'md': 'text/markdown',
            'txt': 'text/plain',
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        content_type = content_types.get(format_type, 'application/octet-stream')
        
        # Generate filename for download
        filename = f"{analysis.repository_name}_{analysis.owner}_analysis.{format_type}"
        
        # Read and serve file
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
    except Exception as e:
        logger.error(f"Download failed for analysis {analysis_id} format {format_type}: {str(e)}")
        return Response({
            'error': 'Download failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_analyses(request):
    """
    List all repository analyses
    
    GET /api/analyses/
    """
    try:
        analyses = RepositoryAnalysis.objects.all().order_by('-created_at')[:50]  # Latest 50
        serializer = RepositoryAnalysisSerializer(analyses, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            'error': 'Failed to list analyses',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_analysis_exports(request, analysis_id):
    """
    Get all exports for an analysis
    
    GET /api/analysis/{analysis_id}/exports/
    """
    try:
        analysis = get_object_or_404(RepositoryAnalysis, id=analysis_id)
        exports = ExportFile.objects.filter(analysis=analysis)
        serializer = ExportFileSerializer(exports, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        return Response({
            'error': 'Failed to retrieve exports',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def health_check(request):
    """
    API health check endpoint
    
    GET /api/health/
    """
    return Response({
        'status': 'healthy',
        'message': 'Repo Insight Generator API is running'
    })


@api_view(['GET'])
def api_info(request):
    """
    API information endpoint
    
    GET /api/info/
    """
    return Response({
        'name': 'Repo Insight Generator API',
        'version': '1.0.0',
        'description': 'Analyze GitHub repositories with AI-powered insights',
        'endpoints': {
            'analyze': '/api/analyze/',
            'get_analysis': '/api/analysis/{id}/',
            'export': '/api/export/{format}/{id}/',
            'download': '/api/download/{format}/{id}/',
            'list_analyses': '/api/analyses/',
            'health': '/api/health/',
        },
        'supported_formats': ['md', 'txt', 'pdf', 'docx']
    })