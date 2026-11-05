# Settings Center (Theme + About) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现按 bid-platform 设计规范的功能化设置中心：主题管理（浅色/深色 + 5 强调色 + 布局切换）与关于页，顶栏 ⚙ 打开，全部持久化、实时生效。

**Architecture:** 新增 reactive 主题 store（localStorage `c2vsdx:theme`，含 `mode/accent/layout`），通过 `<html data-theme data-accent>` 属性 + CSS 变量驱动全局样式与布局；新增 `UiModal`（teleport）承载 `SettingsModal`（240px 导航侧栏 2 项切换右面板），内含 `ThemeSettingsView`（4 张卡）与 `AboutView`；`App.vue` 按 `layout` 在顶栏壳/侧边栏壳间切换。

**Tech Stack:** Vue 3 (`<script setup>`), Remix Icon, CSS 变量, `node --test`（纯逻辑）, Playwright（浏览器验证）。无新增依赖。

**Spec:** `docs/superpowers/specs/2026-11-05-settings-design.md`（对应 `/home/jingle/opc/DESIGN.md` §5–§6 视觉值）

## Global Constraints

- 不新增 npm 依赖（Vue3/Remix Icon 已内置）。
- 保留现有 token 命名（`--bg/--ink/--red…`）；强调色通过 `--primary` 驱动并别名 `--red/--red-soft/--red-2/--shadow-btn`。
- 深色模式所有 bg/ink/line token 必须有 `[data-theme="dark"]` 覆盖，值取自 DESIGN.md §7 Dark 调色板。
- 布局切换**不整页 reload**，实时响应 store；独立应用无 Wujie 例外。
- localStorage key：`c2vsdx:theme`，默认 `{ mode:'light', accent:'red', layout:'topbar' }`。

## Review Focus

1. 深色模式下文本/边框对比度（§7）：`[data-theme=dark]` 下 `--ink` vs `--bg` 可读。→ Task 2 浏览器断言 computed `color` 与背景差异。
2. 强调色切换后所有用到 accent 的位置一致变色（含 `--shadow-btn`）。→ Task 2/3 浏览器断言 `--red` 计算值随 `data-accent` 改变。
3. 非法/缺失 localStorage 值回退默认，不崩溃。→ Task 1 单测 `normalizeTheme`。
4. 侧边栏模式下顶栏不显示品牌图标/文字与居中标签。→ Task 6 浏览器断言 `.header-brand` 隐藏、`.header-tabs` 隐藏。
5. 设置弹窗打开时锁定滚动、ESC/遮罩点击可关闭、重复打开不叠加。→ Task 5 浏览器断言。
6. 布局切换后 `App.vue` 真正切换壳（SideNav 出现/消失）。→ Task 6 浏览器断言。

---

### Task 1: 主题 store（纯逻辑 + 持久化）

**Files:**
- Create: `frontend/src/stores/theme.js`
- Test: `frontend/src/theme.test.mjs`

**Interfaces:**
- Consumes: 无（纯 JS 模块）
- Produces: `THEME_KEY`, `DEFAULT_THEME`, `ACCENTS`, `normalizeTheme(raw)`, `loadTheme()`, `saveTheme(t)`, `applyTheme(t, root=document.documentElement)`, `useTheme()`（reactive: `{ theme, setMode, setAccent, setLayout, reset }`）

- [ ] **Step 1: 写失败测试** `frontend/src/theme.test.mjs`（`node --test`）

```js
import test from 'node:test'
import assert from 'node:assert'
import { DEFAULT_THEME, ACCENTS, normalizeTheme, applyTheme } from './stores/theme.js'

test('normalizeTheme 回退非法输入到默认', () => {
  assert.deepEqual(normalizeTheme(null), DEFAULT_THEME)
  assert.deepEqual(normalizeTheme({}), DEFAULT_THEME)
  assert.deepEqual(normalizeTheme({ mode: 'x', accent: 'y', layout: 'z' }), DEFAULT_THEME)
  assert.deepEqual(normalizeTheme({ mode: 'dark' }), { ...DEFAULT_THEME, mode: 'dark' })
  assert.deepEqual(normalizeTheme({ accent: 'gold', layout: 'sidebar' }), { ...DEFAULT_THEME, accent: 'gold', layout: 'sidebar' })
})

test('ACCENTS 含 5 色且字段齐全', () => {
  const keys = Object.keys(ACCENTS)
  assert.deepEqual(keys, ['red', 'gold', 'green', 'blue', 'ink'])
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
```

