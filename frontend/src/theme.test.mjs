import test from 'node:test'
import assert from 'node:assert'
import { DEFAULT_THEME, ACCENTS, normalizeTheme, applyTheme, useTheme } from './stores/theme.js'

test('normalizeTheme 回退非法输入到默认', () => {
  assert.deepEqual(normalizeTheme(null), DEFAULT_THEME)
  assert.deepEqual(normalizeTheme({}), DEFAULT_THEME)
  assert.deepEqual(normalizeTheme({ mode: 'x', accent: 'y', layout: 'z' }), DEFAULT_THEME)
  assert.deepEqual(normalizeTheme({ mode: 'dark' }), { ...DEFAULT_THEME, mode: 'dark' })
  assert.deepEqual(normalizeTheme({ accent: 'gold', layout: 'sidebar' }), { ...DEFAULT_THEME, accent: 'gold', layout: 'sidebar' })
})

test('ACCENTS 含 5 色且字段齐全', () => {
  const keys = Object.keys(ACCENTS)
  // DESIGN-1 §6.3：电光青/赛博金/玉绿/琉璃蓝/霓虹珊瑚
  assert.deepEqual(keys, ['cyan', 'gold', 'green', 'blue', 'coral'])
  for (const k of keys) for (const f of ['name', 'color', 'soft', 'on', 'deep'])
    assert.ok(ACCENTS[k][f], `${k}.${f} 缺失`)
})

test('applyTheme 设置 data-theme 与 data-accent', () => {
  const root = { setAttribute(){}, }
  let set = {}
  root.setAttribute = (k, v) => { set[k] = v }
  applyTheme({ mode: 'dark', accent: 'gold', layout: 'topbar' }, root)
  assert.equal(set['data-theme'], 'dark')
  assert.equal(set['data-accent'], 'gold')
})

test('setMode 持久化并应用到 DOM，非法值回退默认', () => {
  const persisted = {}
  globalThis.localStorage = {
    getItem: () => null,
    setItem: (k, v) => { persisted[k] = v },
  }
  const attrs = {}
  globalThis.document = {
    documentElement: { setAttribute: (k, v) => { attrs[k] = v } },
  }
  try {
    const { setMode } = useTheme()
    setMode('dark')
    assert.equal(attrs['data-theme'], 'dark')
    // Nebula 默认强调色为 cyan
    assert.equal(attrs['data-accent'], 'cyan')
    assert.equal(JSON.parse(persisted['c2vsdx:theme']).mode, 'dark')

    setMode('banana')
    assert.equal(attrs['data-theme'], 'light')
    assert.equal(JSON.parse(persisted['c2vsdx:theme']).mode, 'light')
  } finally {
    delete globalThis.localStorage
    delete globalThis.document
  }
})

test('tokens 提供深色与强调色变量', async () => {
  const css = await (await import('node:fs/promises')).readFile(new URL('./styles/tokens.css', import.meta.url), 'utf8')
  assert.match(css, /\[data-theme="dark"\]/)
  assert.match(css, /\[data-accent="cyan"\]/)
  // DESIGN-1：tech-cyan 主强调（深色更亮 #00F5C8）
  assert.match(css, /--tech-cyan:\s*#00D4AA/)
  assert.match(css, /\[data-theme="dark"\][\s\S]*--tech-cyan:\s*#00F5C8/)
})

test('模块初始化时按持久化主题应用 data-theme/data-accent（boot 路径）', async () => {
  // 在导入模块前设置 globals，验证 store 顶层 applyTheme 立即生效。
  const persistedTheme = JSON.stringify({ mode: 'dark', accent: 'gold', layout: 'sidebar' })
  globalThis.localStorage = {
    getItem: (k) => (k === 'c2vsdx:theme' ? persistedTheme : null),
    setItem: () => {},
  }
  const attrs = {}
  globalThis.document = {
    documentElement: { setAttribute: (k, v) => { attrs[k] = v } },
  }
  try {
    // 独立模块实例（query 防缓存）：导入时即应反映持久化主题。
    const boot = await import('./stores/theme.js?boot=1')
    assert.equal(attrs['data-theme'], 'dark')
    assert.equal(attrs['data-accent'], 'gold')
    assert.equal(boot.useTheme().theme.layout, 'sidebar')
  } finally {
    delete globalThis.localStorage
    delete globalThis.document
  }
})
