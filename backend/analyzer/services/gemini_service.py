import google.generativeai as genai
from django.conf import settings
from typing import Dict, List, Optional
import json
import re


class GeminiService:
    """Service to interact with Google Gemini Pro API for repository analysis"""
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required in settings")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Try to use the latest Gemini models, prioritizing newest versions
        model_names = [
            'gemini-2.5-flash',           # Latest 2.5 model
            'models/gemini-2.5-flash',    # Alternative format
            'gemini-2.0-flash',           # 2.0 model
            'models/gemini-2.0-flash',    # Alternative format
            'gemini-1.5-flash',           # 1.5 fallback
            'models/gemini-1.5-flash',    # Alternative format
            'gemini-1.5-pro',             # Pro fallback
            'models/gemini-1.5-pro'       # Alternative format
        ]
        
        self.model = None
        last_error = None
        
        for model_name in model_names:
            try:
                print(f"🔄 Trying model: {model_name}")
                self.model = genai.GenerativeModel(model_name)
                # Test the model with a simple request
                test_response = self.model.generate_content("Test")
                print(f"✅ Successfully using Gemini model: {model_name}")
                break
            except Exception as e:
                print(f"⚠️ Model {model_name} failed: {str(e)}")
                last_error = e
                continue
        
        if not self.model:
            raise ValueError(f"No working Gemini model found. Last error: {last_error}. Please check your API key and model availability.")
    
    def generate_repository_summary(self, repo_info: Dict, readme_content: str = None, 
                                   package_files: Dict = None) -> str:
        """
        Generate a comprehensive summary of the repository
        
        Args:
            repo_info: Basic repository information from GitHub API
            readme_content: Content of README file
            package_files: Dictionary of package/dependency files
            
        Returns:
            Generated summary text
        """
        prompt = f"""
        Analyze this GitHub repository and provide a comprehensive summary:

        Repository Information:
        - Name: {repo_info.get('name', 'N/A')}
        - Description: {repo_info.get('description', 'N/A')}
        - Primary Language: {repo_info.get('language', 'N/A')}
        - Stars: {repo_info.get('stars', 0)}
        - Forks: {repo_info.get('forks', 0)}
        - Topics: {', '.join(repo_info.get('topics', []))}
        
        {"README Content:" if readme_content else ""}
        {readme_content[:3000] if readme_content else "No README available"}
        
        {"Package Files:" if package_files else ""}
        {self._format_package_files(package_files) if package_files else "No package files found"}
        
        Please provide:
        1. A clear, concise summary of what this project does (2-3 sentences)
        2. The main purpose and target audience
        3. Key features and capabilities
        4. Notable technologies or frameworks used
        
        Format the response as a well-structured summary without markdown headers.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Failed to generate summary: {str(e)}"
    
    def detect_tech_stack(self, repo_info: Dict, languages: Dict, 
                         package_files: Dict, file_structure: List) -> Dict:
        """
        Analyze and detect the technology stack used in the repository
        
        Args:
            repo_info: Basic repository information
            languages: Programming languages with byte counts
            package_files: Dictionary of package/dependency files
            file_structure: List of files and directories
            
        Returns:
            Dictionary containing detected tech stack information
        """
        prompt = f"""
        Analyze this repository's technology stack and provide a detailed breakdown:

        Programming Languages (by bytes of code):
        {json.dumps(languages, indent=2) if languages else "No language data"}

        Package/Dependency Files:
        {self._format_package_files(package_files) if package_files else "No package files found"}

        File Structure Sample:
        {self._format_file_structure(file_structure[:50]) if file_structure else "No file structure data"}

        Repository Metadata:
        - Primary Language: {repo_info.get('language', 'N/A')}
        - Topics: {', '.join(repo_info.get('topics', []))}

        Please analyze and return a JSON object with the following structure:
        {{
            "primary_languages": ["language1", "language2"],
            "frameworks": ["framework1", "framework2"],
            "databases": ["db1", "db2"],
            "tools_and_services": ["tool1", "tool2"],
            "deployment": ["platform1", "platform2"],
            "testing": ["testing_framework1", "testing_framework2"],
            "build_tools": ["build_tool1", "build_tool2"],
            "package_managers": ["manager1", "manager2"],
            "development_tools": ["tool1", "tool2"],
            "api_technologies": ["api1", "api2"]
        }}

        Only include technologies that you can confidently identify from the provided information.
        Return only the JSON object, no additional text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean the response to extract JSON
            response_text = response.text.strip()
            
            # Remove markdown code block markers if present
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            
            # Try to parse JSON
            tech_stack = json.loads(response_text)
            return tech_stack
            
        except json.JSONDecodeError:
            # Fallback: create a simple tech stack from available data
            return self._create_fallback_tech_stack(languages, package_files)
        except Exception as e:
            return {"error": f"Failed to detect tech stack: {str(e)}"}
    
    def generate_setup_instructions(self, repo_info: Dict, readme_content: str = None,
                                   package_files: Dict = None, tech_stack: Dict = None) -> str:
        """
        Generate setup and installation instructions for the repository
        
        Args:
            repo_info: Basic repository information
            readme_content: Content of README file
            package_files: Dictionary of package/dependency files
            tech_stack: Detected technology stack
            
        Returns:
            Generated setup instructions
        """
        prompt = f"""
        Generate comprehensive setup and installation instructions for this repository:

        Repository: {repo_info.get('name', 'N/A')}
        Primary Language: {repo_info.get('language', 'N/A')}
        
        {"README Content (first 2000 chars):" if readme_content else ""}
        {readme_content[:2000] if readme_content else "No README available"}
        
        {"Package Files:" if package_files else ""}
        {self._format_package_files(package_files) if package_files else "No package files found"}
        
        {"Detected Tech Stack:" if tech_stack else ""}
        {json.dumps(tech_stack, indent=2) if tech_stack else "No tech stack data"}

        Please provide step-by-step setup instructions including:
        1. Prerequisites and system requirements
        2. Installation steps
        3. Configuration requirements
        4. How to run/start the application
        5. Basic usage examples
        6. Common troubleshooting tips

        Format as clear, numbered steps without markdown headers.
        Be specific about commands and file locations where possible.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Failed to generate setup instructions: {str(e)}"
    
    def analyze_file_structure(self, file_list: List[Dict], repo_info: Dict) -> Dict:
        """
        Analyze and explain the repository file structure
        
        Args:
            file_list: List of files and directories from GitHub API
            repo_info: Basic repository information
            
        Returns:
            Dictionary containing file structure analysis
        """
        # Organize files by type and directory
        structure = {
            "directories": [],
            "important_files": [],
            "config_files": [],
            "documentation": [],
            "source_code": [],
            "tests": [],
            "assets": []
        }
        
        for file_info in file_list[:100]:  # Limit to first 100 files
            file_name = file_info.get('name', '')
            file_type = file_info.get('type', 'file')
            
            if file_type == 'dir':
                structure["directories"].append(file_name)
            else:
                # Categorize files
                lower_name = file_name.lower()
                
                if any(name in lower_name for name in ['readme', 'license', 'changelog', 'contributing']):
                    structure["documentation"].append(file_name)
                elif any(ext in lower_name for ext in ['.config', '.json', '.yml', '.yaml', '.toml', '.ini']):
                    structure["config_files"].append(file_name)
                elif any(name in lower_name for name in ['test', 'spec', '__test__']):
                    structure["tests"].append(file_name)
                elif any(ext in lower_name for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb']):
                    structure["source_code"].append(file_name)
                elif any(ext in lower_name for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']):
                    structure["assets"].append(file_name)
                elif file_name in ['package.json', 'requirements.txt', 'Gemfile', 'pom.xml', 'Cargo.toml']:
                    structure["important_files"].append(file_name)
        
        return structure
    
    def _format_package_files(self, package_files: Dict) -> str:
        """Format package files for prompt inclusion"""
        if not package_files:
            return "No package files found"
        
        formatted = []
        for filename, content in package_files.items():
            # Truncate long content
            truncated_content = content[:500] if len(content) > 500 else content
            formatted.append(f"{filename}:\n{truncated_content}")
        
        return "\n\n".join(formatted)
    
    def _format_file_structure(self, file_list: List[Dict]) -> str:
        """Format file structure for prompt inclusion"""
        formatted = []
        for file_info in file_list:
            name = file_info.get('name', 'Unknown')
            file_type = file_info.get('type', 'file')
            size = file_info.get('size', 0)
            
            if file_type == 'dir':
                formatted.append(f"📁 {name}/")
            else:
                formatted.append(f"📄 {name} ({size} bytes)")
        
        return "\n".join(formatted)
    
    def _create_fallback_tech_stack(self, languages: Dict, package_files: Dict) -> Dict:
        """Create a fallback tech stack when AI analysis fails"""
        tech_stack = {
            "primary_languages": list(languages.keys()) if languages else [],
            "frameworks": [],
            "databases": [],
            "tools_and_services": [],
            "deployment": [],
            "testing": [],
            "build_tools": [],
            "package_managers": [],
            "development_tools": [],
            "api_technologies": []
        }
        
        # Analyze package files for additional info
        if package_files:
            for filename in package_files.keys():
                if filename == 'package.json':
                    tech_stack["package_managers"].append("npm")
                elif filename == 'requirements.txt':
                    tech_stack["package_managers"].append("pip")
                elif filename == 'Gemfile':
                    tech_stack["package_managers"].append("bundler")
                elif filename == 'pom.xml':
                    tech_stack["build_tools"].append("maven")
                elif filename == 'build.gradle':
                    tech_stack["build_tools"].append("gradle")
                elif filename == 'Cargo.toml':
                    tech_stack["package_managers"].append("cargo")
        
        return tech_stack