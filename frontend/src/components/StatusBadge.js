import React from 'react';

const StatusBadge = ({ status }) => {
  const getStatusConfig = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return {
          className: 'badge badge-success',
          text: 'Completed',
          icon: '✓'
        };
      case 'analyzing':
        return {
          className: 'badge badge-warning',
          text: 'Analyzing',
          icon: '⚡'
        };
      case 'pending':
        return {
          className: 'badge badge-gray',
          text: 'Pending',
          icon: '⏳'
        };
      case 'failed':
        return {
          className: 'badge badge-danger',
          text: 'Failed',
          icon: '✗'
        };
      default:
        return {
          className: 'badge badge-gray',
          text: status || 'Unknown',
          icon: '?'
        };
    }
  };

  const config = getStatusConfig(status);

  return (
    <span className={config.className}>
      <span className="mr-1" aria-hidden="true">{config.icon}</span>
      {config.text}
    </span>
  );
};

export default StatusBadge;