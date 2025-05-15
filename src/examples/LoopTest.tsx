import React, { useEffect, useRef } from 'react';
import { createLoopTestScene } from './loop-test';
import { NodeParticleRenderer } from '../core/particle/NodeParticleRenderer';

export const LoopTest: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rendererRef = useRef<NodeParticleRenderer | null>(null);
  const systemRef = useRef<ReturnType<typeof createLoopTestScene> | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Initialize system and renderer
    systemRef.current = createLoopTestScene();
    rendererRef.current = new NodeParticleRenderer(canvas);

    // Make system available globally for debugging
    window.particleSystem = systemRef.current;

    // Set up animation loop
    let lastTime = 0;
    const animate = (time: number) => {
      const deltaTime = (time - lastTime) / 1000;
      lastTime = time;

      if (systemRef.current && rendererRef.current) {
        systemRef.current.update(deltaTime);
        rendererRef.current.updateParticles(systemRef.current);
      }

      requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);

    // Cleanup
    return () => {
      if (rendererRef.current) {
        rendererRef.current.destroy();
      }
      window.particleSystem = null;
    };
  }, []);

  return (
    <div style={{ width: '100%', height: '100vh', background: '#000' }}>
      <canvas
        ref={canvasRef}
        style={{ width: '100%', height: '100%' }}
        width={800}
        height={600}
      />
      <div style={{
        position: 'absolute',
        top: 10,
        left: 10,
        color: '#fff',
        fontFamily: 'monospace'
      }}>
        Loop Test Scene
        <br />
        Duration: 2s
        <br />
        Press F12 to open DevTools and access particleSystem
      </div>
    </div>
  );
}; 