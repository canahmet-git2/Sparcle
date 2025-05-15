import React from 'react';
import './TitleBar.css';

const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;

interface TitleBarProps {
  title: string;
}

export const TitleBar: React.FC<TitleBarProps> = ({ title }) => {
  const handleMinimize = () => {
    (window as any).electron?.ipcRenderer.send('window-minimize');
  };

  const handleMaximize = () => {
    (window as any).electron?.ipcRenderer.send('window-maximize');
  };

  const handleClose = () => {
    (window as any).electron?.ipcRenderer.send('window-close');
  };

  return (
    <div className={`title-bar ${isMac ? 'mac' : 'windows'}`}>
      {!isMac && (
        <div className="window-controls left">
          <div className="window-icon">
            <img src="/icon.png" alt="Sparcle" />
          </div>
        </div>
      )}
      <div className="title">{title}</div>
      {!isMac && (
        <div className="window-controls right">
          <button className="control minimize" onClick={handleMinimize}>
            <svg width="10" height="1" viewBox="0 0 10 1">
              <path d="M0 0h10v1H0z" fill="currentColor" />
            </svg>
          </button>
          <button className="control maximize" onClick={handleMaximize}>
            <svg width="10" height="10" viewBox="0 0 10 10">
              <path d="M0 0h10v10H0V0zm1 1v8h8V1H1z" fill="currentColor" />
            </svg>
          </button>
          <button className="control close" onClick={handleClose}>
            <svg width="10" height="10" viewBox="0 0 10 10">
              <path d="M1 0L0 1l4 4-4 4 1 1 4-4 4 4 1-1-4-4 4-4-1-1-4 4-4-4z" fill="currentColor" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}; 