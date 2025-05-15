import React from 'react';
import { NumberInput } from './NumberInput';

interface Vector2InputProps {
  label: string;
  value: { x: number; y: number };
  onChange: (value: { x: number; y: number }) => void;
  min?: number;
  max?: number;
  step?: number;
}

export const Vector2Input: React.FC<Vector2InputProps> = ({
  label,
  value,
  onChange,
  min = -Infinity,
  max = Infinity,
  step = 1
}) => {
  const handleChange = (axis: 'x' | 'y', inputValue: string) => {
    const newValue = parseFloat(inputValue);
    if (!isNaN(newValue)) {
      const clampedValue = Math.min(max, Math.max(min, newValue));
      onChange({
        ...value,
        [axis]: clampedValue
      });
    }
  };

  return (
    <div className="vector2-input">
      <label>{label}</label>
      <div className="vector2-fields">
        <div className="number-input">
          <label htmlFor="x-input">X</label>
          <input
            id="x-input"
            type="number"
            value={value.x}
            onChange={e => handleChange('x', e.target.value)}
            min={min}
            max={max}
            step={step}
          />
        </div>
        <div className="number-input">
          <label htmlFor="y-input">Y</label>
          <input
            id="y-input"
            type="number"
            value={value.y}
            onChange={e => handleChange('y', e.target.value)}
            min={min}
            max={max}
            step={step}
          />
        </div>
      </div>
    </div>
  );
}; 