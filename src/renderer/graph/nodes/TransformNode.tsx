import React from 'react';
import { BaseNode } from './BaseNode';
import { TransformProperties } from '../../../core/types';
import { NumberInput } from '../../components/inputs/NumberInput';

interface TransformNodeProps {
  data: TransformProperties;
  selected?: boolean;
  onChange?: (data: Partial<TransformProperties>) => void;
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

export const TransformNode: React.FC<TransformNodeProps> = ({ 
  data,
  selected,
  onChange = () => {}
}) => {
  return (
    <BaseNode title="Transform" color="#4d2d4d" data={data} selected={selected}>
      <NumberInput
        label="Position X"
        value={data.position.x}
        onChange={(x) => onChange({ position: { ...data.position, x } })}
      />
      <NumberInput
        label="Position Y"
        value={data.position.y}
        onChange={(y) => onChange({ position: { ...data.position, y } })}
      />
      <NumberInput
        label="Scale X"
        value={data.scale.x}
        min={0}
        onChange={(x) => onChange({ scale: { ...data.scale, x } })}
      />
      <NumberInput
        label="Scale Y"
        value={data.scale.y}
        min={0}
        onChange={(y) => onChange({ scale: { ...data.scale, y } })}
      />
      <NumberInput
        label="Rotation"
        value={data.rotation}
        min={-360}
        max={360}
        onChange={(rotation) => onChange({ rotation })}
      />
    </BaseNode>
  );
}; 