- [ ] **Step 2: 运行确认失败**

Run: `cd frontend && node --test src/theme.test.mjs`
Expected: FAIL（`Cannot find module './stores/theme.js'`）

- [ ] **Step 3: 实现 `frontend/src/stores/theme.js`**

`ACCENTS` 用 DESIGN.md §6.3 色值（red `#C0392B`/soft `#FBE9E7`；gold `#D3A93F`/`#F7EEE0`；green `#3E8C6E`/`#E4F0EA`；blue `#4A72A8`/`#E8F0F8`；ink `#2F3640`/`#E9EBEE`），每项含 `name/color/soft/on/deep`（deep=加深，用于 `--red-2` 别名）。`normalizeTheme` 校验 `mode∈{light,dark}`、`accent∈keys`、`layout∈{topbar,sidebar}`，非法字段回退 `DEFAULT_THEME` 对应值。`applyTheme` 只写 `<html>` 的 `data-theme` 与 `data-accent`。`useTheme` 用 `reactive` 包裹，`setMode/setAccent/setLayout` 写 store + `saveTheme` + `applyTheme`。

- [ ] **Step 4: 运行确认通过**

Run: `cd frontend && node --test src/theme.test.mjs`
Expected: PASS（3 测试全过）

- [ ] **Step 5: 提交**

```bash
git add frontend/src/stores/theme.js frontend/src/theme.test.mjs
git commit -m "feat(settings): theme store with mode/accent/layout persistence"
```

---

### Task 2: tokens.css 深色模式 + 强调色别名 + main.js 引导

**Files:**
- Modify: `frontend/src/styles/tokens.css`
- Modify: `frontend/src/main.js`
- Test: `frontend/src/theme.test.mjs`（追加 2 断言）

**Interfaces:**
- Consumes: Task 1 的 `loadTheme/applyTheme`
- Produces: `--primary/--primary-soft/--primary-deep/--btn-shadow`（accent 驱动），`[data-theme="dark"]` 全部 bg/ink/line 覆盖

- [ ] **Step 1: 写失败测试（追加到 theme.test.mjs）**

```js
test('tokens 提供深色与强调色变量', () => {
  const css = await (await import('node:fs/promises')).readFile(new URL('./styles/tokens.css', import.meta.url), 'utf8')
  assert.match(css, /\[data-theme="dark"\]/)
  assert.match(css, /\[data-accent="gold"\]/)
  assert.match(css, /--red:\s*var\(--primary\)/)
})
```

- [ ] **Step 2: 运行确认失败**

Run: `cd frontend && node --test src/theme.test.mjs`
Expected: FAIL（断言未匹配）

- [ ] **Step 3: 修改 `tokens.css` + `main.js`**

`tokens.css`：默认浅色为现有值；`--primary/--primary-soft/--primary-deep/--btn-shadow` 由 `:root`（red）与 `[data-accent=gold|green|blue|ink]` 覆盖；别名 `--red:var(--primary)`、`--red-soft:var(--primary-soft)`、`--red-2:var(--primary-deep)`、`--shadow-btn:0 8px 20px var(--btn-shadow)`。追加 `[data-theme="dark"]` 覆盖：`--bg:#17171A;--bg-card:#232324;--bg-soft:#1C1C1F;--bg-footer:#232324;--ink:#F2F3F5;--ink-2:#DDE0E6;--ink-3:#C9CDD4;--ink-4:#A7AEB9;--ink-5:#86909C;--ink-6:#3A3B3F;--line:#2A2B2E;--line-soft:#2A2B2E` 及各 `*-soft` 深色变体。`main.js`：启动时 `const t = loadTheme(); applyTheme(t)`。

- [ ] **Step 4: 运行确认通过**

Run: `cd frontend && node --test src/theme.test.mjs && npm run build`
Expected: PASS + 构建成功

- [ ] **Step 5: 提交**

```bash
git add frontend/src/styles/tokens.css frontend/src/main.js frontend/src/theme.test.mjs
git commit -m "feat(settings): dark mode tokens and accent-color aliases"
```

