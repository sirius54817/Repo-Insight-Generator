"""
Django REST API Views for Repository Analysis

This module contains the API endpoints for:
- Repository analysis
- Export file downloads
- Analysis status checking
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from django.conf import settings
import logging
import json
from typing import Dict, Any

from .models import RepositoryAnalysis, ExportFile
from .services.github_service import GitHubService
from .services.gemini_service import GeminiService
from .services.export_service import ExportService

logger = logging.getLogger(__name__)


@api_view(['POST'])
def analyze_repository(request):
    """
    Analyze a GitHub repository and return insights.
    
    Expected JSON payload:
    {
        "github_url": "https://github.com/owner/repo",
        "analysis_type": "comprehensive"  // optional, default: "comprehensive"
    }
    
    Returns:
    {
        "id": "uuid",
        "status": "completed",
        "github_url": "https://github.com/owner/repo",
        "analysis": {
            "summary": "...",
            "tech_stack": "...",
            "setup_instructions": "..."
        },
        "export_urls": {
            "md": "/api/download/uuid/md/",
            "txt": "/api/download/uuid/txt/",
            "pdf": "/api/download/uuid/pdf/",
            "docx": "/api/download/uuid/docx/"
        }
    }
    """
    try:
        # Validate request data
        github_url = request.data.get('github_url')
        if not github_url:
            return Response(
                {'error': 'github_url is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        analysis_type = request.data.get('analysis_type', 'comprehensive')
        
        # Initialize services
        github_service = GitHubService()
        gemini_service = GeminiService()
        export_service = ExportService()
        
        # Create analysis record
        analysis = RepositoryAnalysis.objects.create(
            github_url=github_url,
            status='processing'
        )
        
        logger.info(f"Starting analysis for {github_url} (ID: {analysis.id})")
        
        # Step 1: Fetch repository data from GitHub
        repo_data = github_service.analyze_repository(github_url)
        if not repo_data:
            analysis.status = 'failed'
            analysis.error_message = 'Failed to fetch repository data from GitHub'
            analysis.save()
            
            return Response(
                {'error': 'Failed to fetch repository data. Please check the GitHub URL.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Step 2: Generate AI analysis using Gemini
        ai_analysis = {}
        
        try:
            # Generate repository summary
            summary = gemini_service.analyze_repository(repo_data)
            if summary:
                ai_analysis['summary'] = summary
            
            # Generate tech stack analysis
            tech_stack = gemini_service.analyze_tech_stack(repo_data)
            if tech_stack:
                ai_analysis['tech_stack'] = tech_stack
            
            # Generate setup instructions
            setup_instructions = gemini_service.generate_setup_instructions(repo_data)
            if setup_instructions:
                ai_analysis['setup_instructions'] = setup_instructions
                
        except Exception as e:
            logger.error(f"Error during AI analysis: {str(e)}")
            # Continue without AI analysis rather than failing completely
            ai_analysis['error'] = 'AI analysis temporarily unavailable'
        
        # Combine all analysis data
        complete_analysis_data = {
            **repo_data,
            'analysis': ai_analysis
        }
        
        # Step 3: Generate export files
        export_files = {}
        for format_type in ['md', 'txt', 'pdf', 'docx']:
            try:
                export_content = export_service.export_analysis(complete_analysis_data, format_type)
                if export_content:
                    filename = export_service.get_filename(complete_analysis_data, format_type)
                    
                    export_file = ExportFile.objects.create(
                        analysis=analysis,
                        format=format_type,
                        filename=filename,
                        file_size=len(export_content)
                    )
                    
                    # Save the file content (in production, you might want to use cloud storage)
                    export_file.save_content(export_content)
                    export_files[format_type] = export_file.id
                    
            except Exception as e:
                logger.error(f"Error generating {format_type} export: {str(e)}")
                # Continue with other formats
        
        # Step 4: Update analysis record
        analysis.repository_data = complete_analysis_data
        analysis.status = 'completed'
        analysis.save()
        
        # Step 5: Prepare response
        export_urls = {}
        for format_type, export_id in export_files.items():
            export_urls[format_type] = f"/api/download/{analysis.id}/{format_type}/"
        
        response_data = {
            'id': str(analysis.id),
            'status': analysis.status,
            'github_url': github_url,
            'analysis': ai_analysis,
            'repository_info': {
                'name': f"{repo_data.get('owner')}/{repo_data.get('repo')}",
                'description': repo_data.get('info', {}).get('description'),
                'language': repo_data.get('info', {}).get('language'),
                'stars': repo_data.get('info', {}).get('stargazers_count', 0),
                'forks': repo_data.get('info', {}).get('forks_count', 0)
            },
            'export_urls': export_urls,
            'created_at': analysis.created_at.isoformat()
        }
        
        logger.info(f"Analysis completed successfully for {github_url}")
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error during repository analysis: {str(e)}")
        
        # Update analysis record if it exists
        if 'analysis' in locals():
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.save()
        
        return Response(
            {'error': 'Internal server error during analysis'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_analysis_status(request, analysis_id):
    """
    Get the status of a repository analysis.
    
    Returns:
    {
        "id": "uuid",
        "status": "processing|completed|failed",
        "github_url": "https://github.com/owner/repo",
        "created_at": "2023-12-01T10:30:45Z",
        "error_message": "..." // only if status is "failed"
    }
    """
    try:
        analysis = RepositoryAnalysis.objects.get(id=analysis_id)
        
        response_data = {
            'id': str(analysis.id),
            'status': analysis.status,
            'github_url': analysis.github_url,
            'created_at': analysis.created_at.isoformat()
        }
        
        if analysis.status == 'failed' and analysis.error_message:
            response_data['error_message'] = analysis.error_message
        
        return Response(response_data)
        
    except RepositoryAnalysis.DoesNotExist:
        return Response(
            {'error': 'Analysis not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def download_export(request, analysis_id, format_type):
    """
    Download an exported analysis file.
    
    URL: /api/download/<analysis_id>/<format>/
    Formats: md, txt, pdf, docx
    
    Returns the file as a download response.
    """
    try:
        # Validate format
        if format_type not in ['md', 'txt', 'pdf', 'docx']:
            return Response(
                {'error': 'Invalid format. Supported formats: md, txt, pdf, docx'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get analysis
        analysis = RepositoryAnalysis.objects.get(id=analysis_id)
        
        if analysis.status != 'completed':
            return Response(
                {'error': 'Analysis not completed yet'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get export file
        try:
            export_file = ExportFile.objects.get(analysis=analysis, format=format_type)
        except ExportFile.DoesNotExist:
            # Generate the file on-demand if it doesn't exist
            export_service = ExportService()
            export_content = export_service.export_analysis(analysis.repository_data, format_type)
            
            if not export_content:
                return Response(
                    {'error': f'Failed to generate {format_type} export'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            filename = export_service.get_filename(analysis.repository_data, format_type)
            
            # Create export file record
            export_file = ExportFile.objects.create(
                analysis=analysis,
                format=format_type,
                filename=filename,
                file_size=len(export_content)
            )
            export_file.save_content(export_content)
        
        # Get file content
        file_content = export_file.get_content()
        if not file_content:
            return Response(
                {'error': 'Export file content not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Determine content type
        content_types = {
            'md': 'text/markdown',
            'txt': 'text/plain',
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        content_type = content_types.get(format_type, 'application/octet-stream')
        
        # Create response
        response = HttpResponse(file_content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{export_file.filename}"'
        response['Content-Length'] = len(file_content)
        
        return response
        
    except RepositoryAnalysis.DoesNotExist:
        return Response(
            {'error': 'Analysis not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error downloading export: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_analyses(request):
    """
    List recent repository analyses.
    
    Query parameters:
    - limit: Number of results to return (default: 20, max: 100)
    - status: Filter by status (processing, completed, failed)
    
    Returns:
    {
        "results": [
            {
                "id": "uuid",
                "status": "completed",
                "github_url": "https://github.com/owner/repo",
                "created_at": "2023-12-01T10:30:45Z",
                "repository_name": "owner/repo"
            }
        ],
        "count": 25
    }
    """
    try:
        # Get query parameters
        limit = min(int(request.GET.get('limit', 20)), 100)
        status_filter = request.GET.get('status')
        
        # Build queryset
        queryset = RepositoryAnalysis.objects.all().order_by('-created_at')
        
        if status_filter and status_filter in ['processing', 'completed', 'failed']:
            queryset = queryset.filter(status=status_filter)
        
        # Get results
        analyses = queryset[:limit]
        total_count = queryset.count()
        
        # Format response
        results = []
        for analysis in analyses:
            repo_data = analysis.repository_data or {}
            repo_name = f"{repo_data.get('owner', 'unknown')}/{repo_data.get('repo', 'unknown')}"
            
            results.append({
                'id': str(analysis.id),
                'status': analysis.status,
                'github_url': analysis.github_url,
                'created_at': analysis.created_at.isoformat(),
                'repository_name': repo_name
            })
        
        return Response({
            'results': results,
            'count': total_count
        })
        
    except Exception as e:
        logger.error(f"Error listing analyses: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint for monitoring.
    
    Returns:
    {
        "status": "healthy",
        "services": {
            "github": "available",
            "gemini": "available"
        }
    }
    """
    services_status = {}
    
    # Check GitHub service
    try:
        github_service = GitHubService()
        # Try to parse a test URL
        test_result = github_service.parse_github_url("https://github.com/octocat/Hello-World")
        services_status['github'] = 'available' if test_result else 'error'
    except Exception:
        services_status['github'] = 'error'
    
    # Check Gemini service
    try:
        gemini_service = GeminiService()
        services_status['gemini'] = 'available' if gemini_service.model else 'error'
    except Exception:
        services_status['gemini'] = 'error'
    
    overall_status = 'healthy' if all(s == 'available' for s in services_status.values()) else 'degraded'
    
    return Response({
        'status': overall_status,
        'services': services_status
    })
