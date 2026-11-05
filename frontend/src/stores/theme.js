import { reactive } from 'vue'

/** localStorage key for the persisted theme. */
export const THEME_KEY = 'c2vsdx:theme'

/** Default theme: light parchment, red accent, topbar layout. */
export const DEFAULT_THEME = {
  mode: 'light',
  accent: 'red',
  layout: 'topbar',
}

/**
 * The 5 accent palettes (DESIGN.md §6.3 / §7).
 * `on` is the text/icon color used on top of `color`; `deep` is the
 * deepened variant aliased to `--red-2` / `--primary-deep`.
 */
export const ACCENTS = {
  red: { name: '朱红', color: '#C0392B', soft: '#FBE9E7', on: '#FFFFFF', deep: '#A33A2E' },
  gold: { name: '鎏金', color: '#D3A93F', soft: '#F7EEE0', on: '#1F1D1A', deep: '#A8842C' },
  green: { name: '玉绿', color: '#3E8C6E', soft: '#E4F0EA', on: '#FFFFFF', deep: '#2F6E54' },
  blue: { name: '云蓝', color: '#4A72A8', soft: '#E8F0F8', on: '#FFFFFF', deep: '#3A5C96' },
  ink: { name: '黛墨', color: '#2F3640', soft: '#E9EBEE', on: '#FFFFFF', deep: '#1C2128' },
}

const MODES = ['light', 'dark']
const LAYOUTS = ['topbar', 'sidebar']
const ACCENT_KEYS = Object.keys(ACCENTS)

/**
 * Coerce any raw value into a valid theme. Invalid/missing fields fall back to
 * the corresponding DEFAULT_THEME value; a null/non-object input yields the
 * full default theme.
 */
export function normalizeTheme(raw) {
  if (!raw || typeof raw !== 'object') return { ...DEFAULT_THEME }
  return {
    mode: MODES.includes(raw.mode) ? raw.mode : DEFAULT_THEME.mode,
    accent: ACCENT_KEYS.includes(raw.accent) ? raw.accent : DEFAULT_THEME.accent,
    layout: LAYOUTS.includes(raw.layout) ? raw.layout : DEFAULT_THEME.layout,
  }
}

/** Read the persisted theme from localStorage, falling back to defaults. */
export function loadTheme() {
  if (typeof localStorage === 'undefined') return { ...DEFAULT_THEME }
  try {
    const raw = localStorage.getItem(THEME_KEY)
    if (!raw) return { ...DEFAULT_THEME }
    return normalizeTheme(JSON.parse(raw))
  } catch {
    return { ...DEFAULT_THEME }
  }
}

/** Persist the theme to localStorage (no-op outside a browser). */
export function saveTheme(t) {
  if (typeof localStorage === 'undefined') return
  try {
    localStorage.setItem(THEME_KEY, JSON.stringify(normalizeTheme(t)))
  } catch {
    // ignore quota/security errors — persistence is best-effort
  }
}

/** Reflect a theme onto the document root via data-theme / data-accent. */
export function applyTheme(t, root = document.documentElement) {
  root.setAttribute('data-theme', t.mode)
  root.setAttribute('data-accent', t.accent)
}

// Singleton reactive state shared across every useTheme() caller.
const state = reactive(loadTheme())

// Close the persistence cycle: reflect the loaded theme onto <html> on boot so
// a returning user's mode/accent are restored before first paint. Guarded for
// Node (node --test) where `document` is undefined.
if (typeof document !== 'undefined') applyTheme(state)

function commit(next) {
  // Normalize so state, DOM, and localStorage stay mutually consistent even if
  // a mutator receives an invalid value.
  Object.assign(state, normalizeTheme({ ...state, ...next }))
  saveTheme(state)
  applyTheme(state)
}

/**
 * Reactive theme store: read `theme`, mutate via setMode/setAccent/setLayout,
 * or reset() to defaults. Every mutation persists and re-applies immediately.
 */
export function useTheme() {
  return {
    theme: state,
    setMode(mode) {
      commit({ mode })
    },
    setAccent(accent) {
      commit({ accent })
    },
    setLayout(layout) {
      commit({ layout })
    },
    reset() {
      commit({ ...DEFAULT_THEME })
    },
  }
}
