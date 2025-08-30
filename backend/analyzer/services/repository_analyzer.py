from typing import Dict, List, Optional
from django.conf import settings
import logging
from .github_service import GitHubService
from .gemini_service import GeminiService
from ..models import RepositoryAnalysis
import json


logger = logging.getLogger(__name__)


class RepositoryAnalyzerService:
    """Main service for analyzing GitHub repositories"""
    
    def __init__(self):
        self.github_service = GitHubService()
        self.gemini_service = GeminiService()
    
    def analyze_repository(self, repository_url: str) -> RepositoryAnalysis:
        """
        Perform complete analysis of a GitHub repository
        
        Args:
            repository_url: GitHub repository URL
            
        Returns:
            RepositoryAnalysis instance with all analysis data
        """
        analysis = None
        
        try:
            # Parse GitHub URL
            owner, repo_name = self.github_service.parse_github_url(repository_url)
            
            # Create analysis record
            analysis = RepositoryAnalysis.objects.create(
                repository_url=repository_url,
                repository_name=repo_name,
                owner=owner,
                status='analyzing'
            )
            
            logger.info(f"Starting analysis for {owner}/{repo_name}")
            
            # Step 1: Fetch basic repository information
            repo_info = self.github_service.get_repository_info(owner, repo_name)
            
            # Step 2: Get additional repository data
            languages = self.github_service.get_repository_languages(owner, repo_name)
            readme_content = self.github_service.get_readme_content(owner, repo_name)
            package_files = self.github_service.get_package_files(owner, repo_name)
            
            # Step 3: Get repository structure
            repo_contents = self.github_service.get_repository_contents(owner, repo_name)
            file_structure = self._build_file_structure(owner, repo_name, repo_contents)
            
            # Step 4: Update basic repository metadata
            analysis.description = repo_info.get('description') or ''
            analysis.stars = repo_info.get('stars', 0)
            analysis.forks = repo_info.get('forks', 0)
            analysis.language = repo_info.get('language') or ''
            analysis.save()
            
            # Step 5: Generate AI-powered insights
            logger.info("Generating repository summary...")
            summary = self.gemini_service.generate_repository_summary(
                repo_info, readme_content, package_files
            )
            
            logger.info("Detecting technology stack...")
            tech_stack = self.gemini_service.detect_tech_stack(
                repo_info, languages, package_files, file_structure
            )
            
            logger.info("Generating setup instructions...")
            setup_instructions = self.gemini_service.generate_setup_instructions(
                repo_info, readme_content, package_files, tech_stack
            )
            
            logger.info("Analyzing file structure...")
            structured_file_analysis = self.gemini_service.analyze_file_structure(
                repo_contents, repo_info
            )
            
            # Step 6: Combine file structure data
            complete_file_structure = {
                "tree": file_structure,
                "analysis": structured_file_analysis,
                "languages": languages,
                "total_files": len(file_structure) if file_structure else 0
            }
            
            # Step 7: Update analysis with generated content
            analysis.summary = summary
            analysis.tech_stack = tech_stack
            analysis.file_structure = complete_file_structure
            analysis.setup_instructions = setup_instructions
            analysis.status = 'completed'
            analysis.save()
            
            logger.info(f"Analysis completed successfully for {owner}/{repo_name}")
            return analysis
            
        except Exception as e:
            error_message = f"Analysis failed: {str(e)}"
            logger.error(error_message)
            
            if analysis:
                analysis.status = 'failed'
                analysis.error_message = error_message
                analysis.save()
                return analysis
            else:
                # Create a failed analysis record
                try:
                    owner, repo_name = self.github_service.parse_github_url(repository_url)
                    analysis = RepositoryAnalysis.objects.create(
                        repository_url=repository_url,
                        repository_name=repo_name,
                        owner=owner,
                        status='failed',
                        error_message=error_message
                    )
                    return analysis
                except:
                    raise Exception(error_message)
    
    def _build_file_structure(self, owner: str, repo_name: str, 
                             contents: List[Dict], path: str = "", 
                             max_depth: int = 3, current_depth: int = 0) -> List[Dict]:
        """
        Build a hierarchical file structure representation
        
        Args:
            owner: Repository owner
            repo_name: Repository name
            contents: List of contents from GitHub API
            path: Current path being processed
            max_depth: Maximum depth to traverse
            current_depth: Current traversal depth
            
        Returns:
            List of dictionaries representing file structure
        """
        if current_depth >= max_depth:
            return []
        
        structure = []
        
        try:
            for item in contents:
                file_info = {
                    "name": item.get('name', ''),
                    "path": item.get('path', ''),
                    "type": item.get('type', 'file'),
                    "size": item.get('size', 0),
                    "download_url": item.get('download_url'),
                }
                
                # If it's a directory and we haven't reached max depth, get its contents
                if (item.get('type') == 'dir' and 
                    current_depth < max_depth - 1 and 
                    not self._should_skip_directory(item.get('name', ''))):
                    
                    try:
                        sub_contents = self.github_service.get_repository_contents(
                            owner, repo_name, item.get('path', '')
                        )
                        file_info["children"] = self._build_file_structure(
                            owner, repo_name, sub_contents, 
                            item.get('path', ''), max_depth, current_depth + 1
                        )
                    except Exception as e:
                        logger.warning(f"Failed to get contents for {item.get('path', '')}: {e}")
                        file_info["children"] = []
                
                structure.append(file_info)
                
        except Exception as e:
            logger.error(f"Error building file structure: {e}")
            
        return structure
    
    def _should_skip_directory(self, dir_name: str) -> bool:
        """
        Determine if a directory should be skipped during traversal
        
        Args:
            dir_name: Directory name
            
        Returns:
            True if directory should be skipped
        """
        skip_dirs = {
            '.git', '.github', 'node_modules', '__pycache__', '.pytest_cache',
            'venv', 'env', '.venv', '.env', 'dist', 'build', '.next',
            'target', 'vendor', '.idea', '.vscode', '.DS_Store',
            'coverage', '.coverage', '.nyc_output', 'logs', 'log'
        }
        
        return dir_name.lower() in skip_dirs or dir_name.startswith('.')
    
    def get_analysis_by_url(self, repository_url: str) -> Optional[RepositoryAnalysis]:
        """
        Get existing analysis for a repository URL
        
        Args:
            repository_url: GitHub repository URL
            
        Returns:
            RepositoryAnalysis instance or None if not found
        """
        try:
            return RepositoryAnalysis.objects.filter(
                repository_url=repository_url,
                status='completed'
            ).first()
        except Exception:
            return None
    
    def re_analyze_repository(self, repository_url: str) -> RepositoryAnalysis:
        """
        Force re-analysis of a repository (even if already analyzed)
        
        Args:
            repository_url: GitHub repository URL
            
        Returns:
            New RepositoryAnalysis instance
        """
        # Delete any existing analysis for this URL
        RepositoryAnalysis.objects.filter(repository_url=repository_url).delete()
        
        # Perform fresh analysis
        return self.analyze_repository(repository_url)
    
    def get_analysis_summary(self, analysis_id: str) -> Dict:
        """
        Get a summary of the analysis results
        
        Args:
            analysis_id: Analysis UUID
            
        Returns:
            Dictionary containing analysis summary
        """
        try:
            analysis = RepositoryAnalysis.objects.get(id=analysis_id)
            
            return {
                "repository": {
                    "name": analysis.repository_name,
                    "owner": analysis.owner,
                    "url": analysis.repository_url,
                    "description": analysis.description,
                    "language": analysis.language,
                    "stars": analysis.stars,
                    "forks": analysis.forks,
                },
                "summary": analysis.summary,
                "tech_stack": analysis.tech_stack,
                "file_structure_summary": {
                    "total_files": analysis.file_structure.get("total_files", 0),
                    "languages": analysis.file_structure.get("languages", {}),
                    "main_directories": [
                        item["name"] for item in analysis.file_structure.get("tree", [])
                        if item.get("type") == "dir"
                    ][:10]  # Top 10 directories
                },
                "status": analysis.status,
                "created_at": analysis.created_at,
                "updated_at": analysis.updated_at,
            }
            
        except RepositoryAnalysis.DoesNotExist:
            raise Exception(f"Analysis with ID {analysis_id} not found")