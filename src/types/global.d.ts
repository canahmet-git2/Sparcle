import { ParticleNodeSystem } from '../core/particle/ParticleNodeSystem';

declare global {
  interface Window {
    particleSystem: ParticleNodeSystem | null;
  }
} 