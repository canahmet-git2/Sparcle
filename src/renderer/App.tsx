import React from 'react';
import './App.css';
import { TitleBar } from './components/TitleBar';
import { PreviewWindow } from './components/PreviewWindow';
import { NodeEditor } from './graph/NodeEditor';
import { ErrorDisplay } from './components/ErrorDisplay';
import { withComponentErrorLogging } from '../utils/errorLogger';
import './styles/app.css';
import './styles/nodes.css';

const App: React.FC = () => {
  const [nodeData, setNodeData] = React.useState<any>(null);

  const handleNodeChange = withComponentErrorLogging((data: any) => {
    setNodeData(data);
  }, 'App');

  return (
    <div className="app">
      <TitleBar title="Sparcle - Particle System Editor" />
      <div className="main-content">
        <div className="editor-pane">
          <NodeEditor onNodeChange={handleNodeChange} />
          <div className="resize-handle" />
        </div>
        <div className="preview-pane">
          <PreviewWindow data={nodeData} />
        </div>
      </div>
      <ErrorDisplay maxErrors={5} />
    </div>
  );
};

export default App; 