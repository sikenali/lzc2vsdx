# C2VSDX UI Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 对齐 DESIGN.md 视觉规范（§9 Toast / 圆角 / 硬编码色 / A.11 按钮 / A.14 响应式 / 深色对比度），功能零改动。

**Architecture:** 全部为前端 CSS/Vue 单文件改动。核心是 (a) `App.vue` Toast 重构 + 抽 `utils/toast.js`，(b) `tokens.css` 新增 `--primary-fill/--primary-on` 拆分（供实底填充，深色白字 ≥4.5:1）+ 圆角 `--radius-card` 16→14，(c) 各组件硬编码色→token，(d) `router.js` 懒加载。无路由/数据/后端改动。

**Tech Stack:** Vue 3 `<script setup>` + Vite；`node --test` 结构性断言；Playwright 浏览器验证（`verify.mjs`/`settings.mjs`）。

**Spec:** `docs/superpowers/specs/2026-11-05-ui-polish-design.md`（审计 `docs/design-audit.md` 的实现依据）

## Global Constraints

- 功能零改动：不改上传/生成/导出/主题/会话业务逻辑，不改数据流，不改后端。
- 不新增 npm 依赖（remixicon 按需引入**延后**，另立任务）。
- 保留现有 token 命名（`--bg/--ink/--red…`），不引入 `--color-*`。
- `--primary` 本身不改（仍驱动表面强调文字与 active 态）；仅新增 `--primary-fill/--primary-on` 供实底填充。
- 每项改动独立可回退；某项回归则回退该项而非整体。

## Review Focus

1. **Toast 事件契约**：`c2vsdx-toast` detail 从 string 改为 `{type,message}`，所有调用点（TextView/ImageView/ResultView/AppFooter/ThemeSettingsView）必须同步，否则 toast 显示 `[object Object]` 或消失。→ Task 1 断言各调用点 dispatch `{type,message}`。
2. **深色实底对比度**：`--primary-fill` 深色值须让白字 ≥4.5:1，gold 用 `--primary-on:#1F1D1A`。→ Task 2 断言 `[data-theme=dark]` 含 `--primary-fill`。
3. **按钮可点性**：移除 `:disabled` 后，执行中点击须 `toast('info','进行中请稍候')` 且不触发二次生成。→ Task 3 断言 TextView/ImageView/TweakDrawer 无 `:disabled` 且 handler 有 `if (loading) return toast(...)`。
4. **小屏不溢出**：`.upload-card` 用 `min(875px, calc(100vw-64px))`。→ Task 3 断言。
5. **懒加载不破路由**：`() => import(...)` 后全部 5 视图仍可达（verify.mjs 0 pageerror）。→ Task 4 断言 `router.js` 含 `() => import(`。

---

### Task 1: §9 Toast 重构 + 统一助手

**Files:**
- Create: `frontend/src/utils/toast.js`
- Modify: `frontend/src/App.vue`（toast UI + 事件监听 + 关闭）、`frontend/src/views/TextView.vue`、`frontend/src/views/ImageView.vue`、`frontend/src/views/ResultView.vue`、`frontend/src/components/AppFooter.vue`、`frontend/src/components/settings/ThemeSettingsView.vue`
- Test: `frontend/src/ui-polish.test.mjs`（本任务创建，后续任务追加断言）

**Interfaces:**
- Consumes: 现有 `window.dispatchEvent(new CustomEvent('c2vsdx-toast',{detail}))` 调用点。
- Produces: `toast(type, message)`（`utils/toast.js`），`type∈{success,error,warning,info}`；`App.vue` 监听 `c2vsdx-toast` 的 `{type,message}`。

- [ ] **Step 1: 写失败测试**（`ui-polish.test.mjs`）

```js
import test from 'node:test'
import assert from 'node:assert'
import { readFile } from 'node:fs/promises'

test('toast 事件契约为 {type,message}', async () => {
  const app = await readFile(new URL('./App.vue', import.meta.url), 'utf8')
  assert.match(app, /detail:\s*\{\s*type,\s*message\s*\}|detail:\s*toast|onToast\(.*\{/)
  assert.match(app, /top:\s*20px/)          // §9 顶部居中
  assert.match(app, /--green\)|--red\)|--orange\)|--blue\)/)  // 色条按类型
  const util = await readFile(new URL('./utils/toast.js', import.meta.url), 'utf8')
  assert.match(util, /type.*message|message.*type/)
})
```

