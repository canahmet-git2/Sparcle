import { Node, Socket } from 'rete';
import { SelectInput } from '../../components/inputs/SelectInput';
import { NumberInput } from '../../components/inputs/NumberInput';
import { ColorInput } from '../../components/inputs/ColorInput';

export class BehaviorNode extends Node {
  constructor() {
    super('Behavior');
    this.type = 'behavior';

    // Add input and output sockets
    this.addInput('input', new Socket('particle'));
    this.addOutput('output', new Socket('particle'));

    // Initialize default data
    this.data = {
      behaviors: []
    };
  }

  render() {
    return (
      <div className="node behavior-node">
        <div className="node-header">
          <h3>Behavior</h3>
        </div>
        <div className="node-content">
          <button
            className="add-behavior-btn"
            onClick={() => this.addBehavior()}
          >
            Add Behavior
          </button>
          {this.data.behaviors.map((behavior: any, index: number) => (
            <div key={index} className="behavior-item">
              <div className="behavior-header">
                <SelectInput
                  label="Type"
                  value={behavior.type}
                  options={[
                    { value: 'color', label: 'Color' },
                    { value: 'size', label: 'Size' },
                    { value: 'rotation', label: 'Rotation' },
                    { value: 'velocity', label: 'Velocity' },
                    { value: 'alpha', label: 'Alpha' }
                  ]}
                  onChange={type => this.updateBehavior(index, { type })}
                />
                <button
                  className="remove-behavior-btn"
                  onClick={() => this.removeBehavior(index)}
                >
                  ×
                </button>
              </div>
              <SelectInput
                label="Mode"
                value={behavior.mode}
                options={[
                  { value: 'constant', label: 'Constant' },
                  { value: 'overtime', label: 'Over Time' },
                  { value: 'random', label: 'Random' }
                ]}
                onChange={mode => this.updateBehavior(index, { mode })}
              />
              {this.renderBehaviorControls(behavior, index)}
            </div>
          ))}
        </div>
      </div>
    );
  }

  private renderBehaviorControls(behavior: any, index: number) {
    switch (behavior.type) {
      case 'color':
        return this.renderColorControls(behavior, index);
      case 'size':
        return this.renderNumberControls(behavior, index, 'Size');
      case 'rotation':
        return this.renderNumberControls(behavior, index, 'Rotation');
      case 'velocity':
        return this.renderNumberControls(behavior, index, 'Velocity');
      case 'alpha':
        return this.renderNumberControls(behavior, index, 'Alpha', 0, 1, 0.1);
      default:
        return null;
    }
  }

