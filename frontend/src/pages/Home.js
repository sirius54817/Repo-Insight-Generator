import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import repositoryApi from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const Home = () => {
  const [repositoryUrl, setRepositoryUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const validateUrl = (url) => {
    if (!url.trim()) {
      return 'Please enter a repository URL';
    }
    
    if (!repositoryApi.validateGitHubUrl(url)) {
      return 'Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)';
    }
    
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateUrl(repositoryUrl);
    if (validationError) {
      setError(validationError);
      return;
    }
    
    setError('');
    setIsAnalyzing(true);

    try {
      const analysis = await repositoryApi.analyzeRepository(repositoryUrl.trim());
      
      if (analysis.status === 'completed') {
        toast.success('Repository analysis completed!');
        navigate(`/analysis/${analysis.id}`);
      } else if (analysis.status === 'analyzing') {
        toast.info('Analysis is in progress. Redirecting to results page...');
        navigate(`/analysis/${analysis.id}`);
      } else if (analysis.status === 'failed') {
        toast.error(analysis.error_message || 'Analysis failed');
        setError(analysis.error_message || 'Analysis failed');
      } else {
        toast.info('Analysis started. Redirecting to results page...');
        navigate(`/analysis/${analysis.id}`);
      }
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'Failed to analyze repository');
      toast.error('Failed to analyze repository');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUrlChange = (e) => {
    setRepositoryUrl(e.target.value);
    if (error) setError(''); // Clear error when user starts typing
  };

  const exampleRepos = [
    'https://github.com/facebook/react',
    'https://github.com/microsoft/vscode',
    'https://github.com/django/django',
    'https://github.com/nodejs/node'
  ];

  const handleExampleClick = (url) => {
    setRepositoryUrl(url);
    setError('');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Analyze GitHub Repositories with AI
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Get comprehensive insights, tech stack analysis, and setup instructions 
          for any GitHub repository using advanced AI technology.
        </p>
      </div>

      {/* Main Analysis Form */}
      <div className="card max-w-2xl mx-auto mb-12">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="repository-url" className="label">
              GitHub Repository URL
            </label>
            <div className="mt-1">
              <input
                id="repository-url"
                type="url"
                value={repositoryUrl}
                onChange={handleUrlChange}
                placeholder="https://github.com/owner/repository"
                className={`input-field ${error ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}`}
                disabled={isAnalyzing}
                autoFocus
              />
            </div>
            {error && (
              <p className="error-text">{error}</p>
            )}
            <p className="mt-2 text-sm text-gray-500">
              Enter the URL of any public GitHub repository to get started
            </p>
          </div>

          <button
            type="submit"
            disabled={isAnalyzing || !repositoryUrl.trim()}
            className={`btn btn-primary btn-lg w-full ${
              isAnalyzing || !repositoryUrl.trim() ? 'btn-disabled' : ''
            }`}
          >
            {isAnalyzing ? (
              <>
                <span className="loading-spinner mr-3"></span>
                Analyzing Repository...
              </>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Analyze Repository
              </>
            )}
          </button>
        </form>

        {/* Example repositories */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-900 mb-3">Try these examples:</p>
          <div className="flex flex-wrap gap-2">
            {exampleRepos.map((url) => {
              const repoName = url.split('/').slice(-2).join('/');
              return (
                <button
                  key={url}
                  onClick={() => handleExampleClick(url)}
                  className="btn btn-secondary btn-sm"
                  disabled={isAnalyzing}
                >
                  {repoName}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isAnalyzing && (
        <div className="card max-w-2xl mx-auto">
          <LoadingSpinner 
            size="lg" 
            message="Analyzing repository... This may take a few moments."
          />
          <div className="text-center mt-4">
            <p className="text-sm text-gray-600 mb-2">
              We're fetching repository data and generating insights using AI
            </p>
            <div className="text-xs text-gray-500 space-y-1">
              <div>• Fetching repository structure and metadata</div>
              <div>• Analyzing technology stack and dependencies</div>
              <div>• Generating comprehensive summary and insights</div>
              <div>• Creating setup and installation instructions</div>
            </div>
          </div>
        </div>
      )}

      {/* Features Section */}
      {!isAnalyzing && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          <div className="text-center">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Analysis</h3>
            <p className="text-gray-600 text-sm">
              Uses Google Gemini Pro to provide intelligent insights and comprehensive repository understanding.
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14-7H3a2 2 0 00-2 2v14c0 1.1.9 2 2 2h16a2 2 0 002-2V6a2 2 0 00-2-2zM9 7h1m4 0h1m-6 4h1m4 0h1m-6 4h1m4 0h1" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Tech Stack Detection</h3>
            <p className="text-gray-600 text-sm">
              Automatically identifies programming languages, frameworks, databases, and tools used in the project.
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Multiple Export Formats</h3>
            <p className="text-gray-600 text-sm">
              Export your analysis as Markdown, Text, PDF, or Word documents for easy sharing and documentation.
            </p>
          </div>
        </div>
      )}

      {/* Additional Info */}
      {!isAnalyzing && (
        <div className="bg-gray-50 rounded-lg p-6 text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">How it works</h3>
          <div className="text-sm text-gray-600 max-w-3xl mx-auto">
            <p className="mb-3">
              Our AI analyzes your GitHub repository by examining its structure, dependencies, 
              documentation, and code patterns to provide comprehensive insights.
            </p>
            <div className="grid md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="font-medium text-primary-600">1. Fetch</div>
                <div>Repository data from GitHub</div>
              </div>
              <div>
                <div className="font-medium text-primary-600">2. Analyze</div>
                <div>Structure and dependencies</div>
              </div>
              <div>
                <div className="font-medium text-primary-600">3. Generate</div>
                <div>AI-powered insights</div>
              </div>
              <div>
                <div className="font-medium text-primary-600">4. Export</div>
                <div>Multiple format options</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;