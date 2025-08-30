"""
Google Gemini API v1 Service for Repository Analysis

This service uses the correct Gemini API v1 endpoint with supported models:
- gemini-1.5-flash (fast and efficient)
- gemini-1.5-pro (more capable for complex analysis)

NOT using deprecated models like 'gemini-pro' or v1beta API.
"""

import google.generativeai as genai
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    """Service to interact with Google Gemini API v1 for repository analysis"""
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required in settings")
        
        # Configure Gemini API v1
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Use supported v1 models (NOT gemini-pro which is deprecated)
        self.model_names = [
            'gemini-1.5-flash',    # Fast and efficient for most tasks
            'gemini-1.5-pro',      # More capable for complex analysis
        ]
        
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini model with fallback options"""
        for model_name in self.model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                # Test the model
                test_response = self.model.generate_content("Test")
                logger.info(f"✅ Successfully initialized Gemini model: {model_name}")
                break
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize {model_name}: {str(e)}")
                continue
        
        if not self.model:
            raise ValueError("No supported Gemini model could be initialized")
    
    def generate_repository_summary(self, repo_data: Dict) -> str:
        """
        Generate a comprehensive repository summary using Gemini API v1
        
        Args:
            repo_data: Dictionary containing repository information
            
        Returns:
            Generated summary text
        """
        prompt = f"""
        Analyze this GitHub repository and provide a comprehensive summary:

        Repository: {repo_data.get('name', 'Unknown')}
        Owner: {repo_data.get('owner', 'Unknown')}
        Description: {repo_data.get('description', 'No description available')}
        Primary Language: {repo_data.get('language', 'Not specified')}
        Stars: {repo_data.get('stars', 0)}
        Forks: {repo_data.get('forks', 0)}
        
        README Content (first 2000 chars):
        {repo_data.get('readme', 'No README available')[:2000]}
        
        Package Files Found:
        {self._format_package_files(repo_data.get('package_files', {}))}
        
        Please provide:
        1. A clear 2-3 sentence summary of what this project does
        2. The main purpose and target audience
        3. Key features and capabilities based on the README and code structure
        4. Notable technologies or frameworks identified
        
        Format as a well-structured summary without markdown headers.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    def generate_setup_instructions(self, repo_data: Dict) -> str:
        """
        Generate setup and run instructions using Gemini API v1
        
        Args:
            repo_data: Dictionary containing repository information
            
        Returns:
            Generated setup instructions
        """
        prompt = f"""
        Based on this repository information, generate clear setup and run instructions:

        Repository: {repo_data.get('name', 'Unknown')}
        Language: {repo_data.get('language', 'Not specified')}
        
        Package Files:
        {self._format_package_files(repo_data.get('package_files', {}))}
        
        README Content:
        {repo_data.get('readme', 'No README available')[:3000]}
        
        File Structure:
        {self._format_file_structure(repo_data.get('file_structure', []))}
        
        Generate step-by-step instructions for:
        1. Prerequisites and dependencies
        2. Installation steps
        3. Configuration (if needed)
        4. How to run the project
        5. Common troubleshooting tips
        
        Make the instructions clear and beginner-friendly.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to generate setup instructions: {str(e)}")
            return f"Error generating setup instructions: {str(e)}"
    
    def analyze_tech_stack(self, repo_data: Dict) -> Dict:
        """
        Analyze and identify the technology stack using Gemini API v1
        
        Args:
            repo_data: Dictionary containing repository information
            
        Returns:
            Dictionary with categorized tech stack information
        """
        prompt = f"""
        Analyze the technology stack of this repository:

        Languages: {repo_data.get('languages', {})}
        Package Files: {self._format_package_files(repo_data.get('package_files', {}))}
        File Extensions: {repo_data.get('file_extensions', [])}
        
        Identify and categorize:
        1. Programming Languages (with percentages if available)
        2. Frameworks and Libraries
        3. Databases (if any)
        4. Build Tools and Task Runners
        5. Testing Frameworks
        6. Development Tools
        7. Cloud/Deployment Platforms mentioned
        
        Return as structured categories with specific technology names.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse the response into structured data
            return self._parse_tech_stack_response(response.text)
        except Exception as e:
            logger.error(f"Failed to analyze tech stack: {str(e)}")
            return {"error": f"Error analyzing tech stack: {str(e)}"}
    
    def _format_package_files(self, package_files: Dict) -> str:
        """Format package files for prompt inclusion"""
        if not package_files:
            return "No package files found"
        
        formatted = []
        for filename, content in package_files.items():
            formatted.append(f"\n--- {filename} ---\n{content[:500]}...")
        
        return "\n".join(formatted)
    
    def _format_file_structure(self, file_structure: List) -> str:
        """Format file structure for prompt inclusion"""
        if not file_structure:
            return "No file structure available"
        
        return "\n".join(file_structure[:20])  # Limit to first 20 files
    
    def _parse_tech_stack_response(self, response_text: str) -> Dict:
        """Parse Gemini response into structured tech stack data"""
        # Simple parsing - in production, you might want more sophisticated parsing
        tech_stack = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "tools": [],
            "testing": [],
            "deployment": []
        }
        
        # Basic parsing logic - can be enhanced
        lines = response_text.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['language', 'programming']):
                current_category = 'languages'
            elif any(keyword in line.lower() for keyword in ['framework', 'library']):
                current_category = 'frameworks'
            elif 'database' in line.lower():
                current_category = 'databases'
            elif any(keyword in line.lower() for keyword in ['tool', 'build']):
                current_category = 'tools'
            elif 'test' in line.lower():
                current_category = 'testing'
            elif any(keyword in line.lower() for keyword in ['deploy', 'cloud']):
                current_category = 'deployment'
            elif line.startswith('-') or line.startswith('*'):
                if current_category:
                    tech_name = line.lstrip('-* ').split(':')[0].strip()
                    if tech_name and current_category in tech_stack:
                        tech_stack[current_category].append(tech_name)
        
        return tech_stack

# Example usage and API endpoint examples for different languages:

"""
Python Example (using this service):
```python
from analyzer.services.gemini_service import GeminiService

service = GeminiService()
summary = service.generate_repository_summary({
    'name': 'my-repo',
    'description': 'A sample repository',
    'language': 'Python',
    'readme': 'README content...'
})
```

Node.js Example (direct API call):
```javascript
const { GoogleGenerativeAI } = require("@google/generative-ai");

const genAI = new GoogleGenerativeAI("YOUR_API_KEY");
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

const result = await model.generateContent("Analyze this repository...");
console.log(result.response.text());
```

cURL Example (REST API v1):
```bash
curl "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: YOUR_API_KEY' \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Analyze this repository and provide a summary..."
          }
        ]
      }
    ]
  }'
```

List Available Models (v1 API):
```bash
curl "https://generativelanguage.googleapis.com/v1/models" \
  -H 'X-goog-api-key: YOUR_API_KEY'
```
"""