  private renderColorControls(behavior: any, index: number) {
    switch (behavior.mode) {
      case 'constant':
        return (
          <ColorInput
            label="Color"
            value={behavior.value || { r: 1, g: 1, b: 1, a: 1 }}
            onChange={value => this.updateBehavior(index, { value })}
          />
        );
      case 'overtime':
        return (
          <>
            <div className="color-keyframes">
              {(behavior.value || [{ r: 1, g: 1, b: 1, a: 1 }]).map((color: any, i: number) => (
                <div key={i} className="keyframe">
                  <ColorInput
                    label={`Color ${i + 1}`}
                    value={color}
                    onChange={value => {
                      const newColors = [...(behavior.value || [])];
                      newColors[i] = value;
                      this.updateBehavior(index, { value: newColors });
                    }}
                  />
                  {i > 0 && (
                    <button
                      onClick={() => {
                        const newColors = [...(behavior.value || [])];
                        newColors.splice(i, 1);
                        this.updateBehavior(index, { value: newColors });
                      }}
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={() => {
                  const newColors = [...(behavior.value || []), { r: 1, g: 1, b: 1, a: 1 }];
                  this.updateBehavior(index, { value: newColors });
                }}
              >
                Add Color
              </button>
            </div>
            <NumberInput
              label="Time Scale"
              value={behavior.timeScale || 1}
              min={0.1}
              step={0.1}
              onChange={timeScale => this.updateBehavior(index, { timeScale })}
            />
          </>
        );
      case 'random':
        return (
          <>
            <ColorInput
              label="Color 1"
              value={behavior.value?.[0] || { r: 1, g: 1, b: 1, a: 1 }}
              onChange={value => {
                const newValue = [...(behavior.value || [{ r: 1, g: 1, b: 1, a: 1 }, { r: 1, g: 1, b: 1, a: 1 }])];
                newValue[0] = value;
                this.updateBehavior(index, { value: newValue });
              }}
            />
            <ColorInput
              label="Color 2"
              value={behavior.value?.[1] || { r: 1, g: 1, b: 1, a: 1 }}
              onChange={value => {
                const newValue = [...(behavior.value || [{ r: 1, g: 1, b: 1, a: 1 }, { r: 1, g: 1, b: 1, a: 1 }])];
                newValue[1] = value;
                this.updateBehavior(index, { value: newValue });
              }}
            />
          </>
        );
      default:
        return null;
    }
  }

  private renderNumberControls(behavior: any, index: number, label: string, min = -Infinity, max = Infinity, step = 1) {
    switch (behavior.mode) {
      case 'constant':
        return (
          <NumberInput
            label={label}
            value={behavior.value || 0}
            min={min}
            max={max}
            step={step}
            onChange={value => this.updateBehavior(index, { value })}
          />
        );
      case 'overtime':
        return (
          <>
            <div className="number-keyframes">
              {(behavior.value || [0]).map((value: number, i: number) => (
                <div key={i} className="keyframe">
                  <NumberInput
                    label={`${label} ${i + 1}`}
                    value={value}
                    min={min}
                    max={max}
                    step={step}
                    onChange={newValue => {
                      const newValues = [...(behavior.value || [])];
                      newValues[i] = newValue;
                      this.updateBehavior(index, { value: newValues });
                    }}
                  />
                  {i > 0 && (
                    <button
                      onClick={() => {
                        const newValues = [...(behavior.value || [])];
                        newValues.splice(i, 1);
                        this.updateBehavior(index, { value: newValues });
                      }}
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={() => {
                  const newValues = [...(behavior.value || []), 0];
                  this.updateBehavior(index, { value: newValues });
                }}
              >
                Add Value
              </button>
            </div>
            <NumberInput
              label="Time Scale"
              value={behavior.timeScale || 1}
              min={0.1}
              step={0.1}
              onChange={timeScale => this.updateBehavior(index, { timeScale })}
            />
          </>
        );
      case 'random':
        return (
          <>
            <NumberInput
              label={`${label} Min`}
              value={behavior.value?.[0] || 0}
              min={min}
              max={max}
              step={step}
              onChange={value => {
                const newValue = [...(behavior.value || [0, 0])];
                newValue[0] = value;
                this.updateBehavior(index, { value: newValue });
              }}
            />
            <NumberInput
              label={`${label} Max`}
              value={behavior.value?.[1] || 0}
              min={min}
              max={max}
              step={step}
              onChange={value => {
                const newValue = [...(behavior.value || [0, 0])];
                newValue[1] = value;
                this.updateBehavior(index, { value: newValue });
              }}
            />
          </>
        );
      default:
        return null;
    }
  }

  private addBehavior() {
    const newBehavior = {
      type: 'color',
      mode: 'constant',
      value: { r: 1, g: 1, b: 1, a: 1 }
    };
    this.update({
      behaviors: [...this.data.behaviors, newBehavior]
    });
  }

  private removeBehavior(index: number) {
    const behaviors = [...this.data.behaviors];
    behaviors.splice(index, 1);
    this.update({ behaviors });
  }

  private updateBehavior(index: number, newData: any) {
    const behaviors = [...this.data.behaviors];
    behaviors[index] = {
      ...behaviors[index],
      ...newData
    };
    this.update({ behaviors });
  }

  private update(newData: any) {
    this.data = {
      ...this.data,
      ...newData
    };
    this.update();
  }
} 