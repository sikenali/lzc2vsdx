# C2VSDX UI 优化设计（不影响功能）

**日期**：2026-11-05
**来源**：`docs/design-audit.md`（DESIGN.md 审计）P0–P3 中与 UI 相关的条目
**约束**：功能不变（不改任何生成/上传/导出/主题业务逻辑）；不新增 npm 依赖；保留现有 token 命名

## 意图与 why

审计发现多处视觉偏离规范（§9 Toast、圆角、硬编码色、按钮灰置、响应式、深色反模式）。本次在不改功能的前提下，把界面视觉对齐 DESIGN.md，消除深色模式反模式。

## 目标 / 非目标 / 反目标

- **目标**：§9 Toast 结构、圆角入体系、硬编码色→token、A.11 按钮不灰置、A.14 卡片响应式、输入框 focus、页脚 LightOS 链接、`--primary-fill` 深色对比度、路由懒加载。
- **非目标**：不改业务逻辑（上传/生成/导出/主题/会话）、不改数据流、不改后端。
- **反目标**：任何导致既有功能回归的改动（toast 仍显示、按钮仍可点、主题仍切换、图表仍生成）。

## 方案（Approaches）

| 方案 | 取舍 | 结果 |
|------|------|------|
| 仅低风险 CSS 打磨 | 改动面最小，但 §9 Toast 与 A.11 仍偏离 | 用户未选 |
| P0–P2 | 覆盖面广，但留深色对比度残根（`--primary-fill`） | 用户未选 |
| **P0–P3 全部（选中）** | 最彻底，触 15 文件；每项均有精确规范值 | ✅ 采用 |

## 逐项决策（含我裁定的技术取值）

### 1. §9 Toast 重构（P0）
- 结构重写：位置 `top:20px; left:50%; translateX(-50%)`；`z-index:10000`；`width:min(420px,90vw)`；`padding:12px 16px 12px 18px`；`border:0.7px solid var(--line)`；`background:var(--bg-card)`；左侧 `3×20px` 色条（圆角 2px）；右侧 ✕ 关闭按钮。
- 类型色条：success=`var(--green)`、error=`var(--red)`、warning=`var(--orange)`、info=`var(--blue)`。
- 时长：success/error/warning=2500ms、info=2000ms。
- 动画：进入 `translateY(-12px)→0` 0.25s；离开 `opacity→0, translateY(-8px)` 0.25s。
- 事件契约：`c2vsdx-toast` detail 由 `string` 改为 `{ type, message }`。**这是唯一改契约处**，纯呈现（toast 仍显示，仅结构/位置/色条变）。
- 统一助手：抽 `frontend/src/utils/toast.js` 导出 `toast(type, message)`，替换 TextView/ImageView/ResultView/AppFooter/ThemeSettingsView 的 3+ 处重复 dispatch。

### 2. 圆角入体系（P1）
- `--radius-card: 16px → 14px`（§1 lg=14，对齐 §3.2 UploadCard=14）。
- `--radius-btn: 12px` **保留**（§4.3 结果页操作按钮规范明确用 12px，属体系内上下文值）。
- `--radius-item: 14px` 不变（lg，合规）。

### 3. 硬编码色 → token（P1，深色反模式）
- `.soft-action{background:#fff}` → `var(--bg-card)`（ResultView）。
- `.btn-ghost{background:#fff}` → `var(--bg-card)`（base.css）。
- `.stat-card.red{color:#e74c3c}` → `var(--red)`（ResultView）。
- DiagramPreview 连线 `#D9D2C2/#C9C2B4/#B0A79A` → `var(--line-soft)/var(--ink-5)/var(--ink-6)`（SVG 描边，深色下自动适配）。
- `.check-badge{color:#fff}` → `var(--primary-on)`（TypeCard）；ThemeSettingsView 勾徽标 `color:#fff` → `var(--primary-on)`。

### 4. A.11 按钮不灰置（P1）
- 移除 `TextView`/`ImageView` 生成按钮、`TweakDrawer` 保存按钮的 `:disabled` 属性。
- handler 内 `if (loading) return toast('info','进行中请稍候')`。
- `.btn-primary:disabled{opacity:.6}` 规则删除（无其他使用处）。
- 按钮执行中保持原色、可点击（loading 视觉由 `loading` 状态图标承担）。

### 5. A.14 卡片响应式（P1）
- `TextView`/`ImageView` `.upload-card`：`width:875px; max-width:100%` → `width:min(875px, calc(100vw - 64px))`。

### 6. 输入框 focus（P1，深色 §10.2）
- `.text-input:focus`、`.model-select:focus`：`border-color:var(--red); box-shadow:0 0 0 3px var(--red-soft)`。

### 7. 页脚 LightOS 链接（P2，A.3）
- `AppFooter` 右下角：`Powered by <a href="https://lazycat.cloud/" target="_blank" rel="noopener noreferrer">LightOS</a>`。

### 8. `--primary-fill` / `--primary-on` 拆分（P3，深色对比度残根）
- **动机**：`--primary` 同时当「表面强调文字」与「实底填充」；深色下亮色 `--primary` 上白字 3.87:1 <4.5。
- **新增 token**：
  - 浅色：`--primary-fill: var(--primary)`；`--primary-on: #FFFFFF`（gold accent 时 `--primary-on:#1F1D1A`）。
  - 深色：`--primary-fill` 用**更深饱和**值（白字 ≥4.5:1 且仍明显红/金/绿/蓝/墨）：red `#C0392B`、gold `#D3A93F`、green `#3E8C6E`、blue `#4A72A8`、ink `#3A3B3F`；`--primary-on` 同浅色（gold 用 `#1F1D1A`，其余白）。
- **替换实底填充用法**（`background:var(--red|--primary)` + 白字 → `background:var(--primary-fill); color:var(--primary-on)`）：
  - `base.css` `.btn-primary`、`ProgressSteps` `.step-circle`（done/running）、`TypeCard` `.check-badge`、`BrandLogo`、`ProgressPage` 按钮、`ThemeSettingsView` 勾徽标/圆盘、`AboutView` logo 圆。
- **注意**：`--primary` 本身**不改**（仍驱动表面强调文字与 active 态），仅新增 `--primary-fill/on` 供实底使用。深色下 `--red-2`（=primary-deep）保持。

### 9. 路由懒加载（P2，性能）
- `router.js`：5 个视图 `import X` → `component: () => import('./views/X.vue')`。

### 10. 统计卡 §4.4（P3）
- 保留产品语义（节点/连线/标签）与 soft 背景；仅 `.red` 硬编码 → `var(--red)`（已并入第 3 项）。

### 11. remixicon 按需引入（P3）—— **延后（我的裁决）**
- 理由：需新增 `@remixicon/vue` 依赖 + 替换 37 处 `<i class="ri-…">`，改动面大、属 bundle 体积优化而非 UI 视觉，与「不影响功能」高冲突。建议另立性能任务处理（或确认 woff2 单格式够用）。

## 留给实施者的说明
- 全部为前端 CSS/Vue 单文件改动，无路由/数据/后端改动。
- 验证：`npm run build` + `node --test` + `/tmp/opencode/shotenv/settings.mjs`（4 项）+ `verify.mjs`（40 项）须全绿；后端在 `127.0.0.1:5000`。
- 每项改动独立可回退；若某项引发回归，回退该项而非整体。
