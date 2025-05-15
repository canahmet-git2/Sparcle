import React, { useEffect, useRef, useState } from 'react';
import { NodeParticleRenderer } from '@/core/particle/NodeParticleRenderer';
import { ParticleNodeSystem } from '@/core/particle/ParticleNodeSystem';
import { withComponentErrorLogging, withErrorLogging } from '../../utils/errorLogger';

// Configure Pixi.js settings
PIXI.BatchRenderer.defaultMaxTextures = 16;
PIXI.Program.defaultFragmentPrecision = PIXI.PRECISION.MEDIUM;
PIXI.BaseTexture.defaultOptions.scaleMode = PIXI.SCALE_MODES.LINEAR;
PIXI.settings.RENDER_OPTIONS = {
  antialias: true,
  backgroundAlpha: 0,
  clearBeforeRender: true,
  preserveDrawingBuffer: true
};

interface PreviewWindowProps {
  data: {
    nodes: Array<{
      id: string;
      type: string;
      [key: string]: any;
    }>;
    connections: Array<{
      from: string;
      to: string;
      socket: string;
    }>;
    settings?: {
      blendMode?: 'normal' | 'additive' | 'multiply' | 'screen';
      showGrid?: boolean;
      zoom?: number;
    };
  };
}

export const PreviewWindow: React.FC<PreviewWindowProps> = ({ data }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rendererRef = useRef<NodeParticleRenderer | null>(null);
  const systemRef = useRef<ParticleNodeSystem | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(true);
  const [showGrid, setShowGrid] = useState(data.settings?.showGrid ?? true);
  const [zoom, setZoom] = useState(data.settings?.zoom ?? 1);

  // Initialize particle system and renderer
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      console.warn('Canvas ref is not available');
      return;
    }

    const init = withErrorLogging(async () => {
      try {
        // Initialize renderer
        console.log('Initializing NodeParticleRenderer...');
        rendererRef.current = new NodeParticleRenderer(canvas);
        
        // Initialize particle system
        console.log('Initializing ParticleNodeSystem...');
        systemRef.current = new ParticleNodeSystem();

        // Set up canvas size
        const updateCanvasSize = withComponentErrorLogging(() => {
          if (!canvas || !containerRef.current || !rendererRef.current) return;
          
          const rect = containerRef.current.getBoundingClientRect();
          const width = rect.width;
          const height = rect.height;
          
          canvas.style.width = `${width}px`;
          canvas.style.height = `${height}px`;
          rendererRef.current.resize(width, height);
        }, 'PreviewWindow');

        // Handle window resize
        window.addEventListener('resize', updateCanvasSize);
        updateCanvasSize();

        // Animation loop
        let lastTime: number | null = null;
        let animationFrame: number;
        let frameCount = 0;
        const fpsInterval = 60; // Log FPS every 60 frames

        const animate = withComponentErrorLogging((time: number) => {
          if (!rendererRef.current || !systemRef.current) {
            throw new Error('Renderer or particle system not available for animation frame');
          }

          const deltaTime = lastTime ? (time - lastTime) / 1000 : 0;
          lastTime = time;

          // Update particle system if playing
          if (isPlaying) {
            systemRef.current.update(deltaTime);
          }

          // Update renderer
          rendererRef.current.updateParticles(systemRef.current);
          
          // Log performance metrics periodically
          frameCount++;
          if (frameCount % fpsInterval === 0) {
            const fps = 1 / deltaTime;
            console.log(`Performance metrics - FPS: ${fps.toFixed(2)}, Active particles: ${systemRef.current.getParticles().length}`);
          }

          animationFrame = requestAnimationFrame(animate);
        }, 'PreviewWindow');

        animationFrame = requestAnimationFrame(animate);
        console.log('Animation loop started');

        return () => {
          console.log('Cleaning up PreviewWindow...');
          window.removeEventListener('resize', updateCanvasSize);
          cancelAnimationFrame(animationFrame);
          rendererRef.current?.destroy();
        };
      } catch (error) {
        throw error;
      }
    }, 'PreviewWindow')();

    return () => {
      if (rendererRef.current) {
        rendererRef.current.destroy();
      }
    };
  }, [isPlaying]);

  // Update particle system when node data changes
  useEffect(() => {
    if (!systemRef.current) return;
    
    const updateParticleSystem = withComponentErrorLogging(() => {
      if (!systemRef.current) return;

      // Clear existing nodes and connections
      systemRef.current = new ParticleNodeSystem();

      // Add new nodes
      data.nodes.forEach(node => {
        systemRef.current!.addNode(node);
      });

      // Add new connections
      data.connections.forEach(conn => {
        systemRef.current!.connect(conn.from, conn.to, conn.socket);
      });
    }, 'PreviewWindow');

    updateParticleSystem();
  }, [data.nodes, data.connections]);

  return (
    <div 
      ref={containerRef} 
      className="preview-window"
      style={{ width: '100%', height: '100%', position: 'relative' }}
    >
      <canvas 
        ref={canvasRef}
        style={{
          width: '100%',
          height: '100%',
          transform: `scale(${zoom})`,
          transformOrigin: 'center'
        }}
      />
      <div className="preview-controls" style={{
        position: 'absolute',
        bottom: 10,
        left: 10,
        display: 'flex',
        gap: 10,
        background: 'rgba(0,0,0,0.5)',
        padding: 5,
        borderRadius: 5
      }}>
        <button onClick={() => setIsPlaying(!isPlaying)}>
          {isPlaying ? '⏸️' : '▶️'}
        </button>
        <button onClick={() => setShowGrid(!showGrid)}>
          {showGrid ? '⊞' : '⊡'}
        </button>
        <button onClick={() => setZoom(z => Math.max(0.1, z - 0.1))}>
          🔍-
        </button>
        <button onClick={() => setZoom(z => Math.min(5, z + 0.1))}>
          🔍+
        </button>
      </div>
    </div>
  );
}; 