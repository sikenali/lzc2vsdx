import test from 'node:test'
import assert from 'node:assert'
import { readFile } from 'node:fs/promises'

const read = (p) => readFile(new URL(p, import.meta.url), 'utf8')

test('toast 事件契约为 {type,message} 且 §9 顶部居中', async () => {
  const app = await read('./App.vue')
  // §9 位置：顶部 16px 居中（桌面端避让 36px 标题栏）
  assert.match(app, /top:\s*calc\(16px\s*\+\s*var\(--titlebar-h,\s*0px\)\)/)
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
  // dark×accent 交叉规则提供完整强调色（深色下强调色切换生效）
  assert.match(css, /\[data-theme="dark"\]\[data-accent="cyan"\][\s\S]*?--primary-fill:\s*#00F5C8/)
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

test('header 64px glass + glow divider；标签无底部指示条（§2.1/§2.3）', async () => {
  const header = await read('./components/AppHeader.vue')
  assert.match(header, /height:\s*64px/)
  assert.match(header, /backdrop-filter/)
  assert.match(header, /blur\(\s*16px\s*\)/)
  // 电光青发光分割线（随强调色 rgba 变体）
  assert.match(header, /rgba\(var\(--tech-cyan-rgb\),\s*0\.25\)/)
  // 激活态用电光青文字标识（无底部滑动指示条）
  assert.doesNotMatch(header, /\.nav-indicator/)
  assert.match(header, /\.nav-item\.active\s*\{[\s\S]*color:\s*var\(--tech-cyan\)/)
})

test('nav items follow §2.3 spec: cyan hover/focus lift + 右侧 round-btn 恢复', async () => {
  const header = await read('./components/AppHeader.vue')
  // 导航项 hover 微上浮 + 顶部微光条
  assert.match(header, /\.nav-item:hover\s*\{[\s\S]*translateY\(-1px\)/)
  assert.match(header, /\.nav-item:hover::before\s*\{[\s\S]*opacity:\s*1/)
  assert.match(header, /\.nav-item:active\s*\{[\s\S]*scale\(0\.97\)/)
  assert.match(header, /\.nav-item:focus-visible\s*\{[\s\S]*rgba\(var\(--tech-cyan-rgb\),\s*0\.3\)/)
  // 返回/设置圆形按钮已恢复（round-btn）
  assert.match(header, /\.round-btn/)
})

test('SideNav 64px + 品牌 Logo + 激活态无竖条（§2.2）', async () => {
  const nav = await read('./components/SideNav.vue')
  assert.match(nav, /width:\s*64px/)
  assert.doesNotMatch(nav, /\.sidenav-accent/)
  assert.match(nav, /BrandLogo/)
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
test('无边框：Electron main 设置 frame:false + 窗口控制 IPC（#1）', async () => {
  const main = await read('../../electron/main.js')
  const preload = await read('../../electron/preload.js')
  assert.match(main, /frame:\s*false/)
  assert.match(main, /ipcMain\.on\('window:minimize'/)
  assert.match(main, /ipcMain\.on\('window:maximize-toggle'/)
  assert.match(main, /ipcMain\.on\('window:close'/)
  assert.match(main, /window:maximize-changed/)
  assert.match(preload, /minimize:\s*\(\)\s*=>\s*ipcRenderer\.send\('window:minimize'\)/)
  assert.match(preload, /onMaximizeChange/)
  // preload.js 必须被打包进 asar（否则 window.c2vsdx 未暴露 → 标题栏不渲染）
  const pkg = JSON.parse(await read('../../electron/package.json'))
  assert.ok(pkg.build.files.includes('preload.js'), 'build.files 必须包含 preload.js')
  assert.ok(pkg.build.files.includes('main.js'))
  // 前端标题栏组件：仅窗口控制（设置已移除，回到 AppHeader）
  const tb = await read('./components/WindowTitleBar.vue')
  assert.match(tb, /-webkit-app-region:\s*drag/)
  assert.match(tb, /no-drag/)
  assert.doesNotMatch(tb, /ri-settings-3-line/)
  assert.doesNotMatch(tb, /ri-target-line/)   // 品牌用 BrandLogo 徽标（不再是靶心/回旋标）
  assert.match(tb, /BrandLogo/)
  assert.match(tb, /ri-subtract-line/)
  assert.match(tb, /ri-square-line/)
  assert.match(tb, /tb-glyph/)          // 还原态用内联 SVG（ri-restore-line 不存在）
  assert.match(tb, /ri-close-line/)
  // App 仅在桌面渲染标题栏，并为它预留 36px
  const app = await read('./App.vue')
  assert.match(app, /WindowTitleBar/)
  assert.match(app, /desktop-frame/)
  assert.match(app, /--titlebar-h:\s*36px/)
})

test('AppHeader 恢复返回/设置按钮；Electron 标题栏不再有设置', async () => {
  const header = await read('./components/AppHeader.vue')
  // 返回按钮：非首页显示（首页隐藏）
  assert.match(header, /v-if="!isHome"/)
  assert.match(header, /ri-arrow-go-back-line|ri-arrow-left-line/)
  // 设置按钮：始终显示（标题栏已移除设置入口）
  assert.match(header, /ri-settings-3-line/)
  assert.match(header, /isHome\s*=\s*computed\(/)
  assert.match(header, /function\s+back\s*\(/)
  assert.match(header, /function\s+settings\s*\(/)
  assert.match(header, /\.round-btn/)
  // 标题栏不再处理 open-settings
  const tb = await read('./components/WindowTitleBar.vue')
  assert.doesNotMatch(tb, /open-settings/)
  assert.doesNotMatch(tb, /defineEmits/)
})

test('BrandLogo 项目徽标：电光青圆角底 + 层级流程图（根上/两子下，非回旋标）', async () => {
  const logo = await read('./components/BrandLogo.vue')
  assert.match(logo, /background:\s*var\(--primary\)/)
  assert.match(logo, /color:\s*var\(--primary-on\)/)
  assert.doesNotMatch(logo, /background:\s*transparent/)
  // 层级流程图：根节点在上（x=8,y=3），两个子节点在下（x=2/x=14,y=15），分叉连线
  assert.match(logo, /<rect x="8" y="3"/)
  assert.match(logo, /<rect x="2" y="15"/)
  assert.match(logo, /<rect x="14" y="15"/)
  assert.match(logo, /M12 9v3M6 12h12M6 12v3M18 12v3/)
  // 旧品字排布（两个上、一个下）已移除
  assert.doesNotMatch(logo, /<rect x="2" y="3"/)
  assert.doesNotMatch(logo, /<rect x="8" y="15"/)
  // exe 图标源同步为层级图
  const icon = await read('../../electron/build/icon.svg')
  assert.match(icon, /M256 192v64M128 256h256M128 256v64M384 256v64/)
  assert.match(icon, /<rect x="171" y="64"/)
})

test('Diagram 预览/骨架 深色适配：无硬编码暖色，全部用 --diagram-* 令牌', async () => {
  const preview = await read('./components/DiagramPreview.vue')
  const skeleton = await read('./components/SkeletonDiagram.vue')
  const tokens = await read('./styles/tokens.css')
  // SVG 线条/填充全部改为主题令牌，不允许残留硬编码暖色
  assert.doesNotMatch(preview, /#[0-9A-Fa-f]{3,6}/)
  assert.doesNotMatch(skeleton, /#[0-9A-Fa-f]{3,6}/)
  // 浅/深主题都定义了 --diagram-* 令牌
  assert.match(tokens, /--diagram-line:\s*#C9C2B4/)       // light
  assert.match(tokens, /--diagram-border:\s*#D9D2C2/)
  assert.match(tokens, /\[data-theme="dark"\][\s\S]*--diagram-line:\s*#4A5568/)  // dark
  assert.match(tokens, /\[data-theme="dark"\][\s\S]*--diagram-border:\s*#3A4658/)
})

test('Toast 类型色条 + 关闭按钮跟随主题令牌（深色适配）', async () => {
  const app = await read('./App.vue')
  assert.match(app, /\.toast-bar-success\s*\{\s*background:\s*var\(--color-success\)/)
  assert.match(app, /\.toast-bar-error\s*\{\s*background:\s*var\(--color-error\)/)
  assert.match(app, /\.toast-bar-warning\s*\{\s*background:\s*var\(--color-warning\)/)
  assert.match(app, /\.toast-bar-info\s*\{\s*background:\s*var\(--color-info\)/)
  // 关闭按钮：浅色下不可用近白色（会隐形），改用主题令牌
  assert.match(app, /\.toast-close\s*\{[\s\S]*color:\s*var\(--ink-4\)/)
  assert.match(app, /\.toast-close:hover\s*\{[\s\S]*color:\s*var\(--ink\)/)
})

test('结果页统计/状态 + TypeCard/Model 按钮 on-primary 令牌化（深色适配）', async () => {
  const result = await read('./views/ResultView.vue')
  assert.doesNotMatch(result, /#008A62|#FFB347|#FF4D6D/)
  assert.match(result, /\.stat-warning\s*\{[\s\S]*color:\s*var\(--color-warning\)/)
  assert.match(result, /\.stat-danger\s*\{[\s\S]*color:\s*var\(--color-error\)/)
  const typeCard = await read('./components/TypeCard.vue')
  assert.doesNotMatch(typeCard, /#0A1628/)
  const model = await read('./components/settings/ModelSettingsView.vue')
  assert.doesNotMatch(model, /#0A1628/)
})

test('页脚移除企业信用/招标网站图标（仅品牌 + LightOS 链接）', async () => {
  const footer = await read('./components/AppFooter.vue')
  assert.doesNotMatch(footer, /footer-center/)
  assert.doesNotMatch(footer, /footer-chip/)
  assert.doesNotMatch(footer, /企业信用/)
  assert.doesNotMatch(footer, /招标网站/)
  assert.match(footer, /BrandLogo/)
  assert.match(footer, /lazycat\.cloud/)
})

test('侧边栏：品牌用项目 Logo（BrandLogo），激活态无竖条', async () => {
  const nav = await read('./components/SideNav.vue')
  assert.match(nav, /BrandLogo/)
  assert.doesNotMatch(nav, /ri-target-line/)
  assert.doesNotMatch(nav, /sidenav-accent/)
  assert.doesNotMatch(nav, /ri-home-4-line/)
})

test('设置页去掉恢复默认按钮；模型管理改二级标签（视觉模型/文本解析）', async () => {
  const theme = await read('./components/settings/ThemeSettingsView.vue')
  const model = await read('./components/settings/ModelSettingsView.vue')
  // 恢复默认按钮已移除
  assert.doesNotMatch(theme, /reset-btn/)
  assert.doesNotMatch(theme, /恢复默认/)
  assert.doesNotMatch(model, /reset-btn/)
  assert.doesNotMatch(model, /恢复默认/)
  // 模型管理：二级标签，点击显示对应设置项
  assert.match(model, /sub-tabs/)
  assert.match(model, /视觉模型/)
  assert.match(model, /文本解析/)
  assert.match(model, /v-if="tab === 'vision'"/)
  assert.match(model, /v-else/)
  assert.match(model, /const tab = ref\('vision'\)/)
  assert.match(model, /SUB_TABS/)
})

test('关于页：bid-maker 风格（居中品牌信息卡，无自身头部），版本取自 electron/package.json，仓库地址正确', async () => {
  const about = await read('./components/settings/AboutView.vue')
  // 版本来源：electron/package.json（根目录无 package.json）
  assert.match(about, /electron\/package\.json/)
  // 设置中心已有全局头部 → 关于页不再显示自身头部（面包屑/标题/副标题）
  assert.doesNotMatch(about, /page-header-card/)
  assert.doesNotMatch(about, /面包屑/)
  assert.doesNotMatch(about, /版本信息、开源仓库与版权声明/)
  // 品牌信息卡：圆形徽章（BrandLogo 而非回选标的）+ 名称 + 标语 + 版本 + GitHub + 版权
  assert.match(about, /about-card/)
  assert.match(about, /about-badge/)
  assert.match(about, /BrandLogo/)
  assert.doesNotMatch(about, /ri-target-line/)
  assert.match(about, /about-name/)
  assert.match(about, /C2VSDX/)
  assert.match(about, /about-slogan/)
  assert.match(about, /版本: v/)
  assert.match(about, /about-repo/)
  assert.match(about, /ri-github-line/)
  assert.match(about, /about-copy/)
  assert.match(about, /LightOS/)
  // 仓库地址正确（不再指向 yyjuan97/openvs.github.io）
  assert.match(about, /sikenali\/lzc2vsdx/)
  assert.doesNotMatch(about, /yyjuan97/)
})

test('设置中心三页不再显示各自头部（面包屑/标题/描述）；模型管理保留二级标签', async () => {
  const theme = await read('./components/settings/ThemeSettingsView.vue')
  const model = await read('./components/settings/ModelSettingsView.vue')
  const about = await read('./components/settings/AboutView.vue')
  // 三页均无自身头部组件
  for (const [name, src] of [['theme', theme], ['model', model], ['about', about]]) {
    assert.doesNotMatch(src, /header-card/, `${name} 不应有 header-card`)
    assert.doesNotMatch(src, /page-title/, `${name} 不应有 page-title`)
    assert.doesNotMatch(src, /breadcrumb/, `${name} 不应有面包屑`)
    assert.doesNotMatch(src, /crumb-sep/, `${name} 不应有面包屑分隔符`)
  }
  // 主题管理页保留其设置卡
  assert.match(theme, /外观主题/)
  assert.match(theme, /强调色/)
  assert.match(theme, /布局/)
  // 模型管理保留二级标签（视觉模型/文本解析）
  assert.match(model, /sub-tabs/)
  assert.match(model, /视觉模型/)
  assert.match(model, /文本解析/)
  assert.match(model, /v-if="tab === 'vision'"/)
})

test('强调色切换：5 色板 token 齐全；组件无硬编码强调色（按钮/渐变用 var）', async () => {
  const css = await read('./styles/tokens.css')
  // 5 个 accent 色板都定义 --primary + --tech-cyan-rgb（保证切换生效）
  for (const a of ['cyan', 'gold', 'green', 'blue', 'coral']) {
    assert.match(css, new RegExp(`\\[data-accent="${a}"\\][\\s\\S]*?--primary:`), `${a} 色板缺 --primary`)
    assert.match(css, new RegExp(`\\[data-accent="${a}"\\][\\s\\S]*?--tech-cyan-rgb:`), `${a} 色板缺 --tech-cyan-rgb`)
  }
  // 组件不再硬编码强调色（主按钮渐变 / 主色上文字色用 token）
  const model = await read('./components/settings/ModelSettingsView.vue')
  assert.doesNotMatch(model, /#00D4AA/)
  assert.match(model, /linear-gradient\(135deg,\s*var\(--primary\),\s*var\(--primary-deep\)\)/)
  const header = await read('./components/AppHeader.vue')
  assert.doesNotMatch(header, /#0A1628/)
  assert.match(header, /color:\s*var\(--primary-on\)/)
})
