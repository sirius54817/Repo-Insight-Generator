import React from 'react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">About Repo Insight</h3>
            <p className="text-sm text-gray-600">
              AI-powered GitHub repository analysis tool that provides comprehensive insights, 
              tech stack detection, and setup instructions using advanced AI technology.
            </p>
          </div>

          {/* Features */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Features</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Repository Analysis</li>
              <li>• Tech Stack Detection</li>
              <li>• Setup Instructions</li>
              <li>• Multiple Export Formats</li>
            </ul>
          </div>

          {/* Tech Stack */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Built With</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Django (Backend)</li>
              <li>• React (Frontend)</li>
              <li>• Google Gemini Pro AI</li>
              <li>• GitHub API</li>
            </ul>
          </div>
        </div>

        {/* Bottom section */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-500">
              © {currentYear} Repo Insight Generator. Built with ❤️ for developers.
            </p>
            <div className="flex space-x-4 mt-4 md:mt-0">
              <span className="text-sm text-gray-500">
                Powered by Gemini Pro API
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;