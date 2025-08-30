import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import repositoryApi from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import StatusBadge from '../components/StatusBadge';
import { ExportButtons } from '../components/ExportButtons';
import { toast } from 'react-toastify';

const AnalysisResult = () => {
  const { analysisId } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAnalysis();
    
    // Set up polling for ongoing analysis
    let pollInterval;
    if (analysis && (analysis.status === 'pending' || analysis.status === 'analyzing')) {
      pollInterval = setInterval(loadAnalysis, 5000); // Poll every 5 seconds
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [analysisId, analysis?.status]);

  const loadAnalysis = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      const data = await repositoryApi.getAnalysis(analysisId);
      setAnalysis(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load analysis:', err);
      setError(err.message || 'Failed to load analysis');
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadAnalysis(false);
    setRefreshing(false);
    toast.success('Analysis refreshed!');
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderTechStack = (techStack) => {
    if (!techStack || typeof techStack !== 'object') {
      return <p className="text-gray-500">No technology stack information available.</p>;
    }

    const categories = Object.entries(techStack).filter(([, technologies]) => 
      Array.isArray(technologies) && technologies.length > 0
    );

    if (categories.length === 0) {
      return <p className="text-gray-500">No technology stack information available.</p>;
    }

    return (
      <div className="space-y-4">
        {categories.map(([category, technologies]) => (
          <div key={category}>
            <h4 className="font-medium text-gray-900 mb-2 capitalize">
              {category.replace('_', ' ')}
            </h4>
            <div className="flex flex-wrap gap-2">
              {technologies.map((tech, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderFileStructure = (fileStructure) => {
    if (!fileStructure || typeof fileStructure !== 'object') {
      return <p className="text-gray-500">No file structure information available.</p>;
    }

    const { languages, total_files, analysis: fileAnalysis } = fileStructure;

    return (
      <div className="space-y-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {total_files && (
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-gray-900">{total_files}</div>
              <div className="text-sm text-gray-500">Total Files</div>
            </div>
          )}
          
          {languages && Object.keys(languages).length > 0 && (
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-gray-900">{Object.keys(languages).length}</div>
              <div className="text-sm text-gray-500">Languages</div>
            </div>
          )}
        </div>

        {/* Programming Languages */}
        {languages && Object.keys(languages).length > 0 && (
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Programming Languages</h4>
            <div className="space-y-2">
              {Object.entries(languages)
                .sort(([, a], [, b]) => b - a) // Sort by bytes (descending)
                .slice(0, 10) // Show top 10
                .map(([language, bytes]) => {
                  const totalBytes = Object.values(languages).reduce((sum, b) => sum + b, 0);
                  const percentage = ((bytes / totalBytes) * 100).toFixed(1);
                  
                  return (
                    <div key={language} className="flex items-center space-x-3">
                      <div className="flex-1">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium text-gray-700">{language}</span>
                          <span className="text-xs text-gray-500">{percentage}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        )}

        {/* File Categories */}
        {fileAnalysis && (
          <div>
            <h4 className="font-medium text-gray-900 mb-3">File Categories</h4>
            <div className="grid md:grid-cols-2 gap-4">
              {Object.entries(fileAnalysis)
                .filter(([, files]) => Array.isArray(files) && files.length > 0)
                .map(([category, files]) => (
                  <div key={category} className="bg-gray-50 rounded-lg p-3">
                    <h5 className="font-medium text-gray-900 mb-2 capitalize">
                      {category.replace('_', ' ')} ({files.length})
                    </h5>
                    <div className="text-sm text-gray-600">
                      {files.slice(0, 5).map((file, index) => (
                        <div key={index} className="truncate">{file}</div>
                      ))}
                      {files.length > 5 && (
                        <div className="text-gray-500 italic">
                          ... and {files.length - 5} more
                        </div>
                      )}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <LoadingSpinner size="lg" message="Loading analysis results..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.962-.833-2.732 0L4.082 20.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <h2 className="text-xl font-semibold mb-2">Analysis Not Found</h2>
            <p className="text-gray-600 mb-6">{error}</p>
          </div>
          <Link to="/" className="btn btn-primary">
            Start New Analysis
          </Link>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Analysis Not Found</h2>
          <Link to="/" className="btn btn-primary">
            Start New Analysis
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {analysis.repository_name}
            </h1>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                </svg>
                {analysis.owner}
              </span>
              <StatusBadge status={analysis.status} />
              <span>Analyzed {formatDate(analysis.created_at)}</span>
            </div>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="btn btn-secondary"
            >
              {refreshing ? (
                <>
                  <span className="loading-spinner mr-2"></span>
                  Refreshing...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh
                </>
              )}
            </button>
            
            <a
              href={analysis.repository_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary"
            >
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
              </svg>
              View on GitHub
            </a>
          </div>
        </div>

        {/* Repository Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-gray-900">{analysis.stars || 0}</div>
            <div className="text-sm text-gray-500">Stars</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-gray-900">{analysis.forks || 0}</div>
            <div className="text-sm text-gray-500">Forks</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-gray-900">{analysis.language || 'N/A'}</div>
            <div className="text-sm text-gray-500">Language</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-gray-900">
              {analysis.file_structure?.total_files || 'N/A'}
            </div>
            <div className="text-sm text-gray-500">Files</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-gray-900">
              {analysis.file_structure?.languages ? Object.keys(analysis.file_structure.languages).length : 'N/A'}
            </div>
            <div className="text-sm text-gray-500">Languages</div>
          </div>
        </div>

        {analysis.description && (
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
            <p className="text-blue-800">{analysis.description}</p>
          </div>
        )}
      </div>

      {/* Content */}
      {analysis.status === 'analyzing' || analysis.status === 'pending' ? (
        <div className="card text-center">
          <LoadingSpinner size="lg" message="Analysis in progress..." />
          <p className="text-gray-600 mt-4">
            Please wait while we analyze the repository. This page will automatically refresh when complete.
          </p>
        </div>
      ) : analysis.status === 'failed' ? (
        <div className="card text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.962-.833-2.732 0L4.082 20.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <h2 className="text-xl font-semibold mb-2">Analysis Failed</h2>
            <p className="text-gray-600 mb-6">
              {analysis.error_message || 'An error occurred during analysis.'}
            </p>
          </div>
          <Link to="/" className="btn btn-primary">
            Try Another Repository
          </Link>
        </div>
      ) : (
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Summary */}
            {analysis.summary && (
              <div className="card">
                <div className="card-header">
                  <h2 className="text-xl font-semibold text-gray-900">Summary</h2>
                </div>
                <div className="prose max-w-none text-gray-700">
                  {analysis.summary.split('\n').map((paragraph, index) => (
                    <p key={index} className="mb-3">{paragraph}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Setup Instructions */}
            {analysis.setup_instructions && (
              <div className="card">
                <div className="card-header">
                  <h2 className="text-xl font-semibold text-gray-900">Setup Instructions</h2>
                </div>
                <div className="prose max-w-none text-gray-700">
                  <pre className="whitespace-pre-wrap bg-gray-50 rounded-lg p-4 text-sm overflow-x-auto">
                    {analysis.setup_instructions}
                  </pre>
                </div>
              </div>
            )}

            {/* File Structure */}
            {analysis.file_structure && (
              <div className="card">
                <div className="card-header">
                  <h2 className="text-xl font-semibold text-gray-900">File Structure Analysis</h2>
                </div>
                {renderFileStructure(analysis.file_structure)}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Technology Stack */}
            {analysis.tech_stack && (
              <div className="card">
                <div className="card-header">
                  <h2 className="text-lg font-semibold text-gray-900">Technology Stack</h2>
                </div>
                {renderTechStack(analysis.tech_stack)}
              </div>
            )}

            {/* Export Options */}
            <div className="card">
              <ExportButtons analysisId={analysisId} analysis={analysis} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResult;