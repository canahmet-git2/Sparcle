import { NodeParticleRenderer } from '../NodeParticleRenderer';
import { ParticleNodeSystem } from '../ParticleNodeSystem';
import * as PIXI from 'pixi.js';

jest.mock('pixi.js', () => ({
  Application: jest.fn().mockImplementation(() => ({
    stage: {
      addChild: jest.fn(),
      removeChild: jest.fn()
    },
    renderer: {},
    view: document.createElement('canvas'),
    destroy: jest.fn()
  })),
  Sprite: jest.fn().mockImplementation(() => ({
    position: { set: jest.fn() },
    scale: { set: jest.fn() },
    rotation: 0,
    alpha: 1,
    tint: 0xFFFFFF
  })),
  Texture: {
    from: jest.fn().mockReturnValue({ destroy: jest.fn() }),
    WHITE: 'white-texture'
  },
  ParticleContainer: jest.fn().mockImplementation(() => ({
    addChild: jest.fn(),
    removeChild: jest.fn(),
    destroy: jest.fn(),
    children: [],
    blendMode: 'normal'
  })),
  BLEND_MODES: {
    NORMAL: 'normal',
    ADD: 'add',
    MULTIPLY: 'multiply',
    SCREEN: 'screen'
  }
}));

describe('NodeParticleRenderer', () => {
  let renderer: NodeParticleRenderer;
  let canvas: HTMLCanvasElement;
  let system: ParticleNodeSystem;

  beforeEach(() => {
    canvas = document.createElement('canvas');
    renderer = new NodeParticleRenderer(canvas);
    system = new ParticleNodeSystem();
    
    // Mock system methods
    system.getNodes = jest.fn().mockReturnValue(new Map());
    system.getParticles = jest.fn().mockReturnValue([]);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Initialization', () => {
    it('should create PIXI application with correct settings', () => {
      expect(PIXI.Application).toHaveBeenCalledWith({
        view: canvas,
        width: expect.any(Number),
        height: expect.any(Number),
        resolution: expect.any(Number),
        autoDensity: true,
        backgroundColor: 0x000000,
        antialias: true,
        powerPreference: 'high-performance'
      });
    });

    it('should initialize default texture', () => {
      expect(PIXI.Texture.from).toHaveBeenCalledWith(PIXI.Texture.WHITE);
    });
  });

  describe('Particle Container Management', () => {
    it('should create container for renderer node', () => {
      const rendererNode = {
        id: 'test-renderer',
        type: 'renderer',
        enabled: true,
        blendMode: 'normal'
      };
      const nodesMap = new Map([[rendererNode.id, rendererNode]]);
      system.getNodes.mockReturnValue(nodesMap);

      renderer.updateParticles(system);
      expect(PIXI.ParticleContainer).toHaveBeenCalled();
    });

    it('should set correct blend mode', () => {
      const rendererNode = {
        id: 'test-renderer',
        type: 'renderer',
        enabled: true,
        blendMode: 'additive'
      };
      const nodesMap = new Map([[rendererNode.id, rendererNode]]);
      system.getNodes.mockReturnValue(nodesMap);

      renderer.updateParticles(system);
      const container = renderer['particleContainers'].get('test-renderer');
      expect(container.blendMode).toBe(PIXI.BLEND_MODES.ADD);
    });
  });

  describe('Particle Rendering', () => {
    it('should update sprite properties', () => {
      const rendererNode = {
        id: 'test-renderer',
        type: 'renderer',
        enabled: true,
        blendMode: 'normal'
      };
      const nodesMap = new Map([[rendererNode.id, rendererNode]]);
      system.getNodes.mockReturnValue(nodesMap);

      const particle = {
        position: { x: 10, y: 20 },
        scale: 2,
        rotation: 1,
        alpha: 0.5,
        color: { r: 1, g: 0, b: 0, a: 1 },
        velocity: { x: 0, y: 0 }
      };

      system.getParticles.mockReturnValue([particle]);
      
      const mockSprite = {
        position: { set: jest.fn() },
        scale: { set: jest.fn() },
        rotation: 0,
        alpha: 1,
        tint: 0xFFFFFF
      };
      PIXI.Sprite.mockImplementation(() => mockSprite);

      renderer.updateParticles(system);

      expect(mockSprite.position.set).toHaveBeenCalledWith(10, 20);
      expect(mockSprite.scale.set).toHaveBeenCalledWith(2, 2);
      expect(mockSprite.rotation).toBe(1);
      expect(mockSprite.alpha).toBe(0.5);
      expect(mockSprite.tint).toBe(0xFF0000);
    });
  });

  describe('Cleanup', () => {
    it('should properly destroy resources', () => {
      const mockDestroy = jest.fn();
      renderer['app'].destroy = mockDestroy;
      renderer['initialized'] = true;

      renderer.destroy();
      expect(mockDestroy).toHaveBeenCalledWith(true);
      expect(renderer['initialized']).toBe(false);
    });
  });
}); 