---

### Task 3: ThemeSettingsView（主题管理 4 张卡，功能化）

**Files:**
- Create: `frontend/src/components/settings/ThemeSettingsView.vue`
- Test: `/tmp/opencode/shotenv/settings.mjs`（本任务创建，后续任务追加断言）

**Interfaces:**
- Consumes: Task 1 `useTheme`（`theme/setMode/setAccent/setLayout/reset`）+ `ACCENTS`
- Produces: 组件根 `settings-view`；卡内控件 class：`.theme-card`、`.accent-swatch`、`.layout-card`

- [ ] **Step 1: 实现 `ThemeSettingsView.vue`**

按 DESIGN.md §6 四张卡：页头卡（面包屑 `首页 / 设置中心 / 主题管理` + 标题 30px Bold + 描述 + 「恢复默认」outline 按钮 `reset()`）；外观主题卡（浅色/深色 2 张预览缩略图 `100%×128px`，顶条 28px + 内容 54px，选中勾选徽标，激活态 `--primary-soft` 背景 + `--primary` 边框，点击 `setMode`）；强调色卡（`ACCENTS` 5 个 80px 圆盘，选中内部白色 ✓，名称选中 Bold，点击 `setAccent`）；布局切换卡（顶栏/侧边栏 2 个 mockup `150px` 高，点击 `setLayout` + toast）。

- [ ] **Step 2: 创建 `/tmp/opencode/shotenv/settings.mjs` 并运行**（`t('主题管理渲染与切换')`）

Run: `node /tmp/opencode/shotenv/settings.mjs`
Expected: PASS（4 张卡存在；点击深色卡 → `html[data-theme=dark]`；点击鎏金 → `html[data-accent=gold]`）

- [ ] **Step 3: 提交**

```bash
git add frontend/src/components/settings/ThemeSettingsView.vue
git commit -m "feat(settings): theme management view with 4 cards"
```

---

### Task 4: AboutView（关于页）

**Files:**
- Create: `frontend/src/components/settings/AboutView.vue`

**Interfaces:**
- Produces: 组件根 `about-view`；类 `.about-logo/.about-name/.about-version/.about-tech`

- [ ] **Step 1: 实现 `AboutView.vue`**

品牌 logo（`BrandLogo`）+ 名称 `C2VSDX` + 版本 `v1.0.0` + 描述「自然语言或图片，一键生成可编辑 Visio 图表」+ 技术栈 chips（Vue 3 / Flask / Electron / Graphviz / Visio COM）+ 版权行「© 2026 C2VSDX · Powered by LightOS」+ 链接指向仓库。

- [ ] **Step 2: 在 settings.mjs 追加 `t('关于页渲染')` 并运行**（`.about-view` 可见、`.about-version` 含 `1.0.0`）