- [ ] **Step 2: 运行确认失败**

Run: `cd frontend && node --test src/ui-polish.test.mjs`
Expected: FAIL（断言未匹配；`utils/toast.js` 不存在）

- [ ] **Step 3: 实现**

1. `frontend/src/utils/toast.js`：`export function toast(type='info', message='') { window.dispatchEvent(new CustomEvent('c2vsdx-toast', { detail: { type, message } })) }`。
2. `App.vue`：`.toast` 改 `top:20px; left:50%; transform:translateX(-50%); z-index:10000; width:min(420px,90vw); padding:12px 16px 12px 18px; border:0.7px solid var(--line); background:var(--bg-card)`；左侧 `3×20px` 色条（`:class="'toast-bar '+toast.type"`，色 `--green/--red/--orange/--blue`）；右侧 ✕ 关闭按钮；动画 `translateY(-12px)→0` 0.25s / 离开 `opacity→0, translateY(-8px)` 0.25s；时长 success/error/warning=2500ms、info=2000ms。
3. `onToast(event)` 读 `event.detail.type/message`。
4. 各调用点：`toast(message)` → `import { toast } from '../utils/toast'`，改传 `{type,message}`（成功→success、错误→error、警告→warning、提示→info），删除本地重复 `toast` 函数。

- [ ] **Step 4: 运行确认通过**

Run: `cd frontend && node --test src/ui-polish.test.mjs`
Expected: PASS

- [ ] **Step 5: 全量回归 + 提交**

```bash
cd frontend && npm run build && node /tmp/opencode/shotenv/settings.mjs && node /tmp/opencode/shotenv/verify.mjs
git add frontend/src && git commit -m "fix(ui): §9 toast top-center with type color bar + unified toast helper"
```
Expected: build ✓、settings.mjs 4/4、verify.mjs 40/40（0 pageerror）。

---

### Task 2: `--primary-fill/on` 拆分 + 圆角入体系 + 全部实底填充替换

**Files:**
- Modify: `frontend/src/styles/tokens.css`（新增 `--primary-fill/--primary-on` 浅/深 + 各强调色；`--radius-card` 16→14）
- Modify: `frontend/src/styles/base.css`（`.btn-primary` 用 `--primary-fill`/`--primary-on`、`.btn-ghost` bg→`var(--bg-card)`、删 `.btn-primary:disabled`）
- Modify: `frontend/src/components/ProgressSteps.vue`、`frontend/src/components/TypeCard.vue`、`frontend/src/components/BrandLogo.vue`、`frontend/src/components/ProgressPage.vue`、`frontend/src/components/settings/ThemeSettingsView.vue`、`frontend/src/components/settings/AboutView.vue`、`frontend/src/views/ResultView.vue`、`frontend/src/components/DiagramPreview.vue`
- Test: `frontend/src/ui-polish.test.mjs`（追加断言）

**Interfaces:**
- Consumes: Task 1 的 `ui-polish.test.mjs`。
- Produces: `--primary-fill`/`--primary-on` token（浅色 fill=var(--primary)、on=#fff，gold 时 on=#1F1D1A；深色 fill=更深饱和值、on 同浅色）；`--radius-card:14px`。

- [ ] **Step 1: 写失败测试（追加）**

```js
test('tokens 提供 primary-fill/on 与体系圆角', async () => {
  const css = await readFile(new URL('./styles/tokens.css', import.meta.url), 'utf8')
  assert.match(css, /--primary-fill:/)
  assert.match(css, /--primary-on:\s*#fff/i)
  assert.match(css, /\[data-theme="dark"\].*--primary-fill:/s)
  assert.match(css, /--radius-card:\s*14px/)
})
```

- [ ] **Step 2: 运行确认失败**

Run: `cd frontend && node --test src/ui-polish.test.mjs`
Expected: FAIL（`--primary-fill` 未定义）

- [ ] **Step 3: 实现**

