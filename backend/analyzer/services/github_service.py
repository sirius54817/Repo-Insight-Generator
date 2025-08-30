import requests
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from django.conf import settings
import base64


class GitHubService:
    """Service to interact with GitHub API and fetch repository data"""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Add authentication if token is provided
        if settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    
    def parse_github_url(self, url: str) -> Tuple[str, str]:
        """
        Parse GitHub URL to extract owner and repo name
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple of (owner, repo_name)
            
        Raises:
            ValueError: If URL is not a valid GitHub repository URL
        """
        # Clean the URL
        url = url.strip().rstrip('/')
        
        # Remove .git extension if present
        if url.endswith('.git'):
            url = url[:-4]
        
        # Handle various GitHub URL formats
        patterns = [
            r'https?://github\.com/([^/]+)/([^/]+)/?$',
            r'git@github\.com:([^/]+)/([^/]+)$',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, url)
            if match:
                owner = match.group(1)
                repo = match.group(2)
                # Clean repo name further if needed
                repo = repo.rstrip('.git')
                return owner, repo
        
        raise ValueError(f"Invalid GitHub repository URL: {url}")
    
    def get_repository_info(self, owner: str, repo: str) -> Dict:
        """
        Get basic repository information
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary containing repository information
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            # Handle specific error cases
            if response.status_code == 401:
                if not settings.GITHUB_TOKEN:
                    raise Exception(
                        "GitHub API authentication required. This could be because:\n"
                        "1. The repository is private and requires a GitHub token\n"
                        "2. You've hit GitHub's API rate limit for unauthenticated requests\n\n"
                        "Solution: Add a GitHub Personal Access Token to your .env file:\n"
                        "1. Go to https://github.com/settings/tokens\n"
                        "2. Click 'Generate new token (classic)'\n"
                        "3. Select 'repo' scope for private repos or 'public_repo' for public repos\n"
                        "4. Copy the token and add it to your .env file as: GITHUB_TOKEN=your_token_here\n"
                        "5. Restart the Django server"
                    )
                else:
                    raise Exception("GitHub API authentication failed. Please check your GITHUB_TOKEN in the .env file.")
            elif response.status_code == 404:
                raise Exception(f"Repository '{owner}/{repo}' not found. Please check the repository URL and make sure it exists.")
            elif response.status_code == 403:
                raise Exception("GitHub API rate limit exceeded or access forbidden. Please add a GitHub token or try again later.")
            
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'name': data.get('name', ''),
                'full_name': data.get('full_name', ''),
                'owner': data.get('owner', {}).get('login', ''),
                'description': data.get('description', ''),
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0),
                'language': data.get('language', ''),
                'topics': data.get('topics', []),
                'created_at': data.get('created_at', ''),
                'updated_at': data.get('updated_at', ''),
                'default_branch': data.get('default_branch', 'main'),
                'clone_url': data.get('clone_url', ''),
                'html_url': data.get('html_url', ''),
                'homepage': data.get('homepage', ''),
                'license': data.get('license', {}).get('name', '') if data.get('license') else '',
                'size': data.get('size', 0),
                'open_issues': data.get('open_issues_count', 0),
            }
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    # This should be caught above, but just in case
                    raise Exception("GitHub API authentication required. Please add a GITHUB_TOKEN to your .env file.")
                elif e.response.status_code == 404:
                    raise Exception(f"Repository not found: {owner}/{repo}")
                else:
                    raise Exception(f"GitHub API error ({e.response.status_code}): {str(e)}")
            else:
                raise Exception(f"Failed to fetch repository info: {str(e)}")
    
    def get_repository_contents(self, owner: str, repo: str, path: str = "", branch: str = None) -> List[Dict]:
        """
        Get repository contents for a specific path
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path within the repository (empty string for root)
            branch: Branch name (defaults to default branch)
            
        Returns:
            List of file/directory information
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {}
        
        if branch:
            params['ref'] = branch
            
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch repository contents: {str(e)}")
    
    def get_file_content(self, owner: str, repo: str, path: str, branch: str = None) -> str:
        """
        Get content of a specific file
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path to the file
            branch: Branch name (defaults to default branch)
            
        Returns:
            File content as string
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {}
        
        if branch:
            params['ref'] = branch
            
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # If it's a file, decode the base64 content
            if data.get('type') == 'file' and data.get('content'):
                content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
                return content
            
            return ""
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch file content: {str(e)}")
    
    def get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        Get programming languages used in the repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary mapping language names to bytes of code
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch repository languages: {str(e)}")
    
    def get_repository_topics(self, owner: str, repo: str) -> List[str]:
        """
        Get repository topics
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of topic strings
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/topics"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('names', [])
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch repository topics: {str(e)}")
    
    def search_repository_files(self, owner: str, repo: str, filename: str) -> List[Dict]:
        """
        Search for files in the repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            filename: Filename to search for
            
        Returns:
            List of matching files
        """
        query = f"filename:{filename} repo:{owner}/{repo}"
        url = f"{self.base_url}/search/code"
        params = {'q': query}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('items', [])
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to search repository files: {str(e)}")
    
    def get_readme_content(self, owner: str, repo: str) -> Optional[str]:
        """
        Get README content from the repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            README content as string or None if not found
        """
        readme_names = ['README.md', 'README.rst', 'README.txt', 'README']
        
        for readme_name in readme_names:
            try:
                content = self.get_file_content(owner, repo, readme_name)
                if content:
                    return content
            except:
                continue
        
        return None
    
    def get_package_files(self, owner: str, repo: str) -> Dict[str, str]:
        """
        Get common package/dependency files content
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary mapping filename to content
        """
        package_files = [
            'package.json', 'requirements.txt', 'Pipfile', 'poetry.lock',
            'Gemfile', 'composer.json', 'pom.xml', 'build.gradle',
            'Cargo.toml', 'go.mod', 'pubspec.yaml', 'Package.swift'
        ]
        
        results = {}
        
        for filename in package_files:
            try:
                content = self.get_file_content(owner, repo, filename)
                if content:
                    results[filename] = content
            except:
                continue
        
        return results