import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { Vector2Input } from '../Vector2Input';

describe('Vector2Input', () => {
  const defaultProps = {
    label: 'Test Vector',
    value: { x: 0, y: 0 },
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with default values', () => {
    render(<Vector2Input {...defaultProps} />);
    
    expect(screen.getByText('Test Vector')).toBeInTheDocument();
    expect(screen.getByLabelText('X')).toHaveValue(0);
    expect(screen.getByLabelText('Y')).toHaveValue(0);
  });

  it('calls onChange when X value changes', () => {
    render(<Vector2Input {...defaultProps} />);
    
    const xInput = screen.getByLabelText('X');
    fireEvent.change(xInput, { target: { value: '5' } });
    
    expect(defaultProps.onChange).toHaveBeenCalledWith({ x: 5, y: 0 });
  });

  it('calls onChange when Y value changes', () => {
    render(<Vector2Input {...defaultProps} />);
    
    const yInput = screen.getByLabelText('Y');
    fireEvent.change(yInput, { target: { value: '5' } });
    
    expect(defaultProps.onChange).toHaveBeenCalledWith({ x: 0, y: 5 });
  });

  it('respects min and max props', () => {
    render(
      <Vector2Input
        {...defaultProps}
        min={-10}
        max={10}
      />
    );
    
    const xInput = screen.getByLabelText('X');
    const yInput = screen.getByLabelText('Y');
    
    fireEvent.change(xInput, { target: { value: '15' } });
    expect(defaultProps.onChange).toHaveBeenCalledWith({ x: 10, y: 0 });
    
    fireEvent.change(yInput, { target: { value: '-15' } });
    expect(defaultProps.onChange).toHaveBeenCalledWith({ x: 0, y: -10 });
  });

  it('handles step prop', () => {
    render(
      <Vector2Input
        {...defaultProps}
        step={0.5}
      />
    );
    
    const xInput = screen.getByLabelText('X');
    expect(xInput).toHaveAttribute('step', '0.5');
  });
}); 