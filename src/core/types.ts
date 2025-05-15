export interface Vector2 {
  x: number;
  y: number;
}

export interface Color {
  r: number;
  g: number;
  b: number;
  a: number;
}

export interface ParticleProperties {
  position: Vector2;
  velocity: Vector2;
  acceleration: Vector2;
  scale: Vector2;
  rotation: number;
  color: Color;
  life: number;
  alpha: number;
}

export interface EmitterProperties {
  position: Vector2;
  spawnRate: number;
  spawnCount: number;
  duration: number;
  loop: boolean;
  startLife: number;
  startSpeed: Vector2;
  startScale: Vector2;
  startRotation: number;
  startColor: Color;
}

export interface TransformProperties {
  translate: Vector2;
  scale: Vector2;
  rotate: number;
  skew: Vector2;
}

export type NodeType = 'emitter' | 'particle' | 'transform' | 'output'; 