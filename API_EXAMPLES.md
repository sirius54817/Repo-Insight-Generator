# Example API Usage

This document provides examples of how to use the Repo Insight Generator API.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

Currently, no authentication is required for the API endpoints.

## Examples

### 1. Analyze a Repository

**Request:**
```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/facebook/react"
  }'
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "repository_url": "https://github.com/facebook/react",
  "repository_name": "react",
  "owner": "facebook",
  "summary": "React is a JavaScript library for building user interfaces...",
  "tech_stack": {
    "primary_languages": ["JavaScript", "TypeScript"],
    "frameworks": ["React", "Jest"],
    "build_tools": ["Webpack", "Rollup"],
    "testing": ["Jest", "React Testing Library"]
  },
  "file_structure": {
    "total_files": 1250,
    "languages": {
      "JavaScript": 1500000,
      "TypeScript": 800000
    }
  },
  "setup_instructions": "1. Clone the repository...",
  "status": "completed",
  "stars": 200000,
  "forks": 40000,
  "language": "JavaScript",
  "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces.",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### 2. Get Analysis Results

**Request:**
```bash
curl http://localhost:8000/api/analysis/123e4567-e89b-12d3-a456-426614174000/
```

### 3. Export Analysis

**Request:**
```bash
curl -X POST http://localhost:8000/api/export/pdf/123e4567-e89b-12d3-a456-426614174000/
```

**Response:**
```json
{
  "id": "456e7890-e12c-34d5-b678-537625285111",
  "format": "pdf",
  "file_size": 245760,
  "download_url": "http://localhost:8000/api/download/pdf/123e4567-e89b-12d3-a456-426614174000/",
  "created_at": "2024-01-15T10:40:00Z"
}
```

### 4. Download Exported File

**Request:**
```bash
curl -O http://localhost:8000/api/download/pdf/123e4567-e89b-12d3-a456-426614174000/
```

### 5. List All Analyses

**Request:**
```bash
curl http://localhost:8000/api/analyses/
```

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "repository_name": "react",
    "owner": "facebook",
    "status": "completed",
    "created_at": "2024-01-15T10:30:00Z",
    "stars": 200000,
    "forks": 40000
  }
]
```

### 6. Health Check

**Request:**
```bash
curl http://localhost:8000/api/health/
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Repo Insight Generator API is running"
}
```

### 7. API Information

**Request:**
```bash
curl http://localhost:8000/api/info/
```

**Response:**
```json
{
  "name": "Repo Insight Generator API",
  "version": "1.0.0",
  "description": "Analyze GitHub repositories with AI-powered insights",
  "endpoints": {
    "analyze": "/api/analyze/",
    "get_analysis": "/api/analysis/{id}/",
    "export": "/api/export/{format}/{id}/",
    "download": "/api/download/{format}/{id}/",
    "list_analyses": "/api/analyses/",
    "health": "/api/health/"
  },
  "supported_formats": ["md", "txt", "pdf", "docx"]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid repository URL",
  "message": "Please provide a valid GitHub repository URL"
}
```

### 404 Not Found
```json
{
  "error": "Analysis not found",
  "message": "No analysis found with the provided ID"
}
```

### 500 Internal Server Error
```json
{
  "error": "Analysis failed",
  "message": "Failed to fetch repository information from GitHub"
}
```

## Python Client Example

```python
import requests
import json

# Analyze a repository
def analyze_repository(repo_url):
    response = requests.post(
        'http://localhost:8000/api/analyze/',
        json={'repository_url': repo_url}
    )
    return response.json()

# Get analysis results
def get_analysis(analysis_id):
    response = requests.get(f'http://localhost:8000/api/analysis/{analysis_id}/')
    return response.json()

# Export analysis
def export_analysis(analysis_id, format_type):
    response = requests.post(f'http://localhost:8000/api/export/{format_type}/{analysis_id}/')
    return response.json()

# Download file
def download_file(analysis_id, format_type, filename):
    response = requests.get(f'http://localhost:8000/api/download/{format_type}/{analysis_id}/')
    
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    return False

# Example usage
if __name__ == "__main__":
    # Analyze React repository
    result = analyze_repository("https://github.com/facebook/react")
    analysis_id = result['id']
    
    print(f"Analysis ID: {analysis_id}")
    print(f"Status: {result['status']}")
    
    # Wait for completion (in real app, you'd poll or use webhooks)
    if result['status'] == 'completed':
        # Export as PDF
        export_result = export_analysis(analysis_id, 'pdf')
        print(f"Export created: {export_result['download_url']}")
        
        # Download the file
        if download_file(analysis_id, 'pdf', 'react_analysis.pdf'):
            print("File downloaded successfully!")
```

## JavaScript Client Example

```javascript
class RepoInsightClient {
  constructor(baseUrl = 'http://localhost:8000/api') {
    this.baseUrl = baseUrl;
  }

  async analyzeRepository(repositoryUrl) {
    const response = await fetch(`${this.baseUrl}/analyze/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ repository_url: repositoryUrl }),
    });
    return response.json();
  }

  async getAnalysis(analysisId) {
    const response = await fetch(`${this.baseUrl}/analysis/${analysisId}/`);
    return response.json();
  }

  async exportAnalysis(analysisId, format) {
    const response = await fetch(`${this.baseUrl}/export/${format}/${analysisId}/`, {
      method: 'POST',
    });
    return response.json();
  }

  getDownloadUrl(analysisId, format) {
    return `${this.baseUrl}/download/${format}/${analysisId}/`;
  }

  async listAnalyses() {
    const response = await fetch(`${this.baseUrl}/analyses/`);
    return response.json();
  }
}

// Example usage
const client = new RepoInsightClient();

async function main() {
  try {
    // Analyze a repository
    const analysis = await client.analyzeRepository('https://github.com/microsoft/vscode');
    console.log('Analysis started:', analysis.id);

    // Poll for completion (simplified example)
    let result = analysis;
    while (result.status === 'analyzing' || result.status === 'pending') {
      await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
      result = await client.getAnalysis(analysis.id);
      console.log('Status:', result.status);
    }

    if (result.status === 'completed') {
      console.log('Analysis completed!');
      console.log('Summary:', result.summary);

      // Export as Markdown
      const exportResult = await client.exportAnalysis(result.id, 'md');
      console.log('Export URL:', exportResult.download_url);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

main();
```