1. `tokens.css`：`:root` 加 `--primary-fill: var(--primary); --primary-on:#FFFFFF`；gold accent 块加 `--primary-on:#1F1D1A`；`[data-theme=dark]` 加 `--primary-fill: #C0392B; --primary-on:#FFFFFF`（及 gold `--primary-fill:#D3A93F; --primary-on:#1F1D1A`）；`[data-theme=dark][data-accent=…]` 各块加 `--primary-fill`（gold `#D3A93F`、green `#3E8C6E`、blue `#4A72A8`、ink `#3A3B3F`，red 继承 base dark `#C0392B`）。`--radius-card: 16px→14px`。
2. 实底填充替换（`background:var(--red|--primary)` + 白字 → `background:var(--primary-fill); color:var(--primary-on)`）：`base.css` `.btn-primary`、`ProgressSteps` `.step-circle.done/.running`、`TypeCard` `.check-badge`、`BrandLogo` 图标底、`ProgressPage` 按钮、`ThemeSettingsView` 勾徽标/圆盘/选中卡、`AboutView` logo 圆。
3. `.btn-ghost` bg `#fff`→`var(--bg-card)`；`.btn-primary:disabled` 规则删除。
4. `ResultView` `.soft-action` bg `#fff`→`var(--bg-card)`、`.stat-card.red` color `#e74c3c`→`var(--red)`。
5. `DiagramPreview` 连线 `#D9D2C2/#C9C2B4/#B0A79A`→`var(--line-soft)/var(--ink-5)/var(--ink-6)`。

- [ ] **Step 4: 运行确认通过 + 深色对比度抽查**

Run: `cd frontend && node --test src/ui-polish.test.mjs && node --test src/theme.test.mjs`
Expected: 全 PASS；`theme.test.mjs` 原断言（含 `--red:var(--primary)`）不回归。

- [ ] **Step 5: 全量回归 + 提交**

```bash
cd frontend && npm run build && node /tmp/opencode/shotenv/settings.mjs && node /tmp/opencode/shotenv/verify.mjs
git add frontend/src && git commit -m "fix(ui): primary-fill/on split for solid fills, radius into system, hardcoded colors to tokens"
```
Expected: build ✓、settings.mjs 4/4、verify.mjs 40/40。

---

### Task 3: A.11 按钮不灰置 + A.14 响应式 + 输入框 focus

**Files:**
- Modify: `frontend/src/views/TextView.vue`、`frontend/src/views/ImageView.vue`、`frontend/src/components/TweakDrawer.vue`
- Test: `frontend/src/ui-polish.test.mjs`（追加断言）

**Interfaces:**
- Consumes: Task 1 的 `toast()`。
- Produces: 无新接口（移除 `:disabled`，handler 内守卫）。

- [ ] **Step 1: 写失败测试（追加）**

```js
test('生成/保存按钮不灰置 + 卡片响应式', async () => {
  const tv = await readFile(new URL('./views/TextView.vue', import.meta.url), 'utf8')
  const iv = await readFile(new URL('./views/ImageView.vue', import.meta.url), 'utf8')
  const tw = await readFile(new URL('./components/TweakDrawer.vue', import.meta.url), 'utf8')
  assert.doesNotMatch(tv, /:disabled/)
  assert.doesNotMatch(iv, /:disabled/)
  assert.doesNotMatch(tw, /:disabled/)
  assert.match(tv, /width:\s*min\(875px,\s*calc\(100vw\s*-\s*64px\)\)/)
  assert.match(iv, /width:\s*min\(875px,\s*calc\(100vw\s*-\s*64px\)\)/)
  assert.match(tv, /:focus/)   // 输入框 focus 主色边框+外发光
})
```

- [ ] **Step 2: 运行确认失败**

Run: `cd frontend && node --test src/ui-polish.test.mjs`
Expected: FAIL（`:disabled` 仍在 / `min(875px…` 未匹配 / 无 `:focus`）

- [ ] **Step 3: 实现**

1. 移除 `TextView` 生成按钮、`ImageView` 生成按钮、`TweakDrawer` 保存按钮的 `:disabled` 属性；handler 内 `if (loading) return toast('info','进行中请稍候')`（对应 `saving`）。
2. `TextView`/`ImageView` `.upload-card`：`width:875px; max-width:100%` → `width:min(875px, calc(100vw - 64px))`。
3. `.text-input:focus`、`.model-select:focus`：`border-color:var(--red); box-shadow:0 0 0 3px var(--red-soft)`。

- [ ] **Step 4: 运行确认通过**

