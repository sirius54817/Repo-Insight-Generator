import React from 'react';
import repositoryApi from '../services/api';
import { toast } from 'react-toastify';

const ExportButton = ({ analysisId, analysis, format, className = '' }) => {
  const [isExporting, setIsExporting] = React.useState(false);

  const formatConfig = {
    md: {
      name: 'Markdown',
      icon: '📝',
      extension: 'md',
      description: 'Markdown format for documentation'
    },
    txt: {
      name: 'Text',
      icon: '📄',
      extension: 'txt',
      description: 'Plain text format'
    },
    pdf: {
      name: 'PDF',
      icon: '📋',
      extension: 'pdf',
      description: 'PDF document'
    },
    docx: {
      name: 'Word',
      icon: '📘',
      extension: 'docx',
      description: 'Microsoft Word document'
    }
  };

  const config = formatConfig[format] || {
    name: format.toUpperCase(),
    icon: '📎',
    extension: format,
    description: `${format.toUpperCase()} format`
  };

  const handleExport = async () => {
    if (!analysisId || isExporting) return;

    setIsExporting(true);
    try {
      // First export the analysis
      await repositoryApi.exportAnalysis(analysisId, format);
      
      // Then download it
      const filename = `${analysis?.repository_name || 'analysis'}_${analysis?.owner || 'repo'}_analysis.${config.extension}`;
      await repositoryApi.downloadFile(analysisId, format, filename);
      
      toast.success(`${config.name} export completed!`);
    } catch (error) {
      console.error(`Export failed for ${format}:`, error);
      toast.error(`Failed to export ${config.name} file`);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={isExporting || !analysis || analysis.status !== 'completed'}
      className={`btn btn-secondary ${className} ${
        (isExporting || !analysis || analysis.status !== 'completed') ? 'btn-disabled' : ''
      }`}
      title={config.description}
    >
      <span className="mr-2" aria-hidden="true">{config.icon}</span>
      {isExporting ? (
        <>
          <span className="loading-spinner mr-2"></span>
          Exporting...
        </>
      ) : (
        config.name
      )}
    </button>
  );
};

const ExportButtons = ({ analysisId, analysis, className = '' }) => {
  const formats = ['md', 'txt', 'pdf', 'docx'];

  if (!analysis || analysis.status !== 'completed') {
    return (
      <div className={`text-center py-4 ${className}`}>
        <p className="text-gray-500 text-sm">
          {!analysis 
            ? 'No analysis available' 
            : 'Export will be available once analysis is completed'
          }
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Export Analysis</h3>
        <span className="text-sm text-gray-500">
          Choose your preferred format
        </span>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {formats.map((format) => (
          <ExportButton
            key={format}
            analysisId={analysisId}
            analysis={analysis}
            format={format}
            className="w-full justify-center"
          />
        ))}
      </div>
      
      <div className="text-xs text-gray-500 mt-3">
        <p>
          • <strong>Markdown:</strong> Perfect for GitHub README or documentation<br/>
          • <strong>Text:</strong> Simple plain text format<br/>
          • <strong>PDF:</strong> Professional document with formatting<br/>
          • <strong>Word:</strong> Editable Microsoft Word document
        </p>
      </div>
    </div>
  );
};

export { ExportButton, ExportButtons };