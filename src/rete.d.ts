declare module 'rete' {
  export class NodeEditor {
    constructor();
    use(plugin: any): void;
    addNode(node: any): Promise<void>;
    removeNode(id: string): Promise<void>;
    on(event: string, callback: any): void;
    destroy(): void;
  }
}

declare module 'rete-area-plugin' {
  export class AreaPlugin {
    constructor(container: HTMLElement);
    translate(x: number, y: number): void;
    zoom(level: number): void;
    use(plugin: any): void;
  }
  
  export namespace AreaExtensions {
    export function selectableNodes(area: any, selector: any, options: any): void;
    export function selector(): any;
    export function accumulateOnCtrl(): any;
    export function simpleNodesOrder(area: any): void;
    export function snapGrid(area: any, options: any): void;
  }
}

declare module 'rete-react-plugin' {
  export class ReactPlugin {
    addPreset(preset: any): void;
  }
  export interface ReactArea2D {}
}

declare module 'rete-connection-plugin' {
  export class ConnectionPlugin {
    addPipe(callback: any): void;
  }
} 