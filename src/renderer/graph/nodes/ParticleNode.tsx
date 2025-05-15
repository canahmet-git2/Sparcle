import React from 'react';
import { BaseNode } from './BaseNode';
import { ParticleProperties } from '../../../core/types';
import { NumberInput } from '../../components/inputs/NumberInput';
import { ColorInput } from '../../components/inputs/ColorInput';

interface ParticleNodeProps {
  data: ParticleProperties;
  selected?: boolean;
  onChange?: (data: Partial<ParticleProperties>) => void;
}

const Vector2Input: React.FC<{
  label: string;
  value: { x: number; y: number };
  onChange: (value: { x: number; y: number }) => void;
}> = ({ label, value, onChange }) => (
  <div className="control">
    <label className="control-label">{label}</label>
    <div style={{ display: 'flex', gap: '4px' }}>
      <input
        type="number"
        className="control-input"
        value={value.x}
        onChange={(e) => onChange({ ...value, x: parseFloat(e.target.value) })}
        placeholder="X"
      />
      <input
        type="number"
        className="control-input"
        value={value.y}
        onChange={(e) => onChange({ ...value, y: parseFloat(e.target.value) })}
        placeholder="Y"
      />
    </div>
  </div>
);

export const ParticleNode: React.FC<ParticleNodeProps> = ({
  data,
  selected,
  onChange = () => {}
}) => {
  return (
    <BaseNode title="Particle" color="#2d4d2d" data={data} selected={selected}>
      <NumberInput
        label="Life"
        value={data.life}
        min={0}
        onChange={(life) => onChange({ life })}
      />
      <NumberInput
        label="Speed"
        value={data.speed}
        min={0}
        onChange={(speed) => onChange({ speed })}
      />
      <NumberInput
        label="Size"
        value={data.size}
        min={0}
        onChange={(size) => onChange({ size })}
      />
      <NumberInput
        label="Rotation"
        value={data.rotation}
        min={-360}
        max={360}
        onChange={(rotation) => onChange({ rotation })}
      />
      <NumberInput
        label="Alpha"
        value={data.alpha}
        min={0}
        max={1}
        step={0.1}
        onChange={(alpha) => onChange({ alpha })}
      />
      <ColorInput
        label="Color"
        value={data.color}
        onChange={(color) => onChange({ color })}
      />
    </BaseNode>
  );
}; 