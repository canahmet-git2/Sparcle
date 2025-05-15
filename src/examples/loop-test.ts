import { ParticleNodeSystem } from '../core/particle/ParticleNodeSystem';

// Create a test scene with a circular motion particle effect
export function createLoopTestScene(): ParticleNodeSystem {
  const system = new ParticleNodeSystem();

  // Add circular emitter
  system.addNode({
    id: 'circular_emitter',
    type: 'emitter',
    enabled: true,
    position: { x: 400, y: 300 }, // Center of screen
    spawnRate: 60, // One particle per frame
    spawnCount: 1,
    burstMode: false,
    burstCount: 0,
    burstInterval: 0,
    shape: 'point',
    shapeParams: {},
    initialProperties: {
      life: { min: 2, max: 2 }, // Fixed life for consistent motion
      speed: { min: 100, max: 100 }, // Fixed speed for consistent circle
      direction: { min: 0, max: 360 }, // Full circle
      size: { min: 10, max: 10 }, // Fixed size
      rotation: { min: 0, max: 0 },
      color: { r: 1, g: 0.5, b: 0, a: 1 }, // Orange color
      alpha: 1
    }
  });

  // Add force field for circular motion
  system.addNode({
    id: 'circular_force',
    type: 'forceField',
    enabled: true,
    shape: 'point',
    position: { x: 400, y: 300 }, // Same as emitter
    strength: 200,
    falloff: 'none',
    direction: 'clockwise',
    shapeParams: {}
  });

  // Add color behavior
  system.addNode({
    id: 'color_behavior',
    type: 'behavior',
    enabled: true,
    behaviors: [{
      type: 'color',
      mode: 'overtime',
      value: [
        { r: 1, g: 0.5, b: 0, a: 1 }, // Orange
        { r: 1, g: 0, b: 0, a: 1 },   // Red
        { r: 1, g: 0.5, b: 0, a: 1 }  // Back to orange
      ]
    }]
  });

  // Add renderer with additive blending
  system.addNode({
    id: 'renderer',
    type: 'renderer',
    enabled: true,
    blendMode: 'additive',
    sortMode: 'none',
    renderMode: '2d'
  });

  // Connect nodes
  system.connect('circular_emitter', 'circular_force', 'output');
  system.connect('circular_force', 'color_behavior', 'output');
  system.connect('color_behavior', 'renderer', 'output');

  // Enable looping with 2-second duration
  system.enableLooping(2);

  return system;
} 