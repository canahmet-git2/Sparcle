import React from 'react';
import { BaseNode } from './BaseNode';
import { NumberInput } from '../../components/inputs/NumberInput';
import { SelectInput } from '../../components/inputs/SelectInput';

interface OutputProperties {
  blendMode: 'normal' | 'additive' | 'multiply';
  optimizeMesh: boolean;
  loopDuration: number;
}

interface OutputNodeProps {
  data: OutputProperties;
  selected?: boolean;
  onChange?: (data: Partial<OutputProperties>) => void;
}

export const OutputNode: React.FC<OutputNodeProps> = ({ 
  data,
  selected,
  onChange = () => {}
}) => {
  return (
    <BaseNode title="Output" color="#4d4d2d" data={data} selected={selected}>
      <SelectInput
        label="Blend Mode"
        value={data.blendMode}
        options={[
          { value: 'normal', label: 'Normal' },
          { value: 'additive', label: 'Additive' },
          { value: 'multiply', label: 'Multiply' }
        ]}
        onChange={(blendMode) => onChange({ blendMode: blendMode as OutputProperties['blendMode'] })}
      />
      <div className="checkbox-control">
        <label>
          <input
            type="checkbox"
            checked={data.optimizeMesh}
            onChange={(e) => onChange({ optimizeMesh: e.target.checked })}
          />
          Optimize Mesh
        </label>
      </div>
      <NumberInput
        label="Loop Duration"
        value={data.loopDuration}
        min={0}
        step={0.1}
        onChange={(loopDuration) => onChange({ loopDuration })}
      />
    </BaseNode>
  );
}; 