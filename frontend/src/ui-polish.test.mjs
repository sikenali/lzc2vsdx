import test from 'node:test'
import assert from 'node:assert'
import { readFile } from 'node:fs/promises'

const read = (p) => readFile(new URL(p, import.meta.url), 'utf8')

test('toast 事件契约为 {type,message} 且 §9 顶部居中', async () => {
  const app = await read('./App.vue')
  // §9 位置：顶部 16px 居中（DESIGN-1）
  assert.match(app, /top:\s*16px/)
  assert.match(app, /left:\s*50%/)
  assert.match(app, /z-index:\s*10000/)
  // 事件契约：读取 event.detail 并构建 {type,message}
  assert.match(app, /event\.detail/)
  assert.match(app, /toast\.value\s*=\s*\{\s*(type|message)[^}]*,\s*(type|message)/)
  // 模板用 toast.message / toast.type
  assert.match(app, /toast\.message|toast\?\.message|toast\.type/)
  // §9 类型色条（Nebula 色系）
  assert.match(app, /toast-bar|#00D4AA|#FF4D6D|#FFB347|#4A9EFF/)
  // 统一助手：utils/toast.js 导出 toast(type, message) dispatch {type,message}
  const util = await read('./utils/toast.js')
  assert.match(util, /export\s+function\s+toast/)
  assert.match(util, /detail:\s*\{\s*type,\s*message\s*\}/)
})

test('各调用点使用统一 toast 助手并传类型', async () => {
  for (const f of [
    './views/TextView.vue',
    './views/ImageView.vue',
    './views/ResultView.vue',
    './components/AppFooter.vue',
    './components/settings/ThemeSettingsView.vue',
  ]) {
    const src = await read(f)
    assert.match(src, /import\s+\{\s*toast\s*\}\s+from\s+['"].*utils\/toast['"]/, `${f} 应导入统一 toast`)
    assert.doesNotMatch(src, /function\s+toast\(/, `${f} 不应再定义本地 toast`)
  }
})

test('tokens 提供 primary-fill/on 与体系圆角（Nebula）', async () => {
  const css = await read('./styles/tokens.css')
  assert.match(css, /--primary-fill:/)
  assert.match(css, /\[data-theme="dark"\][\s\S]*--primary-fill:/)
  // §1 圆角体系 xs=4/sm=8/md=12/lg=16/xl=20
  assert.match(css, /--radius-xs:\s*4px/)
  assert.match(css, /--radius-sm:\s*8px/)
  assert.match(css, /--radius-md:\s*12px/)
  assert.match(css, /--radius-lg:\s*16px/)
  // Nebula 主强调：电光青
  assert.match(css, /--tech-cyan:\s*#00D4AA/)
})

test('实底填充改用 primary-fill/on，硬编码色入 token', async () => {
  const base = await read('./styles/base.css')
  // .btn-primary 实底用 fill/on
  assert.match(base, /\.btn-primary\s*\{[\s\S]*background:\s*var\(--primary-fill\)/)
  assert.match(base, /\.btn-primary\s*\{[\s\S]*color:\s*var\(--primary-on\)/)
  // .btn-ghost 透明底 + 0.6px 边框
  assert.match(base, /\.btn-ghost\s*\{[\s\S]*background:\s*transparent/)
  assert.doesNotMatch(base, /\.btn-primary:disabled/)
  const result = await read('./views/ResultView.vue')
  // §4.4 统计卡使用 Nebula 色值（cyan/gold/coral），无硬编码红色
  assert.doesNotMatch(result, /\.stat-card\.red\s*\{[\s\S]*color:\s*#[Ff][Ff]3[Bb]30/)
  assert.doesNotMatch(result, /\.soft-action\s*\{[\s\S]*background:\s*#fff/)
})

test('生成/保存按钮不灰置 + 卡片响应式', async () => {
  const tv = await read('./views/TextView.vue')
  const iv = await read('./views/ImageView.vue')
  const tw = await read('./components/TweakDrawer.vue')
  assert.doesNotMatch(tv, /:disabled/)
  assert.doesNotMatch(iv, /:disabled/)
  assert.doesNotMatch(tw, /:disabled/)
  // §A.7 紧凑版单卡片：min(820px, calc(100vw-48px))
  assert.match(iv, /width:\s*min\(820px,\s*calc\(100vw\s*-\s*48px\)\)/)
  assert.match(tv, /:focus/)   // 输入框 focus 主色边框+外发光
})

test('路由懒加载 + 页脚链接', async () => {
  const router = await read('./router.js')
  const footer = await read('./components/AppFooter.vue')
  assert.match(router, /\(\)\s*=>\s*import\(/)
  assert.match(footer, /href="https:\/\/lazycat\.cloud\/"/)
})

test('model-select focus 有电光青外发光', async () => {
  const tv = await read('./views/TextView.vue')
  assert.match(tv, /\.model-select:focus\s*\{[\s\S]*border-color:\s*var\(--tech-cyan\)/)
})

test('Nebula tokens: tech-cyan primary, Space Grotesk/JetBrains Mono fonts', async () => {
  const tokens = await read('./styles/tokens.css')
  assert.match(tokens, /--tech-cyan:\s*#00D4AA/)
  assert.match(tokens, /--tech-coral:\s*#FF4D6D/)
  assert.match(tokens, /--tech-gold:\s*#FFB347/)
  assert.match(tokens, /--tech-blue:\s*#4A9EFF/)
  // DESIGN-1 字体族
  assert.match(tokens, /Space Grotesk/)
  assert.match(tokens, /JetBrains Mono/)
  assert.match(tokens, /Inter/)
  // Light 冷灰蓝底 + Dark 深空底
  assert.match(tokens, /--color-bg-main:\s*#F4F7FA/)
  assert.match(tokens, /\[data-theme="dark"\][\s\S]*--color-bg-main:\s*#0A0F18/)
})

test('tokens define glow + transition tokens (§1.4/§11.2)', async () => {
  const tokens = await read('./styles/tokens.css')
  // glow 两级
  assert.match(tokens, /--glow-xs:\s*0\s*2px\s*8px\s*rgba\(var\(--tech-cyan-rgb\),\s*0\.08\)/)
  assert.match(tokens, /--glow-sm:\s*0\s*4px\s*20px\s*rgba\(var\(--tech-cyan-rgb\),\s*0\.12\)/)
  // 时长 snap=80/fast=120/base=180/slow=280
  assert.match(tokens, /--t-snap:\s*80ms/)
  assert.match(tokens, /--t-fast:\s*120ms/)
  assert.match(tokens, /--t-base:\s*180ms/)
  assert.match(tokens, /--t-slow:\s*280ms/)
  // 微弹曲线
  assert.match(tokens, /--ease-spring:\s*cubic-bezier\(0\.34,\s*1\.56,\s*0\.64,\s*1\)/)
})

test('header 64px glass + glow divider + slide indicator (§2.1/§2.3)', async () => {
  const header = await read('./components/AppHeader.vue')
  assert.match(header, /height:\s*64px/)
  assert.match(header, /backdrop-filter/)
  assert.match(header, /blur\(\s*16px\s*\)/)
  // 电光青发光分割线（随强调色 rgba 变体）
  assert.match(header, /rgba\(var\(--tech-cyan-rgb\),\s*0\.25\)/)
  // 底部滑动指示器
  assert.match(header, /\.nav-indicator/)
  assert.match(header, /linear-gradient\(90deg,\s*var\(--tech-cyan\)/)
  assert.match(header, /\.nav-item\.active\s*\{[\s\S]*color:\s*var\(--tech-cyan\)/)
})

test('round buttons follow §A.4: 36×36px, hover cyan + translateY(-2px)', async () => {
  const header = await read('./components/AppHeader.vue')
  assert.match(header, /width:\s*36px/)
  assert.match(header, /height:\s*36px/)
  assert.match(header, /scale\(0\.96\)/)
  assert.match(header, /\.nav-item:hover\s*\{[\s\S]*translateY\(-1px\)/)
  assert.match(header, /\.round-btn:hover\s*\{[\s\S]*transform\s*:\s*translateY\(-2px\)/)
  assert.match(header, /rgba\(var\(--tech-cyan-rgb\),\s*0\.35\)/)
})

test('SideNav 64px + 左侧竖条发光指示器（§2.2）', async () => {
  const nav = await read('./components/SideNav.vue')
  assert.match(nav, /width:\s*64px/)
  assert.match(nav, /\.sidenav-accent/)
  assert.match(nav, /width:\s*3px/)
  assert.match(nav, /box-shadow:\s*0\s*0\s*8px\s*rgba\(var\(--tech-cyan-rgb\),\s*0\.5\)/)
  assert.match(nav, /width:\s*48px/)   // 按钮 48×48
})

test('upload card drag state uses tech-cyan tint（§A.7）', async () => {
  const iv = await read('./views/ImageView.vue')
  assert.match(iv, /rgba\(var\(--tech-cyan-rgb\),\s*0\.06\)/)
  assert.match(iv, /rgba\(var\(--tech-cyan-rgb\),\s*0\.12\)/)
})

test('remove-btn has rotate 120° on active（§A.7）', async () => {
  const iv = await read('./views/ImageView.vue')
  assert.match(iv, /rotate\(120deg\)/)
})

test('SettingsModal 88vw/86vh/max 1100 + 40px 图标圆（§A.10/§5.2）', async () => {
  const sm = await read('./components/SettingsModal.vue')
  assert.match(sm, /width="88vw"/)
  assert.match(sm, /height="86vh"/)
  assert.match(sm, /:max-width="1100"/)
  assert.match(sm, /width:\s*40px/)          // settings-icon 40px
  assert.match(sm, /font-size:\s*18px/)      // 标题 18px
  // 激活态左侧竖条
  assert.match(sm, /\.settings-nav-accent/)
})

test('UiModal 深空毛玻璃底（仅 dark）+ scale 入场（§8.1）', async () => {
  const modal = await read('./components/UiModal.vue')
  // 浅色主题：浅色表面（修复规范矛盾）；深色主题：深空玻璃底
  assert.match(modal, /background:\s*var\(--bg-card\)/)
  assert.match(modal, /\[data-theme="dark"\][\s\S]*rgba\(10,\s*22,\s*40,\s*0\.9[0-9]\)/)
  assert.match(modal, /scale\(0\.97\)/)
  assert.match(modal, /default:\s*14/)       // radius 14px
})

test('AppFooter 48px + tech-cyan 链接（§2.1）', async () => {
  const footer = await read('./components/AppFooter.vue')
  assert.match(footer, /height:\s*48px/)
  assert.match(footer, /\[data-theme="dark"\]\s*\.app-footer\s*\{[\s\S]*background:\s*rgba\(15,\s*22,\s*35,\s*0\.88\)/)
})

test('base.css: body 15px + 电光青 focus ring（§1.5/§1.6）', async () => {
  const base = await read('./styles/base.css')
  assert.match(base, /font-size:\s*15px/)
  assert.match(base, /:focus-visible\s*\{[\s\S]*box-shadow:\s*0\s*0\s*0\s*3px\s*rgba\(var\(--tech-cyan-rgb\),\s*0\.4\)/)
})

test('base.css: 统一极细滚动条 + 深色白色 thumb（§1.7）', async () => {
  const base = await read('./styles/base.css')
  assert.match(base, /::-webkit-scrollbar\s*\{\s*width:\s*6px;\s*height:\s*6px/)
  assert.match(base, /::-webkit-scrollbar-thumb\s*\{[\s\S]*background:\s*rgba\(0,\s*0,\s*0,\s*0\.15\)/)
  assert.match(base, /\[data-theme="dark"\][\s\S]*::-webkit-scrollbar-thumb\s*\{[\s\S]*background:\s*rgba\(255,\s*255,\s*255,\s*0\.12\)/)
})

test('ResultView 统计卡 Nebula 配色（§4.4）', async () => {
  const result = await read('./views/ResultView.vue')
  assert.match(result, /rgba\(var\(--tech-cyan-rgb\),\s*0\.08\)/)  // cyan（随强调色）
  assert.match(result, /rgba\(255,\s*179,\s*71,\s*0\.08\)/)  // gold
  assert.match(result, /rgba\(255,\s*77,\s*109,\s*0\.08\)/)  // coral
  // 26px 数字
  assert.match(result, /font-size:\s*26px/)
})

test('强调色传播：--tech-cyan 与 --tech-cyan-rgb 随 [data-accent] 变化', async () => {
  const tokens = await read('./styles/tokens.css')
  // 每个强调色块都覆写 --tech-cyan 与 --tech-cyan-rgb（light + dark）
  for (const [accent, hex, rgb] of [
    ['cyan',  '#00D4AA', '0, 212, 170'],
    ['gold',  '#FFB347', '255, 179, 71'],
    ['green', '#00A878', '0, 168, 120'],
    ['blue',  '#4A9EFF', '74, 158, 255'],
    ['coral', '#FF4D6D', '255, 77, 109'],
  ]) {
    assert.match(tokens, new RegExp(`\\[data-accent="${accent}"\\][\\s\\S]{0,200}--tech-cyan:\\s*${hex}[\\s\\S]{0,80}--tech-cyan-rgb:\\s*${rgb}`),
      `light ${accent} 应覆写 --tech-cyan/${rgb}`)
  }
  // 组件使用 accent 驱动的 rgba 变体
  const header = await read('./components/AppHeader.vue')
  assert.match(header, /rgba\(var\(--tech-cyan-rgb\),/)
  const typeCard = await read('./components/TypeCard.vue')
  assert.match(typeCard, /var\(--tech-cyan\)/)   // 激活态跟随强调色
})