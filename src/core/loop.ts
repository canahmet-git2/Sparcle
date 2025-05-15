import { Vector2, Color } from './types';

interface KeyFrame {
  time: number;
  position?: Vector2;
  scale?: Vector2;
  rotation?: number;
  color?: Color;
  alpha?: number;
}

interface ParticleState {
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

interface LoopSettings {
  duration: number;
  frameRate: number;
  tolerance: number;
}

export class ParticleLoopOptimizer {
  private settings: LoopSettings;
  private states: ParticleState[] = [];
  private keyframes: KeyFrame[] = [];

  constructor(settings: LoopSettings = { duration: 1, frameRate: 60, tolerance: 0.001 }) {
    this.settings = settings;
  }

  /**
   * Pre-warms the particle system to reach steady state
   * @param duration Time to simulate in seconds
   * @param updateFn Function to update particle states
   */
  public preWarmSystem(duration: number, updateFn: (dt: number) => ParticleState[]): void {
    const steps = Math.ceil(duration * this.settings.frameRate);
    const dt = 1 / this.settings.frameRate;

    // Run simulation for pre-warm duration
    for (let i = 0; i < steps; i++) {
      this.states = updateFn(dt);
    }
  }

  /**
   * Samples particle transforms over the loop duration
   */
  public sampleTransforms(): void {
    const { duration, frameRate } = this.settings;
    const dt = 1 / frameRate;
    const totalFrames = Math.ceil(duration * frameRate);

    this.keyframes = [];

    // Sample at each time step
    for (let frame = 0; frame <= totalFrames; frame++) {
      const time = frame * dt;
      
      // Calculate average state of all particles
      const avgState = this.calculateAverageState();
      
      this.keyframes.push({
        time,
        position: avgState.position,
        scale: { x: avgState.scale, y: avgState.scale },
        rotation: avgState.rotation,
        color: avgState.color,
        alpha: avgState.alpha
      });
    }
  }

  /**
   * Optimizes keyframes by removing redundant ones
   */
  public optimizeKeyframes(): void {
    const { tolerance } = this.settings;
    let optimized: KeyFrame[] = [this.keyframes[0]];
    
    for (let i = 1; i < this.keyframes.length - 1; i++) {
      const prev = this.keyframes[i - 1];
      const curr = this.keyframes[i];
      const next = this.keyframes[i + 1];

      // Check if current keyframe is significantly different from linear interpolation
      if (!this.isKeyframeRedundant(prev, curr, next, tolerance)) {
        optimized.push(curr);
      }
    }

    // Always keep the last keyframe
    optimized.push(this.keyframes[this.keyframes.length - 1]);
    this.keyframes = optimized;
  }

  /**
   * Ensures perfect loop by matching start and end states
   */
  public enforceLoopContinuity(): void {
    const firstFrame = this.keyframes[0];
    const lastFrame = this.keyframes[this.keyframes.length - 1];

    // Create interpolation keyframe at the end
    const interpolated: KeyFrame = {
      time: this.settings.duration,
      position: firstFrame.position,
      scale: firstFrame.scale,
      rotation: firstFrame.rotation,
      color: firstFrame.color,
      alpha: firstFrame.alpha
    };

    // Replace last keyframe with interpolated one
    this.keyframes[this.keyframes.length - 1] = interpolated;
  }

  /**
   * Gets the optimized keyframes
   */
  public getKeyframes(): KeyFrame[] {
    return this.keyframes;
  }

  /**
   * Gets the loop settings
   */
  public getSettings(): LoopSettings {
    return { ...this.settings };
  }

  private calculateAverageState(): ParticleState {
    if (this.states.length === 0) {
      return this.getDefaultState();
    }

    const sum = this.states.reduce((acc, state) => ({
      position: {
        x: acc.position.x + state.position.x,
        y: acc.position.y + state.position.y
      },
      scale: acc.scale + state.scale,
      rotation: acc.rotation + state.rotation,
      color: {
        r: acc.color.r + state.color.r,
        g: acc.color.g + state.color.g,
        b: acc.color.b + state.color.b,
        a: acc.color.a + state.color.a
      },
      alpha: acc.alpha + state.alpha,
      velocity: { x: 0, y: 0 },
      acceleration: { x: 0, y: 0 },
      rotationSpeed: 0,
      life: 0,
      age: 0
    }));

    const count = this.states.length;
    return {
      position: {
        x: sum.position.x / count,
        y: sum.position.y / count
      },
      scale: sum.scale / count,
      rotation: sum.rotation / count,
      color: {
        r: sum.color.r / count,
        g: sum.color.g / count,
        b: sum.color.b / count,
        a: sum.color.a / count
      },
      alpha: sum.alpha / count,
      velocity: { x: 0, y: 0 },
      acceleration: { x: 0, y: 0 },
      rotationSpeed: 0,
      life: 1,
      age: 0
    };
  }

  private getDefaultState(): ParticleState {
    return {
      position: { x: 0, y: 0 },
      velocity: { x: 0, y: 0 },
      acceleration: { x: 0, y: 0 },
      scale: 1,
      rotation: 0,
      rotationSpeed: 0,
      color: { r: 1, g: 1, b: 1, a: 1 },
      alpha: 1,
      life: 1,
      age: 0
    };
  }

  private isKeyframeRedundant(
    prev: KeyFrame,
    curr: KeyFrame,
    next: KeyFrame,
    tolerance: number
  ): boolean {
    // Calculate interpolated values
    const t = (curr.time - prev.time) / (next.time - prev.time);
    
    // Check each property for significant deviation
    return (
      this.isVectorInterpolated(prev.position!, curr.position!, next.position!, t, tolerance) &&
      this.isVectorInterpolated(prev.scale!, curr.scale!, next.scale!, t, tolerance) &&
      this.isNumberInterpolated(prev.rotation!, curr.rotation!, next.rotation!, t, tolerance) &&
      this.isColorInterpolated(prev.color!, curr.color!, next.color!, t, tolerance) &&
      this.isNumberInterpolated(prev.alpha!, curr.alpha!, next.alpha!, t, tolerance)
    );
  }

  private isVectorInterpolated(
    start: Vector2,
    current: Vector2,
    end: Vector2,
    t: number,
    tolerance: number
  ): boolean {
    const interpolatedX = start.x + (end.x - start.x) * t;
    const interpolatedY = start.y + (end.y - start.y) * t;
    
    return (
      Math.abs(current.x - interpolatedX) <= tolerance &&
      Math.abs(current.y - interpolatedY) <= tolerance
    );
  }

  private isNumberInterpolated(
    start: number,
    current: number,
    end: number,
    t: number,
    tolerance: number
  ): boolean {
    const interpolated = start + (end - start) * t;
    return Math.abs(current - interpolated) <= tolerance;
  }

  private isColorInterpolated(
    start: Color,
    current: Color,
    end: Color,
    t: number,
    tolerance: number
  ): boolean {
    return (
      this.isNumberInterpolated(start.r, current.r, end.r, t, tolerance) &&
      this.isNumberInterpolated(start.g, current.g, end.g, t, tolerance) &&
      this.isNumberInterpolated(start.b, current.b, end.b, t, tolerance) &&
      this.isNumberInterpolated(start.a, current.a, end.a, t, tolerance)
    );
  }
} 