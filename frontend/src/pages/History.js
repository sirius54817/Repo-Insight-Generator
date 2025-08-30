import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import repositoryApi from '../services/api';
import RepositoryCard from '../components/RepositoryCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { toast } from 'react-toastify';

const History = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, completed, failed, analyzing

  useEffect(() => {
    loadAnalyses();
  }, []);

  const loadAnalyses = async () => {
    try {
      setLoading(true);
      const data = await repositoryApi.listAnalyses();
      setAnalyses(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load analyses:', err);
      setError(err.message || 'Failed to load analysis history');
      toast.error('Failed to load analysis history');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    await loadAnalyses();
    toast.success('History refreshed!');
  };

  const getFilteredAnalyses = () => {
    if (filter === 'all') return analyses;
    return analyses.filter(analysis => analysis.status === filter);
  };

  const getStatusCounts = () => {
    const counts = {
      all: analyses.length,
      completed: 0,
      analyzing: 0,
      failed: 0,
      pending: 0
    };

    analyses.forEach(analysis => {
      counts[analysis.status] = (counts[analysis.status] || 0) + 1;
    });

    return counts;
  };

  const statusCounts = getStatusCounts();
  const filteredAnalyses = getFilteredAnalyses();

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <LoadingSpinner size="lg" message="Loading analysis history..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.962-.833-2.732 0L4.082 20.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <h2 className="text-xl font-semibold mb-2">Error Loading History</h2>
            <p className="text-gray-600 mb-6">{error}</p>
          </div>
          <div className="space-x-3">
            <button onClick={handleRefresh} className="btn btn-primary">
              Try Again
            </button>
            <Link to="/" className="btn btn-secondary">
              Start New Analysis
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Analysis History</h1>
            <p className="text-gray-600">View and manage your repository analyses</p>
          </div>
          
          <div className="flex space-x-3 mt-4 sm:mt-0">
            <button
              onClick={handleRefresh}
              className="btn btn-secondary"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
            
            <Link to="/" className="btn btn-primary">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              New Analysis
            </Link>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { key: 'all', label: 'All', count: statusCounts.all },
              { key: 'completed', label: 'Completed', count: statusCounts.completed },
              { key: 'analyzing', label: 'Analyzing', count: statusCounts.analyzing + statusCounts.pending },
              { key: 'failed', label: 'Failed', count: statusCounts.failed }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key)}
                className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                  filter === tab.key
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
                {tab.count > 0 && (
                  <span className={`ml-2 py-0.5 px-2 rounded-full text-xs ${
                    filter === tab.key
                      ? 'bg-primary-100 text-primary-600'
                      : 'bg-gray-100 text-gray-900'
                  }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      {analyses.length === 0 ? (
        <div className="card text-center py-12">
          <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Analyses Yet</h3>
          <p className="text-gray-600 mb-6">
            You haven't analyzed any repositories yet. Start by analyzing your first repository.
          </p>
          <Link to="/" className="btn btn-primary">
            Analyze Repository
          </Link>
        </div>
      ) : filteredAnalyses.length === 0 ? (
        <div className="card text-center py-12">
          <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Results Found</h3>
          <p className="text-gray-600 mb-6">
            No analyses match the current filter. Try selecting a different filter or analyze a new repository.
          </p>
          <div className="space-x-3">
            <button
              onClick={() => setFilter('all')}
              className="btn btn-secondary"
            >
              Show All
            </button>
            <Link to="/" className="btn btn-primary">
              Analyze Repository
            </Link>
          </div>
        </div>
      ) : (
        <>
          {/* Results Summary */}
          <div className="mb-6">
            <p className="text-sm text-gray-600">
              Showing {filteredAnalyses.length} of {analyses.length} analyses
              {filter !== 'all' && ` (filtered by ${filter})`}
            </p>
          </div>

          {/* Analysis Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAnalyses.map((analysis) => (
              <RepositoryCard
                key={analysis.id}
                analysis={analysis}
                showActions={true}
              />
            ))}
          </div>

          {/* Load More (if needed in the future) */}
          {filteredAnalyses.length >= 50 && (
            <div className="text-center mt-8">
              <p className="text-sm text-gray-500">
                Showing the latest 50 analyses. Older analyses may be available through the API.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default History;