Run: `node /tmp/opencode/shotenv/settings.mjs`
Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add frontend/src/components/settings/AboutView.vue
git commit -m "feat(settings): about view"
```

---

### Task 5: UiModal + SettingsModal + 顶栏 ⚙ 接线

**Files:**
- Create: `frontend/src/components/UiModal.vue`
- Create: `frontend/src/components/SettingsModal.vue`
- Modify: `frontend/src/components/AppHeader.vue`
- Modify: `frontend/src/App.vue`

**Interfaces:**
- Consumes: Task 3 `ThemeSettingsView`、Task 4 `AboutView`
- Produces: `SettingsModal` 通过 `v-model`（`modelValue/update:modelValue`）控制开合；`App.vue` 持有 `showSettings`；`AppHeader` 触发 `openSettings` 事件

- [ ] **Step 1: 实现 `UiModal.vue`**

`<teleport to="body">` + 遮罩 `rgba(0,0,0,.4)` + 容器（设置中心用 `92vw/92vh/max 1400px/radius 16px/阴影`），`opacity .25s ease` 进入/离开，ESC 与遮罩点击关闭，`modelValue` 控制 `v-if`。

- [ ] **Step 2: 实现 `SettingsModal.vue`**

§5 结构：头部 48px 图标圆（`--primary-soft` bg + `--primary` 图标 `ri-settings-3-line`）+「设置中心」22px Bold + 副标题 13px Muted + 关闭 ✕；左侧导航侧栏 `240px`（`menuItems=[{key:'theme',label:'主题管理',icon:'ri-palette-line'},{key:'about',label:'关于',icon:'ri-information-line'}]`，条目高 52px，激活态 `--primary-soft` bg + 主色文字，点击切换 `active`）；右侧内容区 `flex:1` 垂直滚动，按 `active` 渲染 `ThemeSettingsView`/`AboutView`。

- [ ] **Step 3: 修改 `AppHeader.vue` + `App.vue`**

`AppHeader`：`settings()` 改为 `emit('open-settings')`；`App.vue`：`const showSettings = ref(false)`，`<AppHeader @open-settings="showSettings=true" />`，底部挂 `<SettingsModal v-model="showSettings" />`；打开时 `document.body.style.overflow='hidden'`，关闭恢复。

- [ ] **Step 4: 在 settings.mjs 追加 `t('设置弹窗开关')` 并运行**（点 ⚙ → `.settings-modal` 可见；ESC → 关闭；侧栏点「关于」→ `.about-view` 可见）

Run: `node /tmp/opencode/shotenv/settings.mjs`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add frontend/src/components/UiModal.vue frontend/src/components/SettingsModal.vue frontend/src/components/AppHeader.vue frontend/src/App.vue
git commit -m "feat(settings): settings center modal with nav sidebar"
```

---

### Task 6: SideNav + 应用布局壳切换 + 顶栏适配

**Files:**
- Create: `frontend/src/components/SideNav.vue`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/components/AppHeader.vue`

**Interfaces:**
- Consumes: Task 1 `useTheme`（`theme.layout`）
- Produces: `.app-shell.layout-sidebar`；`SideNav` 类 `.sidenav/.sidenav-btn.active`；`AppHeader` 类 `.sidebar-mode`

- [ ] **Step 1: 实现 `SideNav.vue`**

DESIGN.md §2.2：宽 `76px`，右侧 `0.7px` 边框；顶部品牌图标 `RiTargetLine` 26px 主色点击回 `/`；导航按钮 `56×56px` 图标 22px + 标签 11px，2 个（文本生成 `ri-file-text-line`、图片生成 `ri-image-line`），激活态 `--primary-soft` bg + 主色，点击切 `/`、`/image`；底部版本 `v1.0.0` 10.5px Muted。

- [ ] **Step 2: 修改 `App.vue` 布局壳**

`theme.layout==='sidebar'` 时渲染 `<div class="app-shell layout-sidebar"><SideNav/><div class="main-col"><AppHeader/><main/><AppFooter/></div></div>`，否则现状（`AppHeader`/`main`/`AppFooter` 直排）。`.layout-sidebar{flex-direction:row}`，`.main-col{flex:1;display:flex;flex-direction:column;min-width:0}`。侧栏模式下 `AppHeader` 隐藏 `.header-brand` 与 `.header-tabs`（仅标题靠左 + 右侧按钮）。

- [ ] **Step 3: 在 settings.mjs 追加 `t('布局切换')` 并运行**（设置里点侧边栏模式 → `.sidenav` 出现、`.header-brand` 隐藏；切回顶栏 → `.sidenav` 消失）

Run: `node /tmp/opencode/shotenv/settings.mjs`
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/SideNav.vue frontend/src/App.vue frontend/src/components/AppHeader.vue
git commit -m "feat(settings): sidebar layout shell and topbar adaptation"
```

---

### Task 7: 全量验证

**Files:**
- Test: `frontend/src/theme.test.mjs`（node --test 全量）、`/tmp/opencode/shotenv/settings.mjs`（已随各任务构建）

**Interfaces:** 无新接口。

- [ ] **Step 1: 运行全部验证**

Run: `cd frontend && node --test src/theme.test.mjs && npm run build && node /tmp/opencode/shotenv/settings.mjs && node /tmp/opencode/shotenv/verify.mjs`
Expected: node --test PASS、构建成功、settings.mjs 全 PASS、verify.mjs 40/40（无回归）

- [ ] **Step 2: 更新 `docs/verification.md` 记录 + 提交**

```bash
git add docs/verification.md
git commit -m "docs: verify settings center"
```
