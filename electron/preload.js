const { contextBridge, ipcRenderer } = require('electron')

// 仅暴露模型配置读写两个方法，不暴露任意 fs / ipcRenderer。
contextBridge.exposeInMainWorld('c2vsdx', {
  readModelConfig: () => ipcRenderer.invoke('model-config:read'),
  writeModelConfig: (cfg) => ipcRenderer.invoke('model-config:write', cfg),
})
