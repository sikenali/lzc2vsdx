const { app, BrowserWindow, dialog, shell, session, ipcMain } = require('electron')
const { spawn } = require('child_process')
const fs = require('fs')
const http = require('http')
const net = require('net')
const path = require('path')

let backend = null
let mainWindow = null
let backendLog = null

const isDev = !app.isPackaged || process.env.ELECTRON_DEV === '1'

function getFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer()
    server.on('error', reject)
    server.listen(0, '127.0.0.1', () => {
      const port = server.address().port
      server.close(() => resolve(port))
    })
  })
}

function waitForHealth(port, timeoutMs = 30000) {
  const deadline = Date.now() + timeoutMs
  return new Promise((resolve, reject) => {
    const probe = () => {
      const req = http.get(
        { host: '127.0.0.1', port, path: '/api/health', timeout: 1500 },
        (res) => {
          res.resume()
          if (res.statusCode === 200) resolve()
          else retry()
        }
      )
      req.on('error', retry)
      req.on('timeout', () => {
        req.destroy()
        retry()
      })
    }
    const retry = () => {
      if (Date.now() > deadline) reject(new Error('后端启动超时'))
      else setTimeout(probe, 300)
    }
    probe()
  })
}

function backendExecutable() {
  const name = process.platform === 'win32' ? 'c2vsdx-backend.exe' : 'c2vsdx-backend'
  return path.join(process.resourcesPath, 'backend', name)
}

// ---- 模型配置（userData/config.json，桌面端持久化 OPENVS_* 注入）----

function modelConfigPath() {
  return path.join(app.getPath('userData'), 'config.json')
}

function readModelConfig() {
  try {
    const raw = fs.readFileSync(modelConfigPath(), 'utf8')
    const cfg = JSON.parse(raw)
    return {
      vision: { baseUrl: cfg?.vision?.baseUrl || '', apiKey: cfg?.vision?.apiKey || '', model: cfg?.vision?.model || '' },
      llm: { baseUrl: cfg?.llm?.baseUrl || '', apiKey: cfg?.llm?.apiKey || '', model: cfg?.llm?.model || '' },
    }
  } catch {
    return { vision: {}, llm: {} }
  }
}

function writeModelConfig(cfg) {
  try {
    const data = {
      vision: { baseUrl: cfg?.vision?.baseUrl || '', apiKey: cfg?.vision?.apiKey || '', model: cfg?.vision?.model || '' },
      llm: { baseUrl: cfg?.llm?.baseUrl || '', apiKey: cfg?.llm?.apiKey || '', model: cfg?.llm?.model || '' },
    }
    fs.writeFileSync(modelConfigPath(), JSON.stringify(data, null, 2), 'utf8')
    return { ok: true }
  } catch (error) {
    return { ok: false, error: String(error.message || error) }
  }
}

function registerModelConfigIpc() {
  ipcMain.handle('model-config:read', () => readModelConfig())
  ipcMain.handle('model-config:write', (_event, cfg) => writeModelConfig(cfg))
}

// ---- #1 无边框窗口控制（自定义标题栏：最小化/最大化切换/关闭）----
function registerWindowIpc() {
  ipcMain.on('window:minimize', () => mainWindow?.minimize())
  ipcMain.on('window:maximize-toggle', () => {
    if (!mainWindow) return
    if (mainWindow.isMaximized()) mainWindow.unmaximize()
    else mainWindow.maximize()
  })
  ipcMain.on('window:close', () => mainWindow?.close())
}

