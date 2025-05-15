import React, { useState, useRef, useEffect } from 'react';
import { NumberInput } from './NumberInput';

interface Color {
  r: number;
  g: number;
  b: number;
  a: number;
}

interface ColorInputProps {
  label: string;
  value: Color;
  onChange: (value: Color) => void;
}

export const ColorInput: React.FC<ColorInputProps> = ({
  label,
  value,
  onChange
}) => {
  const [isPickerOpen, setIsPickerOpen] = useState(false);
  const pickerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        setIsPickerOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const rgbaToHex = (color: Color) => {
    const toHex = (n: number) => {
      const hex = Math.round(n * 255).toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    };
    return `#${toHex(color.r)}${toHex(color.g)}${toHex(color.b)}`;
  };

  const hexToRgba = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16) / 255,
      g: parseInt(result[2], 16) / 255,
      b: parseInt(result[3], 16) / 255,
      a: value.a
    } : value;
  };

  return (
    <div className="color-input" ref={pickerRef}>
      <label>{label}</label>
      <div className="color-preview" onClick={() => setIsPickerOpen(!isPickerOpen)}>
        <div
          className="color-swatch"
          style={{
            backgroundColor: `rgba(${value.r * 255}, ${value.g * 255}, ${value.b * 255}, ${value.a})`
          }}
        />
        <input
          type="color"
          value={rgbaToHex(value)}
          onChange={e => onChange(hexToRgba(e.target.value))}
        />
      </div>
      {isPickerOpen && (
        <div className="color-picker">
          <NumberInput
            label="R"
            value={value.r}
            onChange={r => onChange({ ...value, r })}
            min={0}
            max={1}
            step={0.01}
          />
          <NumberInput
            label="G"
            value={value.g}
            onChange={g => onChange({ ...value, g })}
            min={0}
            max={1}
            step={0.01}
          />
          <NumberInput
            label="B"
            value={value.b}
            onChange={b => onChange({ ...value, b })}
            min={0}
            max={1}
            step={0.01}
          />
          <NumberInput
            label="A"
            value={value.a}
            onChange={a => onChange({ ...value, a })}
            min={0}
            max={1}
            step={0.01}
          />
        </div>
      )}
    </div>
  );
}; 