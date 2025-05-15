import React from 'react';
import { BaseNode } from './BaseNode';
import { EmitterProperties } from '../../../core/types';
import { Node, Socket } from 'rete';
import { Vector2Input } from '../../components/inputs/Vector2Input';
import { NumberInput } from '../../components/inputs/NumberInput';
import { ColorInput } from '../../components/inputs/ColorInput';
import { SelectInput } from '../../components/inputs/SelectInput';

interface EmitterNodeProps {
  data: EmitterProperties;
  selected?: boolean;
  onChange?: (data: Partial<EmitterProperties>) => void;
}

export class EmitterNode extends Node {
  constructor() {
    super('Emitter');
    this.type = 'emitter';

    // Add output socket for particles
    this.addOutput('output', new Socket('particle'));

    // Initialize default data
    this.data = {
      position: { x: 0, y: 0 },
      spawnRate: 10,
      spawnCount: 1,
      burstMode: false,
      burstCount: 10,
      burstInterval: 1,
      shape: 'point',
      shapeParams: {},
      initialProperties: {
        life: { min: 1, max: 2 },
        speed: { min: 1, max: 2 },
        direction: { min: 0, max: 360 },
        size: { min: 1, max: 1 },
        rotation: { min: 0, max: 0 },
        color: { r: 1, g: 1, b: 1, a: 1 },
        alpha: 1
      }
    };
  }

