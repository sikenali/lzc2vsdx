const { contextBridge, ipcRenderer } = require('electron')

// 仅暴露模型配置读写与窗口控制，不暴露任意 fs / ipcRenderer。
contextBridge.exposeInMainWorld('c2vsdx', {
  readModelConfig: () => ipcRenderer.invoke('model-config:read'),
  writeModelConfig: (cfg) => ipcRenderer.invoke('model-config:write', cfg),
  // #1 无边框窗口控制
  minimize: () => ipcRenderer.send('window:minimize'),
  maximizeToggle: () => ipcRenderer.send('window:maximize-toggle'),
  close: () => ipcRenderer.send('window:close'),
  onMaximizeChange: (cb) => {
    const listener = (_e, isMax) => cb(isMax)
    ipcRenderer.on('window:maximize-changed', listener)
    return () => ipcRenderer.removeListener('window:maximize-changed', listener)
  },
})
