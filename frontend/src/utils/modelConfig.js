/**
 * 模型配置读写（设置中心「模型管理」）。
 * 桌面端：经 preload 的 window.c2vsdx.readModelConfig/writeModelConfig（userData/config.json）。
 * Dev/Web：无 window.c2vsdx 时回退 localStorage（仅 UI 可交互，不注入后端）。
 */
const KEY = 'c2vsdx-model-config'
const EMPTY = {
  vision: { baseUrl: '', apiKey: '', model: '' },
  llm: { baseUrl: '', apiKey: '', model: '' },
}

export async function loadModelConfig() {
  if (window.c2vsdx?.readModelConfig) return await window.c2vsdx.readModelConfig()
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || 'null')
    return {
      vision: { ...EMPTY.vision, ...(saved?.vision || {}) },
      llm: { ...EMPTY.llm, ...(saved?.llm || {}) },
    }
  } catch {
    return { ...EMPTY }
  }
}

export async function saveModelConfig(cfg) {
  if (window.c2vsdx?.writeModelConfig) return await window.c2vsdx.writeModelConfig(cfg)
  localStorage.setItem(KEY, JSON.stringify(cfg))
  return { ok: true }
}