Run: `cd frontend && node --test src/ui-polish.test.mjs`
Expected: PASS

- [ ] **Step 5: 全量回归 + 提交**

```bash
cd frontend && npm run build && node /tmp/opencode/shotenv/settings.mjs && node /tmp/opencode/shotenv/verify.mjs
git add frontend/src && git commit -m "fix(ui): no-gray primary buttons (A.11), responsive upload card (A.14), input focus ring"
```
Expected: build ✓、settings.mjs 4/4、verify.mjs 40/40。

---

### Task 4: 路由懒加载 + 页脚 LightOS 链接

**Files:**
- Modify: `frontend/src/router.js`、`frontend/src/components/AppFooter.vue`
- Test: `frontend/src/ui-polish.test.mjs`（追加断言）

**Interfaces:**
- Consumes: 无。
- Produces: 5 视图 `() => import(...)`；页脚 LightOS 为 `<a href="https://lazycat.cloud/">`。

- [ ] **Step 1: 写失败测试（追加）**

```js
test('路由懒加载 + 页脚链接', async () => {
  const router = await readFile(new URL('./router.js', import.meta.url), 'utf8')
  const footer = await readFile(new URL('./components/AppFooter.vue', import.meta.url), 'utf8')
  assert.match(router, /\(\)\s*=>\s*import\(/)
  assert.match(footer, /href="https:\/\/lazycat\.cloud\/"/)
})
```

- [ ] **Step 2: 运行确认失败**

Run: `cd frontend && node --test src/ui-polish.test.mjs`
Expected: FAIL（`() => import(` 未匹配 / 页脚无链接）

- [ ] **Step 3: 实现**

1. `router.js`：`import TextView …` → `component: () => import('./views/TextView.vue')`（5 视图全部）。
2. `AppFooter.vue`：`Powered by <a href="https://lazycat.cloud/" target="_blank" rel="noopener noreferrer">LightOS</a>`。

- [ ] **Step 4: 运行确认通过**

Run: `cd frontend && node --test src/ui-polish.test.mjs && node --test src/theme.test.mjs`
Expected: 全 PASS

- [ ] **Step 5: 全量回归 + 提交**

```bash
cd frontend && npm run build && node /tmp/opencode/shotenv/settings.mjs && node /tmp/opencode/shotenv/verify.mjs
git add frontend/src && git commit -m "perf(ui): lazy-load route views; footer LightOS link (A.3)"
```
Expected: build ✓、settings.mjs 4/4、verify.mjs 40/40（0 pageerror，懒加载后各页仍可达）。

---

### Task 5: 全量验证 + 文档记录

**Files:**
- Test: `frontend/src/ui-polish.test.mjs`（node --test 全量）、`/tmp/opencode/shotenv/settings.mjs`、`/tmp/opencode/shotenv/verify.mjs`
- Modify: `docs/verification.md`

**Interfaces:** 无新接口。

- [ ] **Step 1: 运行全部验证**

Run: `cd frontend && node --test src/ui-polish.test.mjs && node --test src/theme.test.mjs && npm run build && node /tmp/opencode/shotenv/settings.mjs && node /tmp/opencode/shotenv/verify.mjs`
Expected: 全 PASS、build ✓、settings.mjs 4/4、verify.mjs 40/40（0 pageerror）

- [ ] **Step 2: 更新 `docs/verification.md` 记录 UI 优化 + 提交**

```bash
git add docs/verification.md && git commit -m "docs: verify ui polish"
```

---

## Self-Review

- **Spec 覆盖**：设计文档 11 项 → Task 1（§9 Toast+助手）、Task 2（圆角/硬编码色/`--primary-fill`）、Task 3（A.11/A.14/focus）、Task 4（懒加载/页脚）、Task 5（验证）。remixicon 延后已在约束注明。✅ 全覆盖。
- **Step 扫描**：每步单一可检结果（写测试→失败→实现→通过→提交）。CSS 改动用结构性断言（grep）锁定，无歧义。✅
- **类型一致性**：`toast(type,message)` 在 Task 1 定义，Task 3 复用；`--primary-fill/on` 在 Task 2 定义，同任务消费。✅
- **Review Focus**：5 条各挂对应任务断言。✅
- **比例**：计划比设计文档短，无代码转录。✅
