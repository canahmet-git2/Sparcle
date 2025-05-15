import { NodeType } from './types';

interface ConnectionRule {
  from: NodeType;
  to: NodeType;
  fromSocket: string;
  toSocket: string;
}

// Define valid connections between nodes
export const connectionRules: ConnectionRule[] = [
  {
    from: 'emitter',
    to: 'transform',
    fromSocket: 'output',
    toSocket: 'input',
  },
  {
    from: 'transform',
    to: 'particle',
    fromSocket: 'output',
    toSocket: 'transform',
  },
  {
    from: 'particle',
    to: 'output',
    fromSocket: 'output',
    toSocket: 'particle',
  },
  {
    from: 'transform',
    to: 'output',
    fromSocket: 'output',
    toSocket: 'transform',
  },
];

// Validate if a connection is allowed
export const validateConnection = (
  fromNode: { type: NodeType },
  toNode: { type: NodeType },
  fromSocket: string,
  toSocket: string
): boolean => {
  return connectionRules.some(
    (rule) =>
      rule.from === fromNode.type &&
      rule.to === toNode.type &&
      rule.fromSocket === fromSocket &&
      rule.toSocket === toSocket
  );
};

// Get data flow for a node
export const getNodeInputs = (
  nodeId: string,
  connections: Array<{ from: string; to: string; fromSocket: string; toSocket: string }>,
  nodes: Record<string, { id: string; type: NodeType; data: any }>
): { [key: string]: any } => {
  const inputs: { [key: string]: any } = {};
  
  connections
    .filter((conn) => conn.to === nodeId)
    .forEach((conn) => {
      const fromNode = nodes[conn.from];
      if (fromNode) {
        inputs[conn.toSocket] = {
          nodeId: fromNode.id,
          data: fromNode.data,
        };
      }
    });
  
  return inputs;
};

// Process node data based on inputs
export const processNodeData = (
  nodeType: NodeType,
  nodeData: any,
  inputs: { [key: string]: any }
): any => {
  switch (nodeType) {
    case 'transform': {
      const inputData = inputs.input?.data || {};
      return {
        ...inputData,
        position: {
          x: (inputData.position?.x || 0) + nodeData.translate.x,
          y: (inputData.position?.y || 0) + nodeData.translate.y,
        },
        scale: {
          x: (inputData.scale?.x || 1) * nodeData.scale.x,
          y: (inputData.scale?.y || 1) * nodeData.scale.y,
        },
        rotation: (inputData.rotation || 0) + nodeData.rotate,
        skew: {
          x: (inputData.skew?.x || 0) + nodeData.skew.x,
          y: (inputData.skew?.y || 0) + nodeData.skew.y,
        },
      };
    }
    case 'particle': {
      const transformData = inputs.transform?.data || {};
      return {
        ...nodeData,
        position: {
          x: nodeData.position.x + (transformData.position?.x || 0),
          y: nodeData.position.y + (transformData.position?.y || 0),
        },
        scale: {
          x: nodeData.scale.x * (transformData.scale?.x || 1),
          y: nodeData.scale.y * (transformData.scale?.y || 1),
        },
        rotation: nodeData.rotation + (transformData.rotation || 0),
      };
    }
    case 'output': {
      const particleData = inputs.particle?.data;
      const transformData = inputs.transform?.data;
      return {
        ...nodeData,
        particle: particleData,
        transform: transformData,
      };
    }
    default:
      return nodeData;
  }
}; 