# Backend Setup Guide

This directory contains the Django backend for the Repo Insight Generator.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

## Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   
   # On Linux/Mac:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp ../.env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   GITHUB_TOKEN=your_github_token_here (optional)
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

## Development

Start the development server:
```bash
python manage.py runserver
```

The API will be available at http://localhost:8000/api/

## Project Structure

```
backend/
├── repo_analyzer/          # Django project settings
│   ├── settings.py        # Configuration
│   ├── urls.py           # URL routing
│   ├── wsgi.py           # WSGI application
│   └── asgi.py           # ASGI application
├── analyzer/              # Main Django app
│   ├── models.py         # Database models
│   ├── views.py          # API views
│   ├── serializers.py    # DRF serializers
│   ├── urls.py           # App URL patterns
│   ├── admin.py          # Django admin
│   └── services/         # Business logic services
│       ├── github_service.py     # GitHub API integration
│       ├── gemini_service.py     # Gemini AI integration
│       ├── repository_analyzer.py # Main analysis logic
│       └── export_service.py     # Export functionality
├── exports/              # Generated export files
├── requirements.txt      # Python dependencies
└── manage.py            # Django management script
```

## API Endpoints

### Analysis Endpoints

- `POST /api/analyze/` - Analyze a repository
  ```json
  {
    "repository_url": "https://github.com/owner/repo"
  }
  ```

- `GET /api/analysis/{id}/` - Get analysis details
- `POST /api/re-analyze/` - Force re-analysis
- `GET /api/analyses/` - List all analyses

### Export Endpoints

- `POST /api/export/{format}/{id}/` - Export analysis
- `GET /api/download/{format}/{id}/` - Download exported file
- `GET /api/analysis/{id}/exports/` - Get all exports for analysis

### Utility Endpoints

- `GET /api/health/` - Health check
- `GET /api/info/` - API information

## Database Models

### RepositoryAnalysis
Stores repository analysis results including:
- Repository metadata (URL, owner, stars, forks)
- Analysis results (summary, tech stack, file structure)
- Status tracking (pending, analyzing, completed, failed)

### ExportFile
Tracks generated export files:
- Associated analysis
- File format and path
- File size and creation date

## Services

### GitHubService
- Fetches repository data using GitHub API
- Handles authentication and rate limiting
- Parses repository structure and metadata

### GeminiService  
- Integrates with Google Gemini Pro API
- Generates AI-powered insights and summaries
- Detects technology stacks and analyzes code

### RepositoryAnalyzerService
- Orchestrates the complete analysis process
- Combines data from GitHub and AI services
- Manages analysis state and error handling

### ExportService
- Generates export files in multiple formats
- Handles file creation and storage
- Manages export metadata

## Configuration

### Environment Variables

Required:
- `GEMINI_API_KEY` - Google Gemini Pro API key
- `SECRET_KEY` - Django secret key

Optional:
- `GITHUB_TOKEN` - GitHub personal access token (for higher rate limits)
- `DEBUG` - Enable debug mode (default: False)
- `CORS_ALLOWED_ORIGINS` - Frontend URLs for CORS

### API Keys Setup

1. **Gemini API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add to `.env` file

2. **GitHub Token** (optional but recommended):
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate new token with `public_repo` scope
   - Add to `.env` file

## Error Handling

The backend implements comprehensive error handling:

- **API Errors**: Structured error responses with meaningful messages
- **Validation**: Input validation for repository URLs and parameters
- **Rate Limiting**: GitHub API rate limit handling
- **Timeouts**: Request timeout management
- **Logging**: Detailed logging for debugging

## Database

The application uses SQLite by default for development. For production:

1. **PostgreSQL** (recommended):
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'repo_insight',
           'USER': 'your_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

2. **MySQL**:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'repo_insight',
           'USER': 'your_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

## Admin Interface

Access the Django admin at http://localhost:8000/admin/ to:
- View and manage repository analyses
- Monitor export files
- Debug analysis issues
- View system statistics

## Testing

Run tests:
```bash
python manage.py test
```

Run with coverage:
```bash
pip install coverage
coverage run manage.py test
coverage report
```

## Production Deployment

### Using Gunicorn + Nginx

1. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```

2. Create Gunicorn configuration:
   ```python
   # gunicorn.conf.py
   bind = "127.0.0.1:8000"
   workers = 4
   worker_class = "sync"
   timeout = 300
   keepalive = 2
   max_requests = 1000
   max_requests_jitter = 100
   ```

3. Start Gunicorn:
   ```bash
   gunicorn repo_analyzer.wsgi:application -c gunicorn.conf.py
   ```

4. Configure Nginx:
   ```nginx
   server {
       listen 80;
       server_name api.your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       location /static/ {
           alias /path/to/staticfiles/;
       }
       
       location /media/ {
           alias /path/to/media/;
       }
   }
   ```

### Using Docker

Create a Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "repo_analyzer.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Monitoring

### Logging
Configure logging in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'repo_analyzer.log',
        },
    },
    'loggers': {
        'analyzer': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Health Checks
Use the `/api/health/` endpoint for monitoring:
- Application status
- Database connectivity
- API dependencies

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Verify Gemini API key is correct
   - Check API key has proper permissions
   - Monitor API usage and quotas

2. **GitHub Rate Limiting**:
   - Add GitHub personal access token
   - Implement request caching
   - Monitor rate limit headers

3. **Database Issues**:
   - Run migrations: `python manage.py migrate`
   - Check database permissions
   - Verify connection settings

4. **Import Errors**:
   - Ensure all dependencies are installed
   - Check Python path
   - Verify virtual environment is active

### Performance Optimization

- Use database indexing for frequent queries
- Implement caching with Redis
- Optimize API request patterns
- Use background tasks for long-running analyses
- Monitor and profile database queries

## Contributing

1. Follow Django best practices
2. Write comprehensive tests
3. Use type hints where appropriate
4. Document API changes
5. Follow PEP 8 style guidelines