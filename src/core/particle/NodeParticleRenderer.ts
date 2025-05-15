import * as PIXI from 'pixi.js';
import { ParticleNodeSystem } from './ParticleNodeSystem';
import { RendererNode } from './ParticleNodeSystem';

export class NodeParticleRenderer {
  private app: PIXI.Application;
  private particleContainers: Map<string, PIXI.ParticleContainer> = new Map();
  private trailContainers: Map<string, PIXI.Graphics> = new Map();
  private textures: Map<string, PIXI.Texture> = new Map();
  private initialized: boolean = false;

  constructor(canvas: HTMLCanvasElement) {
    // Initialize PIXI Application with optimized settings
    this.app = new PIXI.Application({
      view: canvas,
      width: canvas.clientWidth || 800,
      height: canvas.clientHeight || 600,
      resolution: window.devicePixelRatio || 1,
      autoDensity: true,
      backgroundColor: 0x000000,
      antialias: true,
      powerPreference: 'high-performance'
    });

    // Create default texture
    const defaultTexture = PIXI.Texture.from(PIXI.Texture.WHITE);
    this.textures.set('default', defaultTexture);

    this.initialized = true;
  }

  public resize(width: number, height: number): void {
    if (!this.initialized) return;
    this.app.renderer.resize(width, height);
  }

  public updateParticles(system: ParticleNodeSystem): void {
    if (!this.initialized) return;

    // Get all renderer nodes from the system
    const rendererNodes = Array.from(system.getNodes().values())
      .filter(node => node.type === 'renderer') as RendererNode[];

    // Create or update containers for each renderer node
    rendererNodes.forEach(renderer => {
      let container = this.particleContainers.get(renderer.id);
      if (!container) {
        container = new PIXI.ParticleContainer(10000, {
          position: true,
          rotation: true,
          scale: true,
          alpha: true,
          uvs: true,
        });
        this.particleContainers.set(renderer.id, container);
        this.app.stage.addChild(container);
      }

      // Set blend mode
      switch (renderer.blendMode) {
        case 'additive':
          container.blendMode = PIXI.BLEND_MODES.ADD;
          break;
        case 'multiply':
          container.blendMode = PIXI.BLEND_MODES.MULTIPLY;
          break;
        case 'screen':
          container.blendMode = PIXI.BLEND_MODES.SCREEN;
          break;
        default:
          container.blendMode = PIXI.BLEND_MODES.NORMAL;
      }

      // Load texture if specified
      if (renderer.texture && !this.textures.has(renderer.texture)) {
        const texture = PIXI.Texture.from(renderer.texture);
        this.textures.set(renderer.texture, texture);
      }

      // Handle special material types
      if (renderer.material) {
        switch (renderer.material.type) {
          case 'trail':
          case 'ribbon':
            this.updateTrails(renderer, system.getParticles());
            break;
          default:
            this.updateSprites(renderer, system.getParticles(), container);
        }
      } else {
        this.updateSprites(renderer, system.getParticles(), container);
      }
    });
  }

  private updateSprites(
    renderer: RendererNode,
    particles: any[],
    container: PIXI.ParticleContainer
  ): void {
    // Sort particles if needed
    if (renderer.sortMode === 'byAge') {
      particles.sort((a, b) => b.age - a.age);
    }

    // Remove excess sprites
    while (container.children.length > particles.length) {
      const sprite = container.children[container.children.length - 1];
      container.removeChild(sprite);
      sprite.destroy();
    }

    // Add or update sprites
    const texture = renderer.texture 
      ? this.textures.get(renderer.texture)
      : this.textures.get('default');

    particles.forEach((particle, i) => {
      let sprite = container.children[i] as PIXI.Sprite;
      
      if (!sprite) {
        sprite = new PIXI.Sprite(texture);
        container.addChild(sprite);
      }

      // Update sprite properties
      sprite.position.set(particle.position.x, particle.position.y);
      sprite.scale.set(particle.scale, particle.scale);
      sprite.rotation = particle.rotation;
      sprite.alpha = particle.alpha;

      // Apply color tint
      sprite.tint = (
        (Math.round(particle.color.r * 255) << 16) +
        (Math.round(particle.color.g * 255) << 8) +
        Math.round(particle.color.b * 255)
      );

      // Handle different render modes
      if (renderer.renderMode === 'stretched') {
        const speed = Math.sqrt(
          particle.velocity.x * particle.velocity.x +
          particle.velocity.y * particle.velocity.y
        );
        sprite.scale.x *= speed * 0.1; // Adjust stretch factor as needed
      }
    });
  }

  private updateTrails(renderer: RendererNode, particles: any[]): void {
    let trailContainer = this.trailContainers.get(renderer.id);
    if (!trailContainer) {
      trailContainer = new PIXI.Graphics();
      this.trailContainers.set(renderer.id, trailContainer);
      this.app.stage.addChild(trailContainer);
    }

    trailContainer.clear();

    const params = renderer.material?.params || {};
    const segments = params.segments || 10;
    const fadeOut = params.fadeOut || false;
    const fadeOutLength = params.fadeOutLength || 1;

    particles.forEach(particle => {
      const points: number[] = [];
      const trail = particle.trail || [];

      // Add current position to trail
      trail.unshift({ x: particle.position.x, y: particle.position.y });
      
      // Limit trail length
      while (trail.length > segments) {
        trail.pop();
      }

      // Draw trail
      if (trail.length >= 2) {
        trailContainer.lineStyle({
          width: particle.scale * 2,
          color: (
            (Math.round(particle.color.r * 255) << 16) +
            (Math.round(particle.color.g * 255) << 8) +
            Math.round(particle.color.b * 255)
          ),
          alpha: fadeOut ? particle.alpha * (1 - particle.age / particle.life) : particle.alpha
        });

        trailContainer.moveTo(trail[0].x, trail[0].y);
        for (let i = 1; i < trail.length; i++) {
          trailContainer.lineTo(trail[i].x, trail[i].y);
        }
      }

      // Store updated trail
      particle.trail = trail;
    });
  }

  public destroy(): void {
    if (this.initialized) {
      // Destroy all textures
      this.textures.forEach(texture => texture.destroy());
      this.textures.clear();

      // Destroy all containers
      this.particleContainers.forEach(container => container.destroy());
      this.particleContainers.clear();

      this.trailContainers.forEach(container => container.destroy());
      this.trailContainers.clear();

      // Destroy PIXI application
      this.app.destroy(true);
      this.initialized = false;
    }
  }
} 