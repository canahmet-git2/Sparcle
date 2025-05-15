import React, { useState, useEffect } from 'react';
import { errorLogger } from '../../utils/errorLogger';

interface ErrorDisplayProps {
  maxErrors?: number;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ maxErrors = 5 }) => {
  const [errors, setErrors] = useState<Array<{
    timestamp: string;
    type: string;
    message: string;
    componentName?: string;
  }>>([]);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    // Update errors every second
    const interval = setInterval(() => {
      setErrors(errorLogger.getRecentErrors(maxErrors));
    }, 1000);

    return () => clearInterval(interval);
  }, [maxErrors]);

  if (errors.length === 0) return null;

  return (
    <div className="error-display" style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      maxWidth: '400px',
      backgroundColor: '#ff000015',
      border: '1px solid #ff0000',
      borderRadius: '4px',
      padding: '10px',
      color: '#ff0000',
      fontFamily: 'monospace',
      fontSize: '12px',
      zIndex: 9999,
      maxHeight: isExpanded ? '80vh' : '100px',
      overflow: 'hidden',
      transition: 'max-height 0.3s ease-in-out'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '10px'
      }}>
        <h4 style={{ margin: 0 }}>Recent Errors ({errors.length})</h4>
        <div>
          <button
            onClick={() => errorLogger.clearErrors()}
            style={{
              background: 'none',
              border: '1px solid #ff0000',
              color: '#ff0000',
              marginRight: '5px',
              cursor: 'pointer',
              padding: '2px 5px',
              borderRadius: '3px'
            }}
          >
            Clear
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            style={{
              background: 'none',
              border: '1px solid #ff0000',
              color: '#ff0000',
              cursor: 'pointer',
              padding: '2px 5px',
              borderRadius: '3px'
            }}
          >
            {isExpanded ? 'Collapse' : 'Expand'}
          </button>
        </div>
      </div>
      <div style={{
        overflowY: 'auto',
        maxHeight: isExpanded ? 'calc(80vh - 40px)' : '60px'
      }}>
        {errors.map((error, index) => (
          <div
            key={error.timestamp + index}
            style={{
              marginBottom: '10px',
              padding: '5px',
              borderBottom: index < errors.length - 1 ? '1px solid #ff000050' : 'none'
            }}
          >
            <div style={{ fontSize: '10px', opacity: 0.8 }}>
              [{new Date(error.timestamp).toLocaleTimeString()}]
              {error.componentName && ` - ${error.componentName}`}
              {error.type && ` (${error.type})`}
            </div>
            <div style={{ marginTop: '3px' }}>{error.message}</div>
          </div>
        ))}
      </div>
    </div>
  );
}; 