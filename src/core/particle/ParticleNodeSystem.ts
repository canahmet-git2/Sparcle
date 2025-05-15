import { Vector2, Color } from '../types';

// Base interface for all node types
export interface NodeBase {
  id: string;
  type: string;
  enabled: boolean;
  name?: string;
}

// Emitter node defines how particles are spawned
export interface EmitterNode extends NodeBase {
  type: 'emitter';
  position: Vector2;
  spawnRate: number;
  spawnCount: number;
  burstMode: boolean;
  burstCount: number;
  burstInterval: number;
  shape: 'point' | 'circle' | 'line' | 'rectangle';
  shapeParams: {
    radius?: number;
    width?: number;
    height?: number;
    angle?: number;
  };
  initialProperties: {
    life: { min: number; max: number };
    speed: { min: number; max: number };
    direction: { min: number; max: number };
    size: { min: number; max: number };
    rotation: { min: number; max: number };
    color: Color;
    alpha: number;
  };
}

// Force field node affects particle movement
export interface ForceFieldNode extends NodeBase {
  type: 'forceField';
  shape: 'point' | 'circle' | 'rectangle' | 'line';
  position: Vector2;
  strength: number;
  falloff: 'linear' | 'quadratic' | 'none';
  direction: 'inward' | 'outward' | 'clockwise' | 'counterclockwise' | 'custom';
  customAngle?: number;
  shapeParams: {
    radius?: number;
    width?: number;
    height?: number;
    angle?: number;
  };
}

// Behavior node defines how particles change over time
export interface BehaviorNode extends NodeBase {
  type: 'behavior';
  behaviors: Array<{
    type: 'color' | 'size' | 'rotation' | 'velocity' | 'alpha';
    mode: 'constant' | 'overtime' | 'random';
    value: number | number[] | Color | Color[];
    curve?: number[]; // For overtime mode
    timeScale?: number;
  }>;
}

// Renderer node defines how particles are drawn
export interface RendererNode extends NodeBase {
  type: 'renderer';
  blendMode: 'normal' | 'additive' | 'multiply' | 'screen';
  texture?: string;
  material?: {
    type: 'sprite' | 'trail' | 'ribbon';
    params: {
      length?: number;
      segments?: number;
      fadeOut?: boolean;
      fadeOutLength?: number;
    };
  };
  sortMode: 'none' | 'byDistance' | 'byAge';
  renderMode: '2d' | 'billboard' | 'stretched';
}

// Main particle system class
export class ParticleNodeSystem {
  private nodes: Map<string, NodeBase> = new Map();
  private connections: Array<{ from: string; to: string; socket: string }> = [];
  private time: number = 0;
  private particles: Array<ParticleData> = [];

  constructor() {
    // Initialize with default nodes
    this.addNode({
      id: 'default_emitter',
      type: 'emitter',
      enabled: true,
      position: { x: 0, y: 0 },
      spawnRate: 10,
      spawnCount: 1,
      burstMode: false,
      burstCount: 10,
      burstInterval: 1,
      shape: 'point',
      shapeParams: {},
      initialProperties: {
        life: { min: 1, max: 2 },
        speed: { min: 1, max: 2 },
        direction: { min: 0, max: 360 },
        size: { min: 1, max: 1 },
        rotation: { min: 0, max: 0 },
        color: { r: 1, g: 1, b: 1, a: 1 },
        alpha: 1
      }
    } as EmitterNode);

    this.addNode({
      id: 'default_renderer',
      type: 'renderer',
      enabled: true,
      blendMode: 'normal',
      sortMode: 'none',
      renderMode: '2d'
    } as RendererNode);
  }

  public addNode(node: NodeBase): void {
    this.nodes.set(node.id, node);
  }

  public removeNode(id: string): void {
    this.nodes.delete(id);
    // Remove connections involving this node
    this.connections = this.connections.filter(
      conn => conn.from !== id && conn.to !== id
    );
  }

  public connect(fromId: string, toId: string, socket: string): void {
    if (!this.nodes.has(fromId) || !this.nodes.has(toId)) {
      throw new Error('Invalid node IDs for connection');
    }
    this.connections.push({ from: fromId, to: toId, socket });
  }

  public disconnect(fromId: string, toId: string, socket: string): void {
    this.connections = this.connections.filter(
      conn => !(conn.from === fromId && conn.to === toId && conn.socket === socket)
    );
  }

  public update(deltaTime: number): void {
    this.time += deltaTime;

    // Update existing particles
    this.updateParticles(deltaTime);

    // Spawn new particles from emitter nodes
    this.nodes.forEach(node => {
      if (node.type === 'emitter' && node.enabled) {
        this.spawnParticles(node as EmitterNode, deltaTime);
      }
    });

    // Apply force fields
    this.nodes.forEach(node => {
      if (node.type === 'forceField' && node.enabled) {
        this.applyForceField(node as ForceFieldNode);
      }
    });

    // Apply behaviors
    this.nodes.forEach(node => {
      if (node.type === 'behavior' && node.enabled) {
        this.applyBehaviors(node as BehaviorNode);
      }
    });
  }

