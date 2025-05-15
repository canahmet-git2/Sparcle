import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'electron',
  {
    windowControl: {
      minimize: () => ipcRenderer.send('window-minimize'),
      maximize: () => ipcRenderer.send('window-maximize'),
      close: () => ipcRenderer.send('window-close')
    },
    onWindowStateChange: (callback: (state: string) => void) => {
      ipcRenderer.on('window-state-change', (_event, state) => callback(state));
    }
  }
); 