import { reactive } from 'vue'

export const THEME_KEY = 'c2vsdx:theme'

/** Default theme: light Nebula, cyan accent, topbar layout. */
export const DEFAULT_THEME = { mode: 'light', accent: 'cyan', layout: 'topbar' }

/**
 * 5 accent palettes（DESIGN-1 §6.3 Nebula 科技风）：
 * 电光青·默认 / 赛博金 / 玉绿 / 琉璃蓝 / 霓虹珊瑚
 * `on` = 主色上文字颜色；`deep` = 加深变体。
 */
export const ACCENTS = {
  cyan:  { name: '电光青·默认', color: '#00D4AA', soft: '#E8FFF8', on: '#0A1628', deep: '#0A6B5A' },
  gold:  { name: '赛博金',      color: '#FFB347', soft: '#FFF8E6', on: '#0A1628', deep: '#C67A10' },
  green: { name: '玉绿',        color: '#00A878', soft: '#E6FFF4', on: '#0A1628', deep: '#008A62' },
  blue:  { name: '琉璃蓝',      color: '#4A9EFF', soft: '#EBF4FF', on: '#0A1628', deep: '#2D7FD9' },
  coral: { name: '霓虹珊瑚',    color: '#FF4D6D', soft: '#FFF0F3', on: '#0A1628', deep: '#D13A56' },
}

const MODES       = ['light', 'dark']
const LAYOUTS     = ['topbar', 'sidebar']
const ACCENT_KEYS = Object.keys(ACCENTS)

export function normalizeTheme(raw) {
  if (!raw || typeof raw !== 'object') return { ...DEFAULT_THEME }
  return {
    mode:   MODES.includes(raw.mode)       ? raw.mode   : DEFAULT_THEME.mode,
    accent: ACCENT_KEYS.includes(raw.accent) ? raw.accent : DEFAULT_THEME.accent,
    layout: LAYOUTS.includes(raw.layout)   ? raw.layout : DEFAULT_THEME.layout,
  }
}

export function loadTheme() {
  if (typeof localStorage === 'undefined') return { ...DEFAULT_THEME }
  try {
    const raw = localStorage.getItem(THEME_KEY)
    return raw ? normalizeTheme(JSON.parse(raw)) : { ...DEFAULT_THEME }
  } catch { return { ...DEFAULT_THEME } }
}

export function saveTheme(t) {
  if (typeof localStorage === 'undefined') return
  try { localStorage.setItem(THEME_KEY, JSON.stringify(normalizeTheme(t))) } catch {}
}

export function applyTheme(t, root = document.documentElement) {
  root.setAttribute('data-theme', t.mode)
  root.setAttribute('data-accent', t.accent)
}

const state = reactive(loadTheme())
if (typeof document !== 'undefined') applyTheme(state)

function commit(next) {
  Object.assign(state, normalizeTheme({ ...state, ...next }))
  saveTheme(state)
  applyTheme(state)
}

export function useTheme() {
  return {
    theme: state,
    setMode(mode)     { commit({ mode }) },
    setAccent(accent) { commit({ accent }) },
    setLayout(layout) { commit({ layout }) },
    reset()           { commit({ ...DEFAULT_THEME }) },
  }
}