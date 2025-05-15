import React, { useEffect, useRef, useState } from 'react';
import { NodeEditor as ReteEditor, Node as ReteNode, Connection as ReteConnection } from 'rete';
import { AreaPlugin, AreaExtensions } from 'rete-area-plugin';
import { ReactPlugin, Presets as ReactPresets } from 'rete-react-plugin';
import { ConnectionPlugin, Presets as ConnectionPresets } from 'rete-connection-plugin';
import { EmitterNode } from './nodes/EmitterNode';
import { TransformNode } from './nodes/TransformNode';
import { ParticleNode } from './nodes/ParticleNode';
import { OutputNode } from './nodes/OutputNode';
import { NodeType, EmitterProperties, TransformProperties, ParticleProperties } from '../../core/types';
import { validateConnection, getNodeInputs, processNodeData } from '../../core/connections';
import { Toolbar } from '../components/Toolbar';

interface NodeEditorProps {
  onNodeChange?: (nodeId: string, data: any) => void;
}

interface Node {
  id: string;
  type: NodeType;
  position: { x: number; y: number };
  width: number;
  height: number;
  data: any;
}

interface Connection {
  from: string;
  to: string;
  fromSocket: string;
  toSocket: string;
}

// Define Schemes for Rete
// Our custom Node interface
interface CustomNode extends ReteNode {
  type: NodeType;
  position: { x: number; y: number };
  width: number;
  height: number;
  data: EmitterProperties | TransformProperties | ParticleProperties | any; // More specific types here
}

// Our custom Connection interface (might need to align with Rete's expectations)
interface CustomConnection extends ReteConnection<CustomNode, CustomNode> {
  fromSocket: string;
  toSocket: string;
}

// Base Schemes for Rete
type Schemes = {
  Node: CustomNode;
  Connection: CustomConnection<CustomNode, CustomNode>; // Ensure this is compatible
};

// Define AreaExtra for AreaPlugin and ReactPlugin context if needed (e.g., for custom rendering)
// For now, it can be a simple type or even just { type: 'render', data: any } for ReactPlugin
type AreaExtra = { type: 'render', data: React.ReactElement } | { type: 'pointer', event: PointerEvent };

const getDefaultNodeData = (type: NodeType) => {
  switch (type) {
    case 'emitter':
      return {
        position: { x: 0, y: 0 },
        spawnRate: 10,
        spawnCount: 1,
        duration: 1,
        loop: true,
        startLife: 1,
        startSpeed: { x: 0, y: 0 },
        startScale: { x: 1, y: 1 },
        startRotation: 0,
        startColor: { r: 1, g: 1, b: 1, a: 1 }
      };
    case 'transform':
      return {
        translate: { x: 0, y: 0 },
        scale: { x: 1, y: 1 },
        rotate: 0,
        skew: { x: 0, y: 0 }
      };
    case 'particle':
      return {
        position: { x: 0, y: 0 },
        velocity: { x: 0, y: 0 },
        acceleration: { x: 0, y: 0 },
        scale: { x: 1, y: 1 },
        rotation: 0,
        color: { r: 1, g: 1, b: 1, a: 1 },
        alpha: 1,
        life: 1
      };
    case 'output':
      return {
        blendMode: 'normal',
        optimizeMesh: true,
        loopDuration: 1
      };
  }
};

