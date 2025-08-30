"""
GitHub API Service for Repository Data Fetching

This service handles all interactions with the GitHub API to fetch repository
data including code files, commit history, and repository metadata.
"""

import requests
from typing import Dict, List, Optional, Any
import logging
import os
from urllib.parse import urlparse
import base64

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub API to fetch repository data."""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'RepoInsightGenerator/1.0'
        }
        
        if self.github_token:
            self.headers['Authorization'] = f'token {self.github_token}'
        else:
            logger.warning("No GitHub token found. Rate limits will be lower.")
    
    def parse_github_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Parse GitHub repository URL to extract owner and repo name.
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Dict with 'owner' and 'repo' keys, or None if invalid
        """
        try:
            parsed = urlparse(url.strip())
            
            # Handle various GitHub URL formats
            if 'github.com' not in parsed.netloc:
                return None
            
            path_parts = [part for part in parsed.path.split('/') if part]
            
            if len(path_parts) >= 2:
                owner = path_parts[0]
                repo = path_parts[1]
                
                # Remove .git suffix if present
                if repo.endswith('.git'):
                    repo = repo[:-4]
                
                return {'owner': owner, 'repo': repo}
                
        except Exception as e:
            logger.error(f"Error parsing GitHub URL {url}: {str(e)}")
        
        return None
    
    def get_repository_info(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Fetch basic repository information from GitHub API.
        
        Args:
            owner: Repository owner/organization
            repo: Repository name
            
        Returns:
            Repository information dictionary or None if error
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.error(f"Repository {owner}/{repo} not found")
            elif response.status_code == 403:
                logger.error("GitHub API rate limit exceeded")
            else:
                logger.error(f"GitHub API error: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Error fetching repository info: {str(e)}")
        
        return None
    
    def get_repository_contents(self, owner: str, repo: str, path: str = "") -> Optional[List[Dict[str, Any]]]:
        """
        Fetch repository contents for a given path.
        
        Args:
            owner: Repository owner/organization
            repo: Repository name
            path: Path within repository (empty string for root)
            
        Returns:
            List of file/directory information or None if error
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching contents: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Error fetching repository contents: {str(e)}")
        
        return None
    
    def get_file_content(self, owner: str, repo: str, file_path: str) -> Optional[str]:
        """
        Fetch the content of a specific file from the repository.
        
        Args:
            owner: Repository owner/organization
            repo: Repository name
            file_path: Path to the file within the repository
            
        Returns:
            File content as string or None if error
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                file_data = response.json()
                
                # Decode base64 content
                if file_data.get('encoding') == 'base64':
                    content = base64.b64decode(file_data['content']).decode('utf-8')
                    return content
                else:
                    logger.warning(f"Unexpected encoding for file {file_path}")
                    
        except requests.RequestException as e:
            logger.error(f"Error fetching file content: {str(e)}")
        except Exception as e:
            logger.error(f"Error decoding file content: {str(e)}")
        
        return None
    
    def get_important_files(self, owner: str, repo: str) -> Dict[str, str]:
        """
        Fetch content of important repository files for analysis.
        
        Args:
            owner: Repository owner/organization
            repo: Repository name
            
        Returns:
            Dictionary mapping file paths to their content
        """
        important_files = [
            'README.md', 'README.rst', 'README.txt', 'README',
            'package.json', 'requirements.txt', 'Pipfile', 'pyproject.toml',
            'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle',
            'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            '.github/workflows', 'Makefile', 'CMakeLists.txt',
            'setup.py', 'setup.cfg', 'composer.json'
        ]
        
        file_contents = {}
        
        for file_path in important_files:
            content = self.get_file_content(owner, repo, file_path)
            if content:
                file_contents[file_path] = content
        
        return file_contents
    
    def get_repository_structure(self, owner: str, repo: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Get the overall structure of the repository.
        
        Args:
            owner: Repository owner/organization
            repo: Repository name
            max_depth: Maximum depth to traverse (default: 3)
            
        Returns:
            Dictionary representing repository structure
        """
        def traverse_directory(path: str = "", current_depth: int = 0) -> Dict[str, Any]:
            if current_depth >= max_depth:
                return {}
            
            contents = self.get_repository_contents(owner, repo, path)
            if not contents:
                return {}
            
            structure = {}
            
            for item in contents:
                item_name = item['name']
                item_path = item['path']
                
                if item['type'] == 'dir':
                    structure[item_name] = {
                        'type': 'directory',
                        'contents': traverse_directory(item_path, current_depth + 1)
                    }
                else:
                    structure[item_name] = {
                        'type': 'file',
                        'size': item.get('size', 0),
                        'download_url': item.get('download_url')
                    }
            
            return structure
        
        return traverse_directory()
    
    def get_recent_commits(self, owner: str, repo: str, count: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch recent commits from the repository.
        
        Args:
            owner: Repository owner/organization
            repo: Repository name
            count: Number of commits to fetch (default: 10)
            
        Returns:
            List of commit information or None if error
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            params = {'per_page': count}
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching commits: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Error fetching recent commits: {str(e)}")
        
        return None
    
    def get_languages(self, owner: str, repo: str) -> Optional[Dict[str, int]]:
        """
        Fetch the programming languages used in the repository.
        
        Args:
            owner: Repository owner/organization
            repo: Repository name
            
        Returns:
            Dictionary mapping language names to byte counts or None if error
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/languages"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching languages: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Error fetching languages: {str(e)}")
        
        return None
    
    def analyze_repository(self, github_url: str) -> Optional[Dict[str, Any]]:
        """
        Perform comprehensive analysis of a GitHub repository.
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Complete repository analysis data or None if error
        """
        parsed = self.parse_github_url(github_url)
        if not parsed:
            logger.error(f"Invalid GitHub URL: {github_url}")
            return None
        
        owner = parsed['owner']
        repo = parsed['repo']
        
        # Gather all repository data
        repo_info = self.get_repository_info(owner, repo)
        if not repo_info:
            return None
        
        analysis_data = {
            'url': github_url,
            'owner': owner,
            'repo': repo,
            'info': repo_info,
            'important_files': self.get_important_files(owner, repo),
            'structure': self.get_repository_structure(owner, repo),
            'recent_commits': self.get_recent_commits(owner, repo),
            'languages': self.get_languages(owner, repo)
        }
        
        return analysis_data


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    service = GitHubService()
    
    # Test with a public repository
    test_url = "https://github.com/octocat/Hello-World"
    result = service.analyze_repository(test_url)
    
    if result:
        print(f"Repository: {result['owner']}/{result['repo']}")
        print(f"Description: {result['info'].get('description', 'No description')}")
        print(f"Languages: {list(result['languages'].keys()) if result['languages'] else 'None'}")
        print(f"Important files found: {list(result['important_files'].keys())}")
    else:
        print("Failed to analyze repository")