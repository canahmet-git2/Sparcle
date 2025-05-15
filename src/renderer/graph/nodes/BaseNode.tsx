import React from 'react';

export interface BaseNodeProps {
  title: string;
  color?: string;
  data: any;
  selected?: boolean;
  inputs?: Array<{id: string, socket: any}>;
  outputs?: Array<{id: string, socket: any}>;
  children?: React.ReactNode;
}

export const BaseNode: React.FC<BaseNodeProps> = ({ 
  title, 
  color = '#2d2d2d',
  children,
  selected,
}) => {
  return (
    <div 
      className={`node ${selected ? 'selected' : ''}`}
      style={{
        backgroundColor: color,
        borderColor: selected ? '#fff' : '#3d3d3d'
      }}
    >
      <div className="node-header">
        <div className="node-title">{title}</div>
      </div>
      <div className="node-content">
        {children}
      </div>
    </div>
  );
};

// Add styles to App.css
export const nodeStyles = `
.node {
  background: #2d2d2d;
  border: 1px solid #3d3d3d;
  border-radius: 4px;
  min-width: 180px;
  height: auto;
  padding: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.node.selected {
  border-color: #fff;
  box-shadow: 0 0 0 2px rgba(255,255,255,0.2);
}

.node-header {
  padding: 4px;
  border-bottom: 1px solid #3d3d3d;
  margin-bottom: 8px;
}

.node-title {
  color: #fff;
  font-size: 14px;
  font-weight: 500;
}

.node-content {
  padding: 4px;
}

.socket {
  width: 12px;
  height: 12px;
  border-radius: 6px;
  background: #4d4d4d;
  border: 2px solid #3d3d3d;
  cursor: pointer;
  transition: all 0.2s;
}

.socket:hover {
  background: #5d5d5d;
}

.socket.input {
  margin-right: 8px;
}

.socket.output {
  margin-left: 8px;
}

.connection {
  stroke: #4d4d4d;
  stroke-width: 2px;
  fill: none;
}

.connection.selected {
  stroke: #fff;
}
`; 