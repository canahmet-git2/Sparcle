import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'electron',
  {
    ipcRenderer: {
      send: (channel: string, ...args: any[]) => {
        // Whitelist channels
        const validChannels = ['window-minimize', 'window-maximize', 'window-close'];
        if (validChannels.includes(channel)) {
          ipcRenderer.send(channel, ...args);
        }
      },
      on: (channel: string, func: (...args: any[]) => void) => {
        const validChannels = ['window-state-change'];
        if (validChannels.includes(channel)) {
          // Strip event as it includes `sender` 
          ipcRenderer.on(channel, (...args) => func(...args.slice(1)));
        }
      },
      removeListener: (channel: string, func: (...args: any[]) => void) => {
        const validChannels = ['window-state-change'];
        if (validChannels.includes(channel)) {
          ipcRenderer.removeListener(channel, func);
        }
      }
    }
  }
); 