  private updateParticles(deltaTime: number): void {
    this.particles = this.particles.filter(particle => {
      // Update life
      particle.life -= deltaTime;
      if (particle.life <= 0) return false;

      // Update position based on velocity
      particle.position.x += particle.velocity.x * deltaTime;
      particle.position.y += particle.velocity.y * deltaTime;

      // Update rotation
      particle.rotation += particle.rotationSpeed * deltaTime;

      return true;
    });
  }

  private spawnParticles(emitter: EmitterNode, deltaTime: number): void {
    const spawnCount = emitter.burstMode 
      ? (this.time % emitter.burstInterval < deltaTime ? emitter.burstCount : 0)
      : Math.floor(emitter.spawnRate * deltaTime);

    for (let i = 0; i < spawnCount; i++) {
      const particle = this.createParticle(emitter);
      this.particles.push(particle);
    }
  }

  private createParticle(emitter: EmitterNode): ParticleData {
    const props = emitter.initialProperties;
    const angle = this.randomRange(props.direction.min, props.direction.max) * Math.PI / 180;
    const speed = this.randomRange(props.speed.min, props.speed.max);

    return {
      position: { ...this.getSpawnPosition(emitter) },
      velocity: {
        x: Math.cos(angle) * speed,
        y: Math.sin(angle) * speed
      },
      acceleration: { x: 0, y: 0 },
      scale: this.randomRange(props.size.min, props.size.max),
      rotation: this.randomRange(props.rotation.min, props.rotation.max),
      rotationSpeed: 0,
      color: { ...props.color },
      alpha: props.alpha,
      life: this.randomRange(props.life.min, props.life.max),
      age: 0
    };
  }

  private getSpawnPosition(emitter: EmitterNode): Vector2 {
    switch (emitter.shape) {
      case 'circle': {
        const angle = Math.random() * Math.PI * 2;
        const radius = Math.random() * (emitter.shapeParams.radius || 0);
        return {
          x: emitter.position.x + Math.cos(angle) * radius,
          y: emitter.position.y + Math.sin(angle) * radius
        };
      }
      case 'rectangle': {
        const width = emitter.shapeParams.width || 0;
        const height = emitter.shapeParams.height || 0;
        return {
          x: emitter.position.x + (Math.random() - 0.5) * width,
          y: emitter.position.y + (Math.random() - 0.5) * height
        };
      }
      case 'line': {
        const length = emitter.shapeParams.width || 0;
        const angle = (emitter.shapeParams.angle || 0) * Math.PI / 180;
        const t = Math.random();
        return {
          x: emitter.position.x + Math.cos(angle) * length * t,
          y: emitter.position.y + Math.sin(angle) * length * t
        };
      }
      default:
        return { ...emitter.position };
    }
  }

  private applyForceField(field: ForceFieldNode): void {
    this.particles.forEach(particle => {
      const dx = field.position.x - particle.position.x;
      const dy = field.position.y - particle.position.y;
      const distSq = dx * dx + dy * dy;
      const dist = Math.sqrt(distSq);

      if (dist === 0) return;

      let force = field.strength;
      switch (field.falloff) {
        case 'linear':
          force *= 1 - dist / (field.shapeParams.radius || 1);
          break;
        case 'quadratic':
          force *= 1 - (dist * dist) / ((field.shapeParams.radius || 1) ** 2);
          break;
      }

      if (force <= 0) return;

      let fx = dx / dist;
      let fy = dy / dist;

      switch (field.direction) {
        case 'outward':
          fx = -fx;
          fy = -fy;
          break;
        case 'clockwise':
          [fx, fy] = [-fy, fx];
          break;
        case 'counterclockwise':
          [fx, fy] = [fy, -fx];
          break;
        case 'custom':
          const angle = (field.customAngle || 0) * Math.PI / 180;
          fx = Math.cos(angle);
          fy = Math.sin(angle);
          break;
      }

      particle.velocity.x += fx * force;
      particle.velocity.y += fy * force;
    });
  }

  private applyBehaviors(behavior: BehaviorNode): void {
    this.particles.forEach(particle => {
      behavior.behaviors.forEach(b => {
        const t = particle.age / particle.life;
        
        switch (b.type) {
          case 'color':
            if (Array.isArray(b.value)) {
              const colors = b.value as Color[];
              const idx = Math.min(Math.floor(t * colors.length), colors.length - 1);
              particle.color = { ...colors[idx] };
            }
            break;
          case 'size':
            if (Array.isArray(b.value)) {
              const sizes = b.value as number[];
              const idx = Math.min(Math.floor(t * sizes.length), sizes.length - 1);
              particle.scale = sizes[idx];
            }
            break;
          case 'alpha':
            if (Array.isArray(b.value)) {
              const alphas = b.value as number[];
              const idx = Math.min(Math.floor(t * alphas.length), alphas.length - 1);
              particle.alpha = alphas[idx];
            }
            break;
          // Add more behavior types as needed
        }
      });
    });
  }

  private randomRange(min: number, max: number): number {
    return min + Math.random() * (max - min);
  }

  public getParticles(): ParticleData[] {
    return this.particles;
  }
}

interface ParticleData {
  position: Vector2;
  velocity: Vector2;
  acceleration: Vector2;
  scale: number;
  rotation: number;
  rotationSpeed: number;
  color: Color;
  alpha: number;
  life: number;
  age: number;
} 