function startBackend(port) {
  const exe = backendExecutable()
  if (!fs.existsSync(exe)) {
    throw new Error(`找不到后端可执行文件：${exe}`)
  }

  const runtime = path.join(app.getPath('userData'), 'runtime')
  fs.mkdirSync(runtime, { recursive: true })
  backendLog = fs.createWriteStream(path.join(app.getPath('userData'), 'backend.log'), { flags: 'a' })

  const env = {
    ...process.env,
    PORT: String(port),
    C2VSDX_DIST: path.join(process.resourcesPath, 'frontend', 'dist'),
    C2VSDX_RUNTIME: runtime,
    PYTHONUNBUFFERED: '1',
  }

  // Linux AppImage 内置 Graphviz；Windows 用 backend/c2vsdx/graphviz-bin
  const gvRoot = path.join(process.resourcesPath, 'graphviz-linux')
  if (fs.existsSync(gvRoot)) {
    env.GRAPHVIZ_BIN = path.join(gvRoot, 'bin')
    env.GVBINDIR = path.join(gvRoot, 'lib', 'graphviz')
    env.PATH = `${path.join(gvRoot, 'bin')}:${env.PATH || ''}`
    env.LD_LIBRARY_PATH = `${path.join(gvRoot, 'lib')}:${env.LD_LIBRARY_PATH || ''}`
  }

  // 模型配置：userData/config.json 非空字段注入 OPENVS_*（覆盖终端已设值）
  const cfg = readModelConfig()
  if (cfg.vision?.baseUrl) env.OPENVS_VISION_BASE_URL = cfg.vision.baseUrl
  if (cfg.vision?.apiKey) env.OPENVS_VISION_API_KEY = cfg.vision.apiKey
  if (cfg.vision?.model) env.OPENVS_VISION_MODEL = cfg.vision.model
  if (cfg.llm?.baseUrl) env.OPENVS_LLM_BASE_URL = cfg.llm.baseUrl
  if (cfg.llm?.apiKey) env.OPENVS_LLM_API_KEY = cfg.llm.apiKey
  if (cfg.llm?.model) env.OPENVS_LLM_MODEL = cfg.llm.model

  backend = spawn(exe, [], {
    cwd: path.dirname(exe),
    windowsHide: true,
    env,
  })

  backend.stdout.on('data', (chunk) => {
    backendLog.write(chunk)
    process.stdout.write(chunk)
  })
  backend.stderr.on('data', (chunk) => {
    backendLog.write(chunk)
    process.stderr.write(chunk)
  })
  backend.on('exit', (code) => {
    if (code !== 0 && code !== null && !app.isQuitting) {
      console.error(`backend exited with code ${code}`)
    }
  })
}

function stopBackend() {
  if (!backend) return
  const pid = backend.pid
  backend = null
  try {
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', String(pid), '/T', '/F'], { windowsHide: true })
    } else {
      process.kill(pid, 'SIGTERM')
    }
  } catch (error) {
    console.error('failed to stop backend', error)
  }
}

async function createWindow() {
  let port = 5000
  if (!isDev) {
    port = await getFreePort()
    startBackend(port)
    await waitForHealth(port)
  }

  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1100,
    minHeight: 760,
    title: 'C2VSDX',
    backgroundColor: '#F4F7FA',
    autoHideMenuBar: true,
    frame: false,                       // #1 无边框（自定义标题栏）
    show: false,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  })

  mainWindow.once('ready-to-show', () => mainWindow.show())
  // #1 通知渲染进程最大化状态（切换 最大化/还原 图标）
  mainWindow.on('maximize', () => mainWindow?.webContents.send('window:maximize-changed', true))
  mainWindow.on('unmaximize', () => mainWindow?.webContents.send('window:maximize-changed', false))
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  const url = isDev ? 'http://127.0.0.1:5173' : `http://127.0.0.1:${port}`
  await mainWindow.loadURL(url)
}

const gotLock = app.requestSingleInstanceLock()
if (!gotLock) {
  app.quit()
} else {
  registerModelConfigIpc()
  registerWindowIpc()

  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore()
      mainWindow.focus()
    }
  })

  app.whenReady().then(async () => {
    session.defaultSession.on('will-download', (event, item, webContents) => {
      const win = BrowserWindow.fromWebContents(webContents)
      const savePath = dialog.showSaveDialogSync(win, {
        title: '保存 VSDX 文件',
        defaultPath: item.getFilename(),
        filters: [{ name: 'Visio 图表', extensions: ['vsdx'] }],
      })
      if (!savePath) {
        item.cancel()
        return
      }
      item.setSavePath(savePath)
    })

    try {
      await createWindow()
    } catch (error) {
      dialog.showErrorBox('C2VSDX 启动失败', String(error.message || error))
      app.quit()
    }

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) createWindow().catch(() => {})
    })
  })
}

app.on('before-quit', () => {
  app.isQuitting = true
  stopBackend()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
