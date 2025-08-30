# Repo Insight Generator

A full-stack application that analyzes GitHub repositories using AI and generates comprehensive insights including summaries, tech stack detection, and setup instructions.

## Features

- 🔍 **Repository Analysis**: Automatically analyze any GitHub repository
- 🤖 **AI-Powered Insights**: Uses Google Gemini Pro for intelligent analysis
- 📊 **Tech Stack Detection**: Automatically detect languages, frameworks, and dependencies
- 📄 **Multiple Export Formats**: Export results as MD, TXT, PDF, and DOCX
- 🎨 **Modern UI**: Clean React frontend with intuitive design

## Tech Stack

### Backend
- **Django** (Python web framework)
- **Django REST Framework** (API development)
- **Google Gemini Pro API** (AI analysis)
- **GitHub API** (Repository data fetching)
- **ReportLab** (PDF generation)
- **python-docx** (DOCX generation)

### Frontend
- **React** (User interface)
- **Axios** (HTTP client)
- **Material-UI** or **Tailwind CSS** (Styling)

## Project Structure

```
repo-insight-generator/
├── backend/                    # Django backend
│   ├── repo_analyzer/         # Django project
│   ├── analyzer/              # Main app
│   ├── requirements.txt       # Python dependencies
│   └── manage.py             # Django management
├── frontend/                  # React frontend
│   ├── public/               # Static files
│   ├── src/                  # React components
│   ├── package.json          # Node dependencies
│   └── README.md             # Frontend setup
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd repo-insight-generator

# Copy environment variables
cp .env.example .env
```

### 2. Configure API Keys

Edit `.env` and add your API keys:
```env
# Required: Get from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=AIzaSyDaZlI64SjY8Ta0IKD-r2sExulEEnCHBPk

# Optional: GitHub token for higher rate limits
GITHUB_TOKEN=your_github_token_here

# Django settings
SECRET_KEY=your_secret_key_here
DEBUG=True
```

### 3. Backend Setup (Terminal 1)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Start Django server
python manage.py runserver
```

Backend will be available at: http://localhost:8000

### 4. Frontend Setup (Terminal 2)

```bash
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install

# Start React development server
npm start
```

Frontend will be available at: http://localhost:3000

### 5. Test the Application

1. Open http://localhost:3000 in your browser
2. Enter a GitHub repository URL (e.g., `https://github.com/facebook/react`)
3. Click "Analyze Repository"
4. Wait for the analysis to complete
5. View results and export in different formats

## Usage

1. Open your browser and go to `http://localhost:3000`
2. Paste a GitHub repository URL
3. Click "Analyze Repository"
4. View the generated insights
5. Download results in your preferred format

## API Endpoints

- `POST /api/analyze/` - Analyze a repository
- `GET /api/download/{format}/{analysis_id}/` - Download analysis results

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.# Repo-Insight-Generator
