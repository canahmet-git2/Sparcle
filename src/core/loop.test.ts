import { ParticleLoopOptimizer } from './loop';

describe('ParticleLoopOptimizer', () => {
  let optimizer: ParticleLoopOptimizer;

  beforeEach(() => {
    optimizer = new ParticleLoopOptimizer({
      duration: 1,
      frameRate: 60,
      tolerance: 0.001
    });
  });

  describe('preWarmSystem', () => {
    it('should run simulation for specified duration', () => {
      const updateFn = jest.fn().mockReturnValue([{
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
      }]);

      optimizer.preWarmSystem(1, updateFn);
      expect(updateFn).toHaveBeenCalledTimes(60); // 1 second * 60 fps
    });
  });

  describe('sampleTransforms', () => {
    it('should generate correct number of keyframes', () => {
      optimizer.preWarmSystem(1, () => [{
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
      }]);

      optimizer.sampleTransforms();
      expect(optimizer.getKeyframes()).toHaveLength(61); // 60 frames + 1 (inclusive of end)
    });
  });

  describe('optimizeKeyframes', () => {
    it('should remove redundant keyframes', () => {
      // Setup linear motion keyframes
      const keyframes = Array.from({ length: 61 }, (_, i) => ({
        time: i / 60,
        position: { x: i, y: i },
        scale: { x: 1, y: 1 },
        rotation: i,
        color: { r: 1, g: 1, b: 1, a: 1 },
        alpha: 1
      }));

      optimizer['keyframes'] = keyframes;
      optimizer.optimizeKeyframes();

      // Should only keep start, end, and any non-linear points
      expect(optimizer.getKeyframes().length).toBeLessThan(keyframes.length);
    });
  });

  describe('enforceLoopContinuity', () => {
    it('should make end state match start state', () => {
      const startState = {
        time: 0,
        position: { x: 0, y: 0 },
        scale: { x: 1, y: 1 },
        rotation: 0,
        color: { r: 1, g: 1, b: 1, a: 1 },
        alpha: 1
      };

      const endState = {
        time: 1,
        position: { x: 10, y: 10 },
        scale: { x: 2, y: 2 },
        rotation: 45,
        color: { r: 0, g: 0, b: 0, a: 1 },
        alpha: 0.5
      };

      optimizer['keyframes'] = [startState, endState];
      optimizer.enforceLoopContinuity();

      const finalKeyframes = optimizer.getKeyframes();
      expect(finalKeyframes[finalKeyframes.length - 1]).toEqual({
        ...startState,
        time: 1
      });
    });
  });
}); 