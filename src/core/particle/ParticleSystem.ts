import { Particle } from './ParticleRenderer';

interface ParticleData {
  position: { x: number; y: number };
  velocity: { x: number; y: number };
  acceleration: { x: number; y: number };
  scale: { x: number; y: number };
  rotation: number;
  color: { r: number; g: number; b: number; a: number };
  alpha: number;
  life: number;
}

interface EmitterData {
  position: { x: number; y: number };
  spawnRate: number;
  spawnCount: number;
  duration: number;
  loop: boolean;
  startLife: number;
  startSpeed: { x: number; y: number };
  startScale: { x: number; y: number };
  startRotation: number;
  startColor: { r: number; g: number; b: number; a: number };
}

interface TransformData {
  translate: { x: number; y: number };
  scale: { x: number; y: number };
  rotate: number;
  skew: { x: number; y: number };
}

export class ParticleSystem {
  private particles: ParticleData[] = [];
  private time: number = 0;
  private spawnAccumulator: number = 0;
  private emitterData: EmitterData | null = null;
  private transformData: any = null;

  public setData(data: { particle?: any; transform?: any; emitter?: any }) {
    try {
      if (data.emitter) {
        this.validateEmitterData(data.emitter);
        this.emitterData = data.emitter;
        console.log('Emitter data updated:', this.emitterData);
      }
      if (data.transform) {
        this.validateTransformData(data.transform);
        this.transformData = data.transform;
        console.log('Transform data updated:', this.transformData);
      }
    } catch (error) {
      console.error('Error setting particle system data:', error);
    }
  }

  private validateEmitterData(data: any): void {
    if (!data.position || typeof data.position.x !== 'number' || typeof data.position.y !== 'number') {
      throw new Error('Invalid emitter position data');
    }
    if (typeof data.spawnRate !== 'number' || data.spawnRate < 0) {
      throw new Error('Invalid spawn rate');
    }
    if (typeof data.spawnCount !== 'number' || data.spawnCount < 0) {
      throw new Error('Invalid spawn count');
    }
    if (typeof data.startLife !== 'number' || data.startLife <= 0) {
      throw new Error('Invalid start life');
    }
  }

  private validateTransformData(data: any): void {
    if (!data.translate || typeof data.translate.x !== 'number' || typeof data.translate.y !== 'number') {
      throw new Error('Invalid transform translation data');
    }
    if (!data.scale || typeof data.scale.x !== 'number' || typeof data.scale.y !== 'number') {
      throw new Error('Invalid transform scale data');
    }
    if (typeof data.rotate !== 'number') {
      throw new Error('Invalid transform rotation data');
    }
  }

  public update(deltaTime: number): void {
    try {
      if (deltaTime < 0 || !isFinite(deltaTime)) {
        console.warn('Invalid delta time:', deltaTime);
        return;
      }

      this.time += deltaTime;
      
      // Spawn new particles
      if (this.emitterData) {
        this.spawnAccumulator += deltaTime;
        const spawnInterval = 1 / this.emitterData.spawnRate;
        
        while (this.spawnAccumulator >= spawnInterval) {
          this.spawnAccumulator -= spawnInterval;
          
          for (let i = 0; i < this.emitterData.spawnCount; i++) {
            try {
              this.particles.push(this.createParticle(this.emitterData));
            } catch (error) {
              console.error('Error creating particle:', error);
            }
          }
        }
      }

      // Update existing particles
      const particleCount = this.particles.length;
      this.particles = this.particles.filter(particle => {
        try {
          // Update life
          particle.life -= deltaTime;
          if (particle.life <= 0) return false;

          // Update position
          particle.velocity.x += particle.acceleration.x * deltaTime;
          particle.velocity.y += particle.acceleration.y * deltaTime;
          particle.position.x += particle.velocity.x * deltaTime;
          particle.position.y += particle.velocity.y * deltaTime;

          // Apply transform if available
          if (this.transformData) {
            // Apply translation
            particle.position.x += this.transformData.translate.x * deltaTime;
            particle.position.y += this.transformData.translate.y * deltaTime;

            // Apply scale
            particle.scale.x *= 1 + (this.transformData.scale.x - 1) * deltaTime;
            particle.scale.y *= 1 + (this.transformData.scale.y - 1) * deltaTime;

            // Apply rotation
            particle.rotation += this.transformData.rotate * deltaTime;

            // Apply skew (as additional velocity)
            particle.velocity.x += this.transformData.skew.x * deltaTime;
            particle.velocity.y += this.transformData.skew.y * deltaTime;
          }

          return true;
        } catch (error) {
          console.error('Error updating particle:', error);
          return false;
        }
      });

      if (this.particles.length !== particleCount) {
        console.log(`Particles updated: ${particleCount} -> ${this.particles.length}`);
      }
    } catch (error) {
      console.error('Error in particle system update:', error);
    }
  }

  public getParticles(): Particle[] {
    return this.particles.map(p => ({
      position: { x: p.position.x, y: p.position.y },
      scale: { x: p.scale.x, y: p.scale.y },
      rotation: p.rotation,
      color: { ...p.color },
      alpha: p.alpha
    }));
  }

  private createParticle(emitter: EmitterData): ParticleData {
    if (!emitter) {
      throw new Error('Emitter data is required to create a particle');
    }

    return {
      position: { ...emitter.position },
      velocity: { ...emitter.startSpeed },
      acceleration: { x: 0, y: 0 },
      scale: { ...emitter.startScale },
      rotation: emitter.startRotation,
      color: { ...emitter.startColor },
      alpha: emitter.startColor.a,
      life: emitter.startLife
    };
  }
} 