import { ParticleNodeSystem } from '../ParticleNodeSystem';

describe('ParticleNodeSystem', () => {
  let system: ParticleNodeSystem;

  beforeEach(() => {
    system = new ParticleNodeSystem();
  });

  describe('Node Management', () => {
    it('should initialize with default nodes', () => {
      const nodes = Array.from(system['nodes'].values());
      expect(nodes).toHaveLength(2);
      expect(nodes[0].type).toBe('emitter');
      expect(nodes[1].type).toBe('renderer');
    });

    it('should add a new node', () => {
      const forceField = {
        id: 'test-force',
        type: 'forceField',
        enabled: true,
        position: { x: 0, y: 0 },
        strength: 1,
        falloff: 'none',
        direction: 'inward',
        shape: 'point',
        shapeParams: {}
      };

      system.addNode(forceField);
      expect(system['nodes'].get('test-force')).toEqual(forceField);
    });

    it('should remove a node and its connections', () => {
      system.addNode({
        id: 'test-node',
        type: 'forceField',
        enabled: true
      });
      system.connect('test-node', 'default_renderer', 'output');
      
      system.removeNode('test-node');
      expect(system['nodes'].has('test-node')).toBeFalsy();
      expect(system['connections']).toEqual(
        expect.not.arrayContaining([
          expect.objectContaining({ from: 'test-node' })
        ])
      );
    });
  });

  describe('Connection Management', () => {
    it('should create a valid connection', () => {
      const forceField = {
        id: 'test-force',
        type: 'forceField',
        enabled: true
      };
      system.addNode(forceField);
      
      system.connect('test-force', 'default_renderer', 'output');
      expect(system['connections']).toContainEqual({
        from: 'test-force',
        to: 'default_renderer',
        socket: 'output'
      });
    });

    it('should throw error for invalid connection', () => {
      expect(() => {
        system.connect('invalid-id', 'default_renderer', 'output');
      }).toThrow('Invalid node IDs for connection');
    });

    it('should disconnect nodes', () => {
      const forceField = {
        id: 'test-force',
        type: 'forceField',
        enabled: true
      };
      system.addNode(forceField);
      system.connect('test-force', 'default_renderer', 'output');
      
      system.disconnect('test-force', 'default_renderer', 'output');
      expect(system['connections']).toHaveLength(0);
    });
  });

  describe('Particle Update', () => {
    it('should update particle life and position', () => {
      const deltaTime = 0.1;
      const particle = {
        life: 1.0,
        position: { x: 0, y: 0 },
        velocity: { x: 1, y: 1 },
        acceleration: { x: 0, y: 0 },
        rotation: 0,
        rotationSpeed: 0,
        scale: 1,
        color: { r: 1, g: 1, b: 1, a: 1 },
        alpha: 1,
        age: 0
      };
      system['particles'] = [particle];

      system.update(deltaTime);

      expect(particle.life).toBe(0.9);
      expect(particle.position.x).toBe(0.1);
      expect(particle.position.y).toBe(0.1);
    });

    it('should remove dead particles', () => {
      const particle1 = {
        life: 0.1,
        position: { x: 0, y: 0 },
        velocity: { x: 0, y: 0 },
        acceleration: { x: 0, y: 0 },
        rotation: 0,
        rotationSpeed: 0,
        scale: 1,
        color: { r: 1, g: 1, b: 1, a: 1 },
        alpha: 1,
        age: 0
      };
      const particle2 = { ...particle1, life: -0.1 };
      system['particles'] = [particle1, particle2];

      // Disable particle emission
      const emitterNode = Array.from(system['nodes'].values())
        .find(node => node.type === 'emitter');
      if (emitterNode) {
        emitterNode.enabled = false;
      }

      system.update(0.2);
      expect(system['particles']).toHaveLength(0);
    });
  });
}); 