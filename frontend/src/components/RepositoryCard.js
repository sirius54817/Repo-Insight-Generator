import React from 'react';
import { Link } from 'react-router-dom';
import StatusBadge from './StatusBadge';

const RepositoryCard = ({ analysis, showActions = true }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatNumber = (num) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  const getTechStackSummary = (techStack) => {
    if (!techStack || typeof techStack !== 'object') return [];
    
    const technologies = [];
    Object.values(techStack).forEach(category => {
      if (Array.isArray(category)) {
        technologies.push(...category);
      }
    });
    
    return technologies.slice(0, 5); // Show first 5 technologies
  };

  const techSummary = getTechStackSummary(analysis.tech_stack);

  return (
    <div className="card animate-fade-in">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {analysis.repository_name}
            </h3>
            <StatusBadge status={analysis.status} />
          </div>
          
          <div className="flex items-center text-sm text-gray-500 space-x-4 mb-2">
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
              {analysis.owner}
            </span>
            
            {analysis.language && (
              <span className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-blue-500 mr-1"></div>
                {analysis.language}
              </span>
            )}
            
            {analysis.stars > 0 && (
              <span className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                {formatNumber(analysis.stars)}
              </span>
            )}
            
            {analysis.forks > 0 && (
              <span className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7.707 3.293a1 1 0 010 1.414L5.414 7H11a7 7 0 017 7v2a1 1 0 11-2 0v-2a5 5 0 00-5-5H5.414l2.293 2.293a1 1 0 11-1.414 1.414L2.586 8l3.707-3.707a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                {formatNumber(analysis.forks)}
              </span>
            )}
          </div>

          <p className="text-gray-600 text-sm line-clamp-2 mb-3">
            {analysis.description || 'No description available'}
          </p>

          {/* Tech Stack Summary */}
          {techSummary.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {techSummary.map((tech, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700"
                >
                  {tech}
                </span>
              ))}
              {Object.values(analysis.tech_stack || {}).flat().length > 5 && (
                <span className="text-xs text-gray-500">
                  +{Object.values(analysis.tech_stack || {}).flat().length - 5} more
                </span>
              )}
            </div>
          )}

          <div className="text-xs text-gray-500">
            Analyzed {formatDate(analysis.created_at)}
          </div>
        </div>
      </div>

      {showActions && (
        <div className="flex justify-between items-center pt-4 border-t border-gray-200">
          <Link
            to={`/analysis/${analysis.id}`}
            className="btn btn-primary btn-sm"
          >
            View Details
          </Link>
          
          <a
            href={analysis.repository_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary btn-sm"
          >
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
            </svg>
            GitHub
          </a>
        </div>
      )}
    </div>
  );
};

export default RepositoryCard;