  render() {
    return (
      <BaseNode title="Emitter" color="#2d4d2d" data={this.data} selected={this.selected}>
        <Vector2Input
          label="Position"
          value={this.data.position}
          onChange={(position) => this.update({ position })}
        />
        <NumberInput
          label="Spawn Rate"
          value={this.data.spawnRate}
          min={0}
          onChange={(spawnRate) => this.update({ spawnRate })}
        />
        <NumberInput
          label="Spawn Count"
          value={this.data.spawnCount}
          min={1}
          onChange={(spawnCount) => this.update({ spawnCount })}
        />
        <div className="checkbox-control">
          <label>
            <input
              type="checkbox"
              checked={this.data.burstMode}
              onChange={(e) => this.update({ burstMode: e.target.checked })}
            />
            Burst Mode
          </label>
        </div>
        {this.data.burstMode && (
          <>
            <NumberInput
              label="Burst Count"
              value={this.data.burstCount}
              min={1}
              onChange={(burstCount) => this.update({ burstCount })}
            />
            <NumberInput
              label="Burst Interval"
              value={this.data.burstInterval}
              min={0.1}
              step={0.1}
              onChange={(burstInterval) => this.update({ burstInterval })}
            />
          </>
        )}
        <SelectInput
          label="Shape"
          value={this.data.shape}
          options={[
            { value: 'point', label: 'Point' },
            { value: 'circle', label: 'Circle' },
            { value: 'line', label: 'Line' },
            { value: 'rectangle', label: 'Rectangle' }
          ]}
          onChange={(shape) => {
            const shapeParams = {};
            switch (shape) {
              case 'circle':
                shapeParams.radius = 50;
                break;
              case 'line':
                shapeParams.width = 100;
                shapeParams.angle = 0;
                break;
              case 'rectangle':
                shapeParams.width = 100;
                shapeParams.height = 100;
                break;
            }
            this.update({ shape, shapeParams });
          }}
        />
        {this.data.shape === 'circle' && (
          <NumberInput
            label="Radius"
            value={this.data.shapeParams.radius}
            min={0}
            onChange={(radius) => this.update({
              shapeParams: { ...this.data.shapeParams, radius }
            })}
          />
        )}
        {this.data.shape === 'line' && (
          <>
            <NumberInput
              label="Length"
              value={this.data.shapeParams.width}
              min={0}
              onChange={(width) => this.update({
                shapeParams: { ...this.data.shapeParams, width }
              })}
            />
            <NumberInput
              label="Angle"
              value={this.data.shapeParams.angle}
              min={0}
              max={360}
              onChange={(angle) => this.update({
                shapeParams: { ...this.data.shapeParams, angle }
              })}
            />
          </>
        )}
        {this.data.shape === 'rectangle' && (
          <>
            <NumberInput
              label="Width"
              value={this.data.shapeParams.width}
              min={0}
              onChange={(width) => this.update({
                shapeParams: { ...this.data.shapeParams, width }
              })}
            />
            <NumberInput
              label="Height"
              value={this.data.shapeParams.height}
              min={0}
              onChange={(height) => this.update({
                shapeParams: { ...this.data.shapeParams, height }
              })}
            />
          </>
        )}
        <h4>Initial Properties</h4>
        <NumberInput
          label="Life Min"
          value={this.data.initialProperties.life.min}
          min={0}
          onChange={(min) => this.update({
            initialProperties: {
              ...this.data.initialProperties,
              life: { ...this.data.initialProperties.life, min }
            }
          })}
        />
        <NumberInput
          label="Life Max"
          value={this.data.initialProperties.life.max}
          min={0}
          onChange={(max) => this.update({
            initialProperties: {
              ...this.data.initialProperties,
              life: { ...this.data.initialProperties.life, max }
            }
          })}
        />
        <NumberInput
          label="Speed Min"
          value={this.data.initialProperties.speed.min}
          min={0}
          onChange={(min) => this.update({
            initialProperties: {
              ...this.data.initialProperties,
              speed: { ...this.data.initialProperties.speed, min }
            }
          })}
        />
        <NumberInput
          label="Speed Max"
          value={this.data.initialProperties.speed.max}
          min={0}
          onChange={(max) => this.update({
            initialProperties: {
              ...this.data.initialProperties,
              speed: { ...this.data.initialProperties.speed, max }
            }
          })}
        />
        <NumberInput
          label="Direction Min"
          value={this.data.initialProperties.direction.min}
          min={0}
          max={360}
          onChange={(min) => this.update({
            initialProperties: {
              ...this.data.initialProperties,
              direction: { ...this.data.initialProperties.direction, min }
            }
          })}
        />
        <NumberInput
          label="Direction Max"
          value={this.data.initialProperties.direction.max}
          min={0}
          max={360}
          onChange={(max) => this.update({
            initialProperties: {
              ...this.data.initialProperties,
              direction: { ...this.data.initialProperties.direction, max }
            }
          })}
        />
        <NumberInput
          label="Size Min"
          value={this.data.initialProperties.size.min}
          min={0}
          onChange={(min) => this.update({
            initialProperties: {
              ...this.data.initialProperties,
              size: { ...this.data.initialProperties.size, min }
            }
          })}
        />
        <NumberInput
          label="Size Max"
          value={this.data.initialProperties.size.max}
          min={0}
          onChange={(max) => this.update({
            initialProperties: {
              ...this.data.initialProperties,
              size: { ...this.data.initialProperties.size, max }
            }
          })}
        />
        <NumberInput
          label="Rotation Min"
          value={this.data.initialProperties.rotation.min}
          min={-360}
          max={360}
          onChange={(min) => this.update({
            initialProperties: {
              ...this.data.initialProperties,
              rotation: { ...this.data.initialProperties.rotation, min }
            }
          })}
        />
        <NumberInput
          label="Rotation Max"
          value={this.data.initialProperties.rotation.max}
          min={-360}
          max={360}
          onChange={(max) => this.update({
            initialProperties: {
              ...this.data.initialProperties,
              rotation: { ...this.data.initialProperties.rotation, max }
            }
          })}
        />
        <ColorInput
          label="Color"
          value={this.data.initialProperties.color}
          onChange={(color) => this.update({
            initialProperties: {
              ...this.data.initialProperties,
              color
            }
          })}
        />
        <NumberInput
          label="Alpha"
          value={this.data.initialProperties.alpha}
          min={0}
          max={1}
          step={0.1}
          onChange={(alpha) => this.update({
            initialProperties: {
              ...this.data.initialProperties,
              alpha
            }
          })}
        />
      </BaseNode>
    );
  }

  private update(newData: Partial<EmitterProperties>) {
    this.data = {
      ...this.data,
      ...newData
    };
    this.update();
  }
} 