import { Node, Socket } from 'rete';
import { Vector2Input } from '../../components/inputs/Vector2Input';
import { NumberInput } from '../../components/inputs/NumberInput';
import { SelectInput } from '../../components/inputs/SelectInput';

export class ForceFieldNode extends Node {
  constructor() {
    super('Force Field');
    this.type = 'forceField';

    // Add input and output sockets
    this.addInput('input', new Socket('particle'));
    this.addOutput('output', new Socket('particle'));

    // Initialize default data
    this.data = {
      position: { x: 0, y: 0 },
      strength: 1,
      falloff: 'none',
      direction: 'inward',
      customAngle: 0,
      shape: 'point',
      shapeParams: {}
    };
  }

  render() {
    return (
      <div className="node force-field-node">
        <div className="node-header">
          <h3>Force Field</h3>
        </div>
        <div className="node-content">
          <Vector2Input
            label="Position"
            value={this.data.position}
            onChange={position => this.update({ position })}
          />
          <NumberInput
            label="Strength"
            value={this.data.strength}
            onChange={strength => this.update({ strength })}
          />
          <SelectInput
            label="Falloff"
            value={this.data.falloff}
            options={[
              { value: 'none', label: 'None' },
              { value: 'linear', label: 'Linear' },
              { value: 'quadratic', label: 'Quadratic' }
            ]}
            onChange={falloff => this.update({ falloff })}
          />
          <SelectInput
            label="Direction"
            value={this.data.direction}
            options={[
              { value: 'inward', label: 'Inward' },
              { value: 'outward', label: 'Outward' },
              { value: 'clockwise', label: 'Clockwise' },
              { value: 'counterclockwise', label: 'Counter-Clockwise' },
              { value: 'custom', label: 'Custom Angle' }
            ]}
            onChange={direction => this.update({ direction })}
          />
          {this.data.direction === 'custom' && (
            <NumberInput
              label="Angle"
              value={this.data.customAngle}
              min={0}
              max={360}
              onChange={customAngle => this.update({ customAngle })}
            />
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
            onChange={shape => {
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
              onChange={radius => this.update({
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
                onChange={width => this.update({
                  shapeParams: { ...this.data.shapeParams, width }
                })}
              />
              <NumberInput
                label="Angle"
                value={this.data.shapeParams.angle}
                min={0}
                max={360}
                onChange={angle => this.update({
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
                onChange={width => this.update({
                  shapeParams: { ...this.data.shapeParams, width }
                })}
              />
              <NumberInput
                label="Height"
                value={this.data.shapeParams.height}
                min={0}
                onChange={height => this.update({
                  shapeParams: { ...this.data.shapeParams, height }
                })}
              />
            </>
          )}
        </div>
      </div>
    );
  }

  private update(newData: any) {
    this.data = {
      ...this.data,
      ...newData
    };
    this.update();
  }
} 