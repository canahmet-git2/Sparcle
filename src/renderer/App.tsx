import React, { useState } from 'react';
import { HashRouter as Router, Route, Routes, Link } from 'react-router-dom';
import './styles/app.css';
import { TitleBar } from './components/TitleBar';
import { NodeEditor } from './graph/NodeEditor';
import { PreviewWindow } from './components/PreviewWindow';
import { ErrorDisplay } from './components/ErrorDisplay';
import { LoopTest } from '../examples/LoopTest';
import './styles/nodes.css';

const EditorPage: React.FC = () => {
  const [nodeData, setNodeData] = useState({});

  const handleNodeChange = (data: any) => {
    setNodeData(data);
  };

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

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<EditorPage />} />
        <Route path="/loop-test" element={<LoopTest />} />
      </Routes>
      <div style={{
        position: 'fixed',
        bottom: 10,
        right: 10,
        zIndex: 1000
      }}>
        <Link to="/" style={{ marginRight: 10, color: '#fff' }}>Editor</Link>
        <Link to="/loop-test" style={{ color: '#fff' }}>Loop Test</Link>
      </div>
    </Router>
  );
};

export default App; 