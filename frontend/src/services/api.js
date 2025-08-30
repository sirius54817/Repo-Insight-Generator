import axios from 'axios';
import { toast } from 'react-toastify';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 60000, // 60 seconds timeout for analysis requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed in the future
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.code === 'ECONNABORTED') {
      toast.error('Request timed out. Please try again.');
    } else if (error.response?.status === 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.response?.data?.message) {
      // Use server-provided error message
      toast.error(error.response.data.message);
    } else {
      toast.error('An unexpected error occurred.');
    }
    
    return Promise.reject(error);
  }
);

/**
 * API Service for Repository Analysis
 */
class RepositoryApiService {
  /**
   * Analyze a GitHub repository
   * @param {string} repositoryUrl - GitHub repository URL
   * @returns {Promise<Object>} Analysis result
   */
  async analyzeRepository(repositoryUrl) {
    try {
      const response = await api.post('/analyze/', {
        repository_url: repositoryUrl
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Force re-analysis of a repository
   * @param {string} repositoryUrl - GitHub repository URL
   * @returns {Promise<Object>} Analysis result
   */
  async reAnalyzeRepository(repositoryUrl) {
    try {
      const response = await api.post('/re-analyze/', {
        repository_url: repositoryUrl
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Get analysis by ID
   * @param {string} analysisId - Analysis UUID
   * @returns {Promise<Object>} Analysis data
   */
  async getAnalysis(analysisId) {
    try {
      const response = await api.get(`/analysis/${analysisId}/`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * List all analyses
   * @returns {Promise<Array>} List of analyses
   */
  async listAnalyses() {
    try {
      const response = await api.get('/analyses/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Export analysis to specified format
   * @param {string} analysisId - Analysis UUID
   * @param {string} format - Export format (md, txt, pdf, docx)
   * @returns {Promise<Object>} Export file info
   */
  async exportAnalysis(analysisId, format) {
    try {
      const response = await api.post(`/export/${format}/${analysisId}/`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Get download URL for exported file
   * @param {string} analysisId - Analysis UUID
   * @param {string} format - Export format
   * @returns {string} Download URL
   */
  getDownloadUrl(analysisId, format) {
    const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    return `${baseUrl}/download/${format}/${analysisId}/`;
  }

  /**
   * Download exported file
   * @param {string} analysisId - Analysis UUID
   * @param {string} format - Export format
   * @param {string} filename - Desired filename
   */
  async downloadFile(analysisId, format, filename) {
    try {
      const downloadUrl = this.getDownloadUrl(analysisId, format);
      
      // Create a temporary link element to trigger download
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename || `analysis.${format}`;
      link.target = '_blank';
      
      // Append to body, click, and remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.success(`${format.toUpperCase()} file download started!`);
    } catch (error) {
      toast.error('Failed to download file');
      throw error;
    }
  }

  /**
   * Get all exports for an analysis
   * @param {string} analysisId - Analysis UUID
   * @returns {Promise<Array>} List of export files
   */
  async getAnalysisExports(analysisId) {
    try {
      const response = await api.get(`/analysis/${analysisId}/exports/`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  async healthCheck() {
    try {
      const response = await api.get('/health/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Get API information
   * @returns {Promise<Object>} API info
   */
  async getApiInfo() {
    try {
      const response = await api.get('/info/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Handle API errors consistently
   * @param {Error} error - Axios error object
   * @returns {Object} Normalized error object
   */
  handleError(error) {
    if (error.response) {
      // Server responded with error status
      return {
        message: error.response.data?.message || 'Server error occurred',
        status: error.response.status,
        data: error.response.data
      };
    } else if (error.request) {
      // Request was made but no response received
      return {
        message: 'Network error - please check your connection',
        status: 0,
        data: null
      };
    } else {
      // Something else happened
      return {
        message: error.message || 'An unexpected error occurred',
        status: 0,
        data: null
      };
    }
  }

  /**
   * Validate GitHub URL
   * @param {string} url - URL to validate
   * @returns {boolean} Whether URL is valid GitHub repo URL
   */
  validateGitHubUrl(url) {
    if (!url || typeof url !== 'string') return false;
    
    const githubPatterns = [
      /^https?:\/\/github\.com\/[\w\-._]+\/[\w\-._]+\/?$/,
      /^https?:\/\/github\.com\/[\w\-._]+\/[\w\-._]+\.git\/?$/,
    ];
    
    return githubPatterns.some(pattern => pattern.test(url.trim()));
  }

  /**
   * Extract owner and repo name from GitHub URL
   * @param {string} url - GitHub repository URL
   * @returns {Object} Object with owner and repo properties
   */
  parseGitHubUrl(url) {
    if (!this.validateGitHubUrl(url)) {
      throw new Error('Invalid GitHub repository URL');
    }
    
    const cleanUrl = url.trim().replace(/\.git$/, '').replace(/\/$/, '');
    const parts = cleanUrl.split('/');
    
    return {
      owner: parts[parts.length - 2],
      repo: parts[parts.length - 1]
    };
  }
}

// Create and export singleton instance
const repositoryApi = new RepositoryApiService();
export default repositoryApi;