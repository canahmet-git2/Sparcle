import React from 'react';
import { NodeType } from '../../core/types';

interface ToolbarProps {
  onAddNode: (type: NodeType) => void;
  nodes: Record<string, { type: NodeType }>;
}

interface NodeTypeInfo {
  type: NodeType;
  label: string;
  color: string;
  description: string;
  maxInstances?: number;
}

export const Toolbar: React.FC<ToolbarProps> = ({ onAddNode, nodes }) => {
  const nodeTypes: NodeTypeInfo[] = [
    {
      type: 'emitter',
      label: 'Emitter',
      color: '#2d4d2d',
      description: 'Controls particle emission properties like spawn rate, count, and initial values'
    },
    {
      type: 'transform',
      label: 'Transform',
      color: '#4d2d4d',
      description: 'Handles spatial transformations like position, scale, rotation, and skew'
    },
    {
      type: 'particle',
      label: 'Particle',
      color: '#2d4d2d',
      description: 'Defines particle properties like velocity, acceleration, color, and life'
    },
    {
      type: 'output',
      label: 'Output',
      color: '#4d4d2d',
      description: 'Configures final output settings and exports to Spine format',
      maxInstances: 1
    }
  ];

  const getNodeCount = (type: NodeType): number => {
    return Object.values(nodes).filter(node => node.type === type).length;
  };

  const isNodeDisabled = (type: NodeType, maxInstances?: number): boolean => {
    if (!maxInstances) return false;
    return getNodeCount(type) >= maxInstances;
  };

  return (
    <div className="toolbar">
      <div className="toolbar-section">
        <h3>Add Node</h3>
        <div className="toolbar-buttons">
          {nodeTypes.map((nodeType) => {
            const disabled = isNodeDisabled(nodeType.type, nodeType.maxInstances);
            return (
              <button
                key={nodeType.type}
                className={`toolbar-button ${disabled ? 'disabled' : ''}`}
                style={{ backgroundColor: nodeType.color }}
                onClick={() => !disabled && onAddNode(nodeType.type)}
                title={`${nodeType.description}${disabled ? ' (Maximum instances reached)' : ''}`}
                disabled={disabled}
              >
                <span className="button-label">{nodeType.label}</span>
                {nodeType.maxInstances && (
                  <span className="instance-count">
                    {getNodeCount(nodeType.type)}/{nodeType.maxInstances}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}; 