export const NodeEditor: React.FC<NodeEditorProps> = ({ onNodeChange }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const editorRef = useRef<ReteEditor<Schemes> | null>(null);
  const areaRef = useRef<AreaPlugin<Schemes, AreaExtra> | null>(null);
  const [nodes, setNodes] = useState<Record<string, Node>>({});
  const [connections, setConnections] = useState<Connection[]>([]);
  const [nextNodeId, setNextNodeId] = useState(5); // Start from 5 since we have 4 initial nodes

  const handleAddNode = async (type: NodeType) => {
    if (!editorRef.current || !areaRef.current) return;

    // Check if we're trying to add a second output node
    if (type === 'output' && Object.values(nodes).some(node => node.type === 'output')) {
      // TODO: Show error notification
      console.warn('Only one output node is allowed');
      return;
    }

    const editor = editorRef.current;
    const id = nextNodeId.toString();
    
    // Calculate position based on viewport center
    const container = containerRef.current!;
    const rect = container.getBoundingClientRect();
    const position = {
      x: (rect.width / 2 - container.scrollLeft),
      y: (rect.height / 2 - container.scrollTop)
    };

    const node = {
      id,
      type,
      position,
      width: 200,
      height: type === 'particle' ? 500 : type === 'emitter' ? 400 : 300,
      data: getDefaultNodeData(type)
    };

    await editor.addNode(node);
    setNodes((prev) => ({ ...prev, [id]: node }));
    setNextNodeId((prev) => prev + 1);
  };

  const handleNodeDelete = async (nodeId: string) => {
    if (!editorRef.current) return;

    const editor = editorRef.current;
    await editor.removeNode(nodeId);
    
    // Remove node from state
    setNodes((prev) => {
      const newNodes = { ...prev };
      delete newNodes[nodeId];
      return newNodes;
    });

    // Remove associated connections
    setConnections((prev) => 
      prev.filter(conn => conn.from !== nodeId && conn.to !== nodeId)
    );

    // Update affected nodes
    connections
      .filter(conn => conn.from === nodeId)
      .forEach(conn => updateNodeData(conn.to));
  };

  const handleNodeMove = (nodeId: string, position: { x: number; y: number }) => {
    setNodes((prev) => ({
      ...prev,
      [nodeId]: {
        ...prev[nodeId],
        position
      }
    }));
  };

  useEffect(() => {
    if (!containerRef.current) return;
    let destroyed = false;

    const init = async () => {
      const container = containerRef.current!;
      try {
        const editor = new ReteEditor<Schemes>();
        editorRef.current = editor;

        const area = new AreaPlugin<Schemes, AreaExtra>(container);
        editor.use(area);

        const connection = new ConnectionPlugin<Schemes, AreaExtra>();
        const render = new ReactPlugin<Schemes, AreaExtra>();

        area.use(connection);
        area.use(render);
        
        areaRef.current = area;

        // Presets for ReactPlugin
        render.addPreset(ReactPresets.classic.setup());
        connection.addPreset(ConnectionPresets.classic.setup());

        // Add basic controls (zoom, pan)
        AreaExtensions.selectableNodes(area, AreaExtensions.selector(), {
          accumulating: AreaExtensions.accumulateOnCtrl()
        });

        // Enable node dragging and snapping
        AreaExtensions.simpleNodesOrder(area);
        AreaExtensions.snapGrid(area, { size: 20 });

        // Set up default viewport
        area.translate(container.clientWidth / 2, container.clientHeight / 2);

        if (!destroyed) {
          // Register node components
          render.addPreset({
            render: (props: any) => <EmitterNode {...props} />,
            update: (props: any) => <EmitterNode {...props} />
          });
          render.addPreset({
            render: (props: any) => <TransformNode {...props} />,
            update: (props: any) => <TransformNode {...props} />
          });
          render.addPreset({
            render: (props: any) => <ParticleNode {...props} />,
            update: (props: any) => <ParticleNode {...props} />
          });
          render.addPreset({
            render: (props: any) => <OutputNode {...props} />,
            update: (props: any) => <OutputNode {...props} />
          });

          // Add initial nodes
          const initialNodes = {
            '1': {
              id: '1',
              type: 'emitter' as NodeType,
              position: { x: -300, y: 0 },
              width: 200,
              height: 400,
              data: getDefaultNodeData('emitter')
            },
            '2': {
              id: '2',
              type: 'transform' as NodeType,
              position: { x: 0, y: 0 },
              width: 200,
              height: 300,
              data: getDefaultNodeData('transform')
            },
            '3': {
              id: '3',
              type: 'particle' as NodeType,
              position: { x: 300, y: 0 },
              width: 200,
              height: 500,
              data: getDefaultNodeData('particle')
            },
            '4': {
              id: '4',
              type: 'output' as NodeType,
              position: { x: 600, y: 0 },
              width: 200,
              height: 300,
              data: getDefaultNodeData('output')
            }
          };

          // First set the state
          setNodes(initialNodes);

          // Then add nodes to editor
          for (const node of Object.values(initialNodes)) {
            await editor.addNode(node);
          }

          // Set up event listeners after nodes are added
          area.addPipe(context => {
            if (context.type === 'nodecreate') {
              const { node } = context;
              setNodes(prev => ({ ...prev, [node.id]: node }));
            }
            if (context.type === 'noderemove') {
              const { node } = context;
              handleNodeDelete(node.id);
            }
            if (context.type === 'nodetranslate') {
              const { node, position } = context;
              handleNodeMove(node.id, position);
            }
            if (context.type === 'connectioncreate') {
              const { connection } = context;
              const { from, to, fromSocket, toSocket } = connection;
              const fromNode = nodes[from];
              const toNode = nodes[to];

              // Check if the target socket already has a connection
              const hasExistingConnection = connections.some(
                conn => conn.to === to && conn.toSocket === toSocket
              );

              if (hasExistingConnection) {
                console.warn('Socket already has a connection');
                return false;
              }

              if (!validateConnection(
                { type: fromNode.type },
                { type: toNode.type },
                fromSocket,
                toSocket
              )) {
                console.warn('Invalid connection');
                return false;
              }

              setConnections(prev => [...prev, connection]);
              updateNodeData(connection.to);
            }
            if (context.type === 'connectionremove') {
              const { connection } = context;
              setConnections(prev => prev.filter(c => c !== connection));
              updateNodeData(connection.to);
            }
            if (context.type === 'nodeupdate') {
              const { node, data } = context;
              setNodes(prev => ({
                ...prev,
                [node.id]: {
                  ...prev[node.id],
                  data
                }
              }));
              updateNodeData(node.id);
            }
            return context;
          });

          // Initial zoom after nodes are added
          await AreaExtensions.zoomAt(area, Object.values(initialNodes));
        }
      } catch (error) {
        console.error("Error initializing Rete editor:", error);
      }
    };

    init();

    return () => {
      destroyed = true;
      if (areaRef.current && typeof areaRef.current.destroy === 'function') {
        areaRef.current.destroy(); // AreaPlugin might be what needs destroying
      }
      if (editorRef.current && typeof editorRef.current.destroy === 'function') {
        editorRef.current.destroy();
      }
    };
  }, []);

  const updateNodeData = (nodeId: string) => {
    const node = nodes[nodeId];
    if (!node) return;

    const inputs = getNodeInputs(nodeId, connections, nodes);
    const processedData = processNodeData(node.type, node.data, inputs);

    if (onNodeChange) {
      onNodeChange(nodeId, processedData);
    }

    // Update downstream nodes
    connections
      .filter((conn) => conn.from === nodeId)
      .forEach((conn) => updateNodeData(conn.to));
  };

  return (
    <div className="node-editor-container">
      <Toolbar onAddNode={handleAddNode} nodes={Object.values(nodes)} />
      <div ref={containerRef} className="rete-container" />
    </div>
  );
}; 