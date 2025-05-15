import React from 'react';
import { BaseNode } from './BaseNode';
import { SelectInput } from '../../components/inputs/SelectInput';
import { NumberInput } from '../../components/inputs/NumberInput';
import { Node, Socket } from 'rete';

interface RendererProperties {
  blendMode: 'normal' | 'additive' | 'multiply' | 'screen';
  texture?: string;
  material?: {
    type: 'sprite' | 'trail' | 'ribbon';
    params: {
      length?: number;
      segments?: number;
      fadeOut?: boolean;
      fadeOutLength?: number;
    };
  };
  sortMode: 'none' | 'byDistance' | 'byAge';
  renderMode: '2d' | 'billboard' | 'stretched';
}

interface RendererNodeProps {
  data: RendererProperties;
  selected?: boolean;
  onChange?: (data: Partial<RendererProperties>) => void;
}

export class RendererNode extends Node {
  constructor() {
    super('Renderer');
    this.type = 'renderer';

    // Add input socket for particles
    this.addInput('input', new Socket('particle'));

    // Initialize default data
    this.data = {
      blendMode: 'normal',
      sortMode: 'none',
      renderMode: '2d',
      texture: 'default',
      material: {
        type: 'sprite',
        params: {
          length: 10,
          segments: 8,
          fadeOut: true,
          fadeOutLength: 0.5
        }
      }
    };
  }

  render() {
    return (
      <BaseNode title="Renderer" color="#4d2d4d" data={this.data} selected={this.selected}>
        <div className="renderer-controls">
          <SelectInput
            label="Blend Mode"
            value={this.data.blendMode}
            options={[
              { value: 'normal', label: 'Normal' },
              { value: 'additive', label: 'Additive' },
              { value: 'multiply', label: 'Multiply' },
              { value: 'screen', label: 'Screen' }
            ]}
            onChange={(blendMode) => this.update({ blendMode })}
          />

          <SelectInput
            label="Material Type"
            value={this.data.material.type}
            options={[
              { value: 'sprite', label: 'Sprite' },
              { value: 'trail', label: 'Trail' },
              { value: 'ribbon', label: 'Ribbon' }
            ]}
            onChange={(type) => this.update({
              material: { ...this.data.material, type }
            })}
          />

          {(this.data.material.type === 'trail' || this.data.material.type === 'ribbon') && (
            <>
              <NumberInput
                label="Length"
                value={this.data.material.params.length}
                min={1}
                onChange={(length) => this.update({
                  material: {
                    ...this.data.material,
                    params: { ...this.data.material.params, length }
                  }
                })}
              />
              <NumberInput
                label="Segments"
                value={this.data.material.params.segments}
                min={2}
                onChange={(segments) => this.update({
                  material: {
                    ...this.data.material,
                    params: { ...this.data.material.params, segments }
                  }
                })}
              />
              <div className="checkbox-control">
                <label>
                  <input
                    type="checkbox"
                    checked={this.data.material.params.fadeOut}
                    onChange={(e) => this.update({
                      material: {
                        ...this.data.material,
                        params: { ...this.data.material.params, fadeOut: e.target.checked }
                      }
                    })}
                  />
                  Fade Out
                </label>
              </div>
              {this.data.material.params.fadeOut && (
                <NumberInput
                  label="Fade Length"
                  value={this.data.material.params.fadeOutLength}
                  min={0}
                  max={1}
                  step={0.1}
                  onChange={(fadeOutLength) => this.update({
                    material: {
                      ...this.data.material,
                      params: { ...this.data.material.params, fadeOutLength }
                    }
                  })}
                />
              )}
            </>
          )}

          <SelectInput
            label="Sort Mode"
            value={this.data.sortMode}
            options={[
              { value: 'none', label: 'None' },
              { value: 'byDistance', label: 'By Distance' },
              { value: 'byAge', label: 'By Age' }
            ]}
            onChange={(sortMode) => this.update({ sortMode })}
          />

          <SelectInput
            label="Render Mode"
            value={this.data.renderMode}
            options={[
              { value: '2d', label: '2D' },
              { value: 'billboard', label: 'Billboard' },
              { value: 'stretched', label: 'Stretched' }
            ]}
            onChange={(renderMode) => this.update({ renderMode })}
          />
        </div>
      </BaseNode>
    );
  }

  private update(newData: Partial<RendererProperties>) {
    this.data = {
      ...this.data,
      ...newData
    };
    this.update();
  }
} 