import '@testing-library/jest-dom';

// Mock PIXI.js
jest.mock('pixi.js', () => ({
  Application: jest.fn().mockImplementation(() => ({
    stage: {},
    renderer: {},
    view: document.createElement('canvas'),
    destroy: jest.fn()
  })),
  Sprite: jest.fn(),
  Texture: {
    from: jest.fn(),
    WHITE: 'white-texture'
  },
  ParticleContainer: jest.fn().mockImplementation(() => ({
    addChild: jest.fn(),
    removeChild: jest.fn(),
    destroy: jest.fn()
  })),
  BLEND_MODES: {
    NORMAL: 'normal',
    ADD: 'add',
    MULTIPLY: 'multiply',
    SCREEN: 'screen'
  }
}));

// Mock Rete.js
jest.mock('rete', () => ({
  createEditor: jest.fn().mockImplementation(() => ({
    use: jest.fn(),
    addNode: jest.fn(),
    on: jest.fn(),
    getNodes: jest.fn().mockReturnValue(new Map()),
    getConnections: jest.fn().mockReturnValue([]),
    destroy: jest.fn()
  })),
  Node: class {},
  Socket: class {}
})); 