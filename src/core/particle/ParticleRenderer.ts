import * as PIXI from 'pixi.js';

export interface Particle {
  position: { x: number; y: number };
  scale: { x: number; y: number };
  rotation: number;
  color: { r: number; g: number; b: number; a: number };
  alpha: number;
}

export class ParticleRenderer {
  private app: PIXI.Application;
  private particleContainer: PIXI.ParticleContainer;
  private gridGraphics: PIXI.Graphics;
  private particles: PIXI.Sprite[];
  private initialized: boolean = false;

  constructor(canvas: HTMLCanvasElement) {
    // Initialize PIXI Application with safe defaults
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

    // Create particle container with optimized settings
    this.particleContainer = new PIXI.ParticleContainer(10000, {
      position: true,
      rotation: true,
      scale: true,
      alpha: true,
      uvs: true,
    });

    // Create grid graphics
    this.gridGraphics = new PIXI.Graphics();
    
    // Add containers to stage
    this.app.stage.addChild(this.gridGraphics);
    this.app.stage.addChild(this.particleContainer);

    // Initialize particles array
    this.particles = [];
    
    // Mark as initialized
    this.initialized = true;
  }

  public resize(width: number, height: number): void {
    if (!this.initialized) return;
    
    this.app.renderer.resize(width, height);
    this.drawGrid(20); // Redraw grid with default size
  }

  public drawGrid(size: number): void {
    if (!this.initialized || !this.app.screen) return;
    
    const width = this.app.screen.width;
    const height = this.app.screen.height;

    this.gridGraphics.clear();
    this.gridGraphics.lineStyle(1, 0x333333, 0.5);

    // Draw vertical lines
    for (let x = 0; x <= width; x += size) {
      this.gridGraphics.moveTo(x, 0);
      this.gridGraphics.lineTo(x, height);
    }

    // Draw horizontal lines
    for (let y = 0; y <= height; y += size) {
      this.gridGraphics.moveTo(0, y);
      this.gridGraphics.lineTo(width, y);
    }

    // Draw center lines
    this.gridGraphics.lineStyle(2, 0x444444, 0.8);
    this.gridGraphics.moveTo(width / 2, 0);
    this.gridGraphics.lineTo(width / 2, height);
    this.gridGraphics.moveTo(0, height / 2);
    this.gridGraphics.lineTo(width, height / 2);
  }

  public updateParticles(particles: Particle[]): void {
    if (!this.initialized) return;

    // Remove excess particles
    while (this.particles.length > particles.length) {
      const particle = this.particles.pop();
      if (particle) {
        this.particleContainer.removeChild(particle);
        particle.destroy();
      }
    }

    // Add or update particles
    particles.forEach((data, i) => {
      let particle = this.particles[i];
      
      // Create new particle if needed
      if (!particle) {
        particle = PIXI.Sprite.from(PIXI.Texture.WHITE);
        this.particles[i] = particle;
        this.particleContainer.addChild(particle);
      }

      // Update particle properties
      particle.position.set(data.position.x, data.position.y);
      particle.scale.set(data.scale.x, data.scale.y);
      particle.rotation = data.rotation;
      particle.alpha = data.alpha;
      particle.tint = (
        (Math.round(data.color.r * 255) << 16) +
        (Math.round(data.color.g * 255) << 8) +
        Math.round(data.color.b * 255)
      );
    });
  }

  public setBlendMode(mode: 'normal' | 'additive' | 'multiply'): void {
    if (!this.initialized) return;

    switch (mode) {
      case 'normal':
        this.particleContainer.blendMode = PIXI.BLEND_MODES.NORMAL;
        break;
      case 'additive':
        this.particleContainer.blendMode = PIXI.BLEND_MODES.ADD;
        break;
      case 'multiply':
        this.particleContainer.blendMode = PIXI.BLEND_MODES.MULTIPLY;
        break;
    }
  }

  public destroy(): void {
    if (this.initialized) {
      this.app.destroy(true);
      this.particles = [];
      this.initialized = false;
    }
  }
} 