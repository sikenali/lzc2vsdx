# C2VSDX 设计规范审计报告

**基准**：`/home/jingle/opc/DESIGN.md`（bid-platform 统一设计规范，§1–§11 + 附录 A.1–A.15，1190 行）
**对象**：C2VSDX 前端（5 页视图 + 设置中心 + Electron 壳）+ 继承引擎 `backend/c2vsdx/`
**审计性质**：设计图落地 / 原型差距 / 功能完整性 / 冗余 / 性能，五类
**日期**：2026-11-05
**前置裁决**：C2VSDX 非 bid-* 产品，DESIGN.md 仅作视觉规范参考；保留现有 token 命名（`--bg/--ink/--red…`）不改 `--color-*`；结果页用 Web 层紧凑布局（`backend/compact_layout.py`，对 OpenVS 原样继承的有意偏离，README 已注明）。

---

## 0. 总体结论

| 维度 | 评级 | 说明 |
|------|------|------|
| 设计图落地 | 🟡 大部分实现 | §5/§6/§2.2/§3.2 已按规范；§9 Toast、§4 结果页侧栏、§1 圆角体系偏离 |
| 原型差距 | 🟡 中等 | 主要差距在 Toast 结构与结果页左侧分类侧栏；其余为色值/圆角/按钮禁用等细节 |
| 功能完整性 | 🟢 完整 | 6 类图表端到端 done；上传→进度→结果→导出全链路通；设置中心（主题+关于）完整 |
| 冗余 | 🟢 低 | SSE 为主动、轮询仅回退（不并行）；toast 助手函数 3 处重复；remixicon 全量字体 |
| 性能 | 🟡 中 | 路由静态 import（违 §A.15 懒加载）；remixicon 字体 ~4.6MB 全量随包；SSE 模式良好 |

**已确认有意偏离（README 已注明）**：结果页用 Web 层紧凑布局 `backend/compact_layout.py`（对 OpenVS 原样继承），不实现 §4.1 的三栏骨架（左侧 300px 分类侧栏 + 结论卡）。

---

## 1. 设计图实现情况（对照 §1–§11 + 附录 A）

### ✅ 已按规范实现

| 规范 | 实现 | 证据 |
|------|------|------|
| §5 设置弹窗 | 240px 导航侧栏（主题管理/关于 2 项）、头部 48px 图标圆、✕ 关闭、内容区 flex:1 滚动 | `SettingsModal.vue` |
| §6 主题管理 | 4 张卡（页头/外观/强调色/布局），强调色 5 盘取自 §6.3 色值，布局切换实时生效 | `ThemeSettingsView.vue` |
| §6.3 强调色 | red `#C0392B`/gold `#D3A93F`/green `#3E8C6E`/blue `#4A72A8`/ink `#2F3640`，与规范逐字一致 | `stores/theme.js` ACCENTS |
| §2.2 侧边栏 | 76px 宽、0.7px 右边框、品牌 26px、导航按钮 56×56、激活 --primary-soft | `SideNav.vue` |
| §7 深色调色板 | `--bg #17171A`/`--bg-card #232324`/`--ink #F2F3F5`/`--line #2A2B2E` 等逐字一致 | `tokens.css` `[data-theme=dark]` |
| §7 深色强调色（裁决） | 每强调色深色 `--primary`（red #E05050 / gold #E0B84A / green #5CB98C / blue #82AEDD / ink #C9CDD4）≥4.5:1，`--primary-soft` 对应深色 soft | `tokens.css` `[data-theme=dark][data-accent=…]` |
| §8.1 UiModal | `<teleport to="body">`、遮罩 rgba(0,0,0,.4)、props 驱动尺寸（width/maxWidth/height）、ESC+遮罩关闭、opacity .25s | `UiModal.vue` |
| §3.2 UploadCard | 875px、345px、padding 40px 32px、radius 14px、icon-circle 80px、fmt 28px | `TextView.vue`/`ImageView.vue` |
| §2.1 顶栏结构 | 品牌区 + 居中标签 + 右侧按钮（返回/设置）三段式 | `AppHeader.vue` |
| §A.4 右上按钮 | 40px 圆钮、hover 文案「返回」「设置」、图标 18px | `AppHeader.vue` |
| §10.1/10.2 深色原则 | 强调色更亮（#E05050）、边框有可见度（#2A2B2E 差≈19）、文字四级分明 | `tokens.css` |

### ⚠️ 部分实现 / 偏离

| 规范 | 现状 | 差距 |
|------|------|------|
| §9 Toast | 底部居中 84px、无左侧色条、无 ✕ 关闭、无类型区分、z-index 100、背景深色 rgba、时长 2200ms | **显著偏离**（见 2.1） |
| §4 结果页 | 单列紧凑布局（标题/统计/预览/操作），**无左侧 300px 分类侧栏、无结论卡** | 见 2.2（有意偏离） |
| §4.4 统计卡 | 显示 图形节点/连接线/文本标签（绿/橙/红），非 通过/警告/风险；`.stat-card.red` 硬编码 `color:#e74c3c` | 语义与色值偏离（见 2.3） |
| §1 圆角体系 | `--radius-card:16px`、`--radius-btn:12px`（规范 6/10/14/18/24 无 16/12）；`--radius-item:14px` 合规 | 16 与 12 不入体系（见 2.4） |
| §A.11 按钮不灰置 | Text/Image 生成 + Tweak 保存用 `:disabled` + `.btn-primary:disabled{opacity:.6}` 灰置 | 执行中状态灰置违 A.11 例外（见 2.5） |
| §A.14 卡片响应式 | `width:875px; max-width:100%`，非 `min(875px, calc(100vw-64px))` | 小屏可能溢出（见 2.6） |
| §A.3 页脚 | 右下角 `© 2026 C2VSDX · Powered by LightOS` 为纯文本，**非 `<a href="https://lazycat.cloud/">` 链接** | 缺链接（见 2.7） |
| §10.2 输入框 focus | `.text-input` 无 `:focus` 主色边框+外发光 | 深色清单未满（见 2.8） |
| §10.2 按钮 hover | `.btn-primary:hover{filter:brightness(1.04)}`，非 `color-mix()` 阴影 | 深色清单未满（见 2.8） |
| §2.3 顶栏标签 | `.header-tabs` gap 6px、图标 18px ✓；但为产品内模式切换（文本/图片），非六星工具切换 | 见 2.9（边界可接受） |

### ❌ 未实现 / 不适用

| 规范 | 说明 |
|------|------|
| §4.2 左侧分类侧栏 | 结果页无此结构（有意偏离，见 2.2） |
| §8.6 Pagination | 本产品结果页为图形预览（无数据表格），分页不适用 |
| §8.2–8.5 UiInput/UiCheck/UiSwitch/UiSelect | 本产品无对应表单场景（上传页为拖拽 + 文本域 + 模型下拉自定义），未引入，合理 |
| §A.5 关于页布局 | 本产品 AboutView 为设置中心内页（无 1620px 布局约束），适配合理 |

---

## 2. 与原型/规范的差距（按严重度）

### 2.1 【高】Toast 组件未按 §9 实现

**现状**（`App.vue`）：`position:fixed; left:50%; bottom:84px`，`border-radius:10px`，`background:rgba(31,29,26,.9)`，`color:#fff`，`z-index:100`，消失 2200ms；仅一条消息，无类型、无色条、无关闭。

**§9 要求**：顶部居中距顶 20px、z-index 10000、`width:min(420px,90vw)`、`padding:12px 16px 12px 18px`、`border:0.7px solid var(--color-border)`、`background:var(--color-bg-white)`、**左侧 3×20px 色条（按 success/error/warning/info）**、**✕ 关闭按钮**、成功/错误/警告 2.5s / info 2.0s、进入 `translateY(-12px)→0` 0.25s、离开 `opacity→0, translateY(-8px)` 0.25s。

**差距**：位置（底→顶）、结构（缺色条/缺✕）、类型（单一→四型）、z-index（100→10000）、背景（深色→bg-white）、时长（2200→2500/2000）。当前 Toast 只满足「顶部居中」的反例（实际底部），属**最明显的设计偏离**。

**修复**：重写 `App.vue` `.toast` 为 §9 结构，`c2vsdx-toast` 事件 detail 由字符串改为 `{ type, message }`，各调用点（TextView/ImageView/ResultView/AppFooter/ThemeSettingsView）同步传类型；色条用 `--color-success/error/warning/info` 对应 token（本产品可用 `--green/--orange/--red/--blue`）。

### 2.2 【高】结果页无 §4 左侧分类侧栏（有意偏离，需知会）

**现状**（`ResultView.vue`）：标题行 → 提示 → 统计卡 → 预览卡 → 底部操作按钮，单列，无侧栏。

**§4.1/4.2 要求**：结果页「左侧 300px 分类侧栏（分类按钮 + 底部结论卡）」+ 主内容区（标题/统计/表格/分页/左下操作）。

**性质**：README 已注明采用 Web 层紧凑布局 `backend/compact_layout.py`（对 OpenVS 原样继承的有意偏离）。C2VSDX 结果页展示的是**图形预览**（SVG/VSDX 渲染），非「检查项数据表格」，故 §4 的「分类侧栏 + 结论卡 + 数据表格」骨架不直接适用。**结论：接受为有意偏离**，但建议在 README/文档中明确「结果页为何不用 §4 三栏骨架」（当前只说了紧凑布局来源，未说 §4 不适用的理由）。

### 2.3 【中】统计卡语义与色值偏离 §4.4

**现状**：`.stat-card.green`（图形节点）/`.orange`（连接线）/`.red`（文本标签），`.stat-card.red{color:#e74c3c}` 硬编码。

**§4.4**：通过=`rgba(228,240,234,1)`/success、警告=`rgba(253,246,227,1)`/warning、风险=`rgba(251,233,231,1)`/error；数字 30px Bold。

**差距**：本产品统计的是图表节点/连线/标签（贴合图形预览场景），非「检查通过/警告/风险」，语义差异合理；但 (a) `.red` 硬编码 `#e74c3c` 破坏深色模式（应 `var(--red)`/`--primary`），(b) 三卡背景用 `--green-soft/--orange-soft/--red-soft`，与 §4.4 的 `rgba(...)` 近似但未用规范值。**建议**：`.red` 改用 `var(--red)`；背景可用 §4.4 语义（若保留图形指标则维持 soft 亦可，注明为产品语义）。

### 2.4 【中】圆角不入 §1 体系

**现状**：`--radius-card:16px`、`--radius-btn:12px`、`--radius-item:14px`。
**§1**：sm=6/md=10/lg=14/xl=18/2xl=24/full=9999。

**差距**：16（card）与 12（btn）是体系外值。**建议**：card→`14px`（lg）或 `18px`（xl）、btn→`10px`（md）或 `14px`（lg）；若坚持 16/12 为产品特色，在 README 记录理由。`--radius-item:14px`（lg）合规。

### 2.5 【中】上传/生成按钮 `:disabled` 灰置违 A.11

**现状**：`TextView.vue:74`、`ImageView.vue` 生成按钮 `:disabled="loading"`；`TweakDrawer.vue:45` 保存 `:disabled="saving"`；`.btn-primary:disabled{opacity:.6}`。

**A.11**：主要操作按钮**不得用 `:disabled` 灰置**，在 handler 内判断前置条件并 toast；执行中状态可显示 loading 但**不灰置外观**（保持原色、可点击、点击时提示「进行中请稍候」）。

**差距**：当前生成/保存为「执行中状态」却灰置（opacity .6），违 A.11 例外。**建议**：移除 `:disabled`，改用 `loading` 图标 + handler 内 `if (loading) return toast('进行中请稍候')`；或保留灰置但降低 `opacity` 影响（`.btn-primary:disabled{opacity:.85}` 不显著）。上传页「生成」按钮同规则。

### 2.6 【低】UploadCard 响应式违 A.14

**现状**（`ImageView.vue:172`）：`width:875px; max-width:100%`。
**A.14**：单卡片模式必须 `width:min(875px, calc(100vw - 64px))`，**禁止硬编码 875px**。

**差距**：`max-width:100%` 在窄屏（<875px）时取父容器宽，但父容器 `.app-main` padding 32px，实际可用为 `100vw - 64px`，二者在极端小屏可能溢出或留白不均。**建议**：改为 `width:min(875px, calc(100vw - 64px))`。`TextView.vue` 同。

### 2.7 【低】页脚 LightOS 非链接（A.3）

**现状**（`AppFooter.vue:11`）：`© 2026 C2VSDX · Powered by LightOS` 纯文本。
**A.3**：应为 `© 2026 {{品牌名}} · Powered by <a href="https://lazycat.cloud/" target="_blank" rel="noopener noreferrer">LightOS</a>`。

**建议**：将 LightOS 包为指向 `https://lazycat.cloud/` 的 `<a>`，`target="_blank" rel="noopener noreferrer"`。

### 2.8 【低】深色模式 §10.2 清单未满 2 项

| §10.2 项 | 状态 | 说明 |
|---------|------|------|
| `--primary` ≥ #E05050 | ✅ | 修复波后 red=#E05050，全强调色 ≥4.5:1 |
| 边框与背景差 ≥10px | ✅ | `--line #2A2B2E` vs `--bg #17171A`，差≈19 |
| muted ≥ #A7AEB9 | ✅ | `--ink-4 #A7AEB9` |
| faint ≥ #86909C | ✅ | `--ink-5 #86909C` |
| 输入框 focus 主色边框+外发光 | ❌ | `.text-input` 无 `:focus` 样式（仅程序化 `.focus()`） |
| 按钮 hover 用 color-mix 阴影 | ⚠️ | `.btn-primary:hover{filter:brightness(1.04)}`，非 color-mix |
| 表格行 hover 背景 | ➖ | 无数据表格，不适用 |
| Modal 遮罩 ≥ rgba(0,0,0,.4) | ✅ | UiModal 遮罩 rgba(0,0,0,.4) |

**建议**：给 `.text-input`/`.model-select` 加 `:focus{border-color:var(--red); box-shadow:0 0 0 3px var(--red-soft)}`；`.btn-primary:hover` 可用 `filter:brightness(1.08)`（视觉等价，规范为建议非强制）。

### 2.9 【边界】顶栏标签非六星工具切换（§2.3 可接受）

**现状**：`.header-tabs` 为产品内「文本/图片」模式切换，gap 6px、图标 18px、品牌色（gold/blue）对齐 §2.3.2。
**§2.3**：适用于「切换同级工具」的标签（六星），**禁止自创**。

**判定**：C2VSDX 为单产品，其「文本/图片」为页面内分段控件（产品自身模式），非六星工具切换，§2.3 严格不强制；但样式已用品牌色 + 6px 间距 + 18px 图标对齐，**可接受**。无需改动。

---

## 3. 功能完整性

| 项 | 状态 | 证据 |
|----|------|------|
| 6 类图表端到端（flowchart/sequence/composition/component/architecture/swimlane） | ✅ done | `docs/integration-audit.md`、commit `bd7c696` |
| 文本生成（上传→进度→结果） | ✅ | `TextView`/`TextProgressView`/`ResultView` |
| 图片生成（上传→进度→结果，demo 回退） | ✅ | `ImageView`/`ImageProgressView`/`ResultView`（demo 提示已接入） |
| 结果页导出 VSDX（Windows+Visio 受限） | ✅ | `download()`，`downloadable` 判定 + toast 提示 |
| 在线微调（文本流程图） | ✅ | `TweakDrawer`（仅文本+流程图，其余 toast 提示） |
| 重新生成 / 返回重新上传 | ✅ | `ResultView` `regenerate()` |
| 设置中心（主题管理 + 关于） | ✅ | §5/§6 全实现，localStorage 持久化 |
| 布局切换（顶栏/侧边栏） | ✅ | `theme.layout`，实时生效无 reload |
| 深色/强调色持久化 | ✅ | `c2vsdx:theme` 键，boot 自动 apply |
| 任务取消 / 进度恢复 | ✅ | `cancelJob`，SSE 断线回退轮询 |
| 会话恢复（sessionStorage） | ✅ | `api/store.js` `loadSession/saveSession` |
| Electron 壳 | ✅ | 主进程 + 预览特殊形状 |

**缺口**：无。功能链路完整。

---

## 4. 冗余问题

| 项 | 说明 | 建议 |
|----|------|------|
| toast 助手函数 ×3 | `TextView.vue:146`、`ImageView.vue:69`、`ResultView.vue:155` 三处重复同一 1 行 dispatch | 抽到 `utils/toast.js`（同时顺带统一 §9 类型参数） |
| SSE + 轮询 | 轮询**仅**在 SSE `onerror`/`end` 断开时启动，不并行，**无冗余** | 保持 |
| remixicon 全量字体 | `dist/assets` 含 remixicon svg 3.0MB + eot 613KB + ttf 613KB + woff 260KB + woff2 189KB ≈ 4.6MB | 若用 `@remixicon/vue` 按需引入可瘦身；当前为 CSS 全量字体 |
| `.soft-action`/`.btn-ghost`/`.stat-card.red` 硬编码色 | 浅色 `#fff`/`#e74c3c` 与 token 重复 | 统一 `var(--bg-card)`/`var(--red)`（兼修深色） |
| 重复布局 class | `.soft-action`（ResultView）与 `.btn-ghost`（base.css）功能重叠 | 可选合并 |

---

## 5. 性能问题

| 项 | 现状 | 问题 | 建议 |
|----|------|------|------|
| **路由懒加载** | `router.js:2-6` **静态 import** 全部 5 视图 | 首屏 JS 更大（index.js 159KB 已含全部视图），**违 §A.15**「必须 `() => import(...)` 懒加载」 | 改 `component: () => import('./views/TextView.vue')` 等；结果/进度页独立 chunk |
| **图标字体** | remixicon 全量字体随包 ~4.6MB | 浏览器通常只下载 woff2 189KB，但 dist 含全部格式；字体为 CSS 引用 | 用 `@remixicon/vue` 按需图标（或确认 woff2 单格式够用） |
| bundle JS | index.js 159KB / CSS 169KB | 对单页应用中等，懒加载后更优 | 懒加载 + 路由级分包 |
| SSE | `subscribeJob` 用 `EventSource`，服务端事件流 | **良好**（无轮询空转），断线回退 1s 轮询 | 保持 |
| 图片预览 | `DiagramPreview` SVG 内联渲染 + `SkeletonDiagram` 骨架 | 预览为 SVG 轻量，无位图大图 | 保持 |
| `preview` 存 sessionStorage | 大 SVG 可能超 sessionStorage 限额（~5MB） | 复杂图预览字符串可能触限 | 可考虑 IndexedDB 或仅存元数据 |

---

## 6. 深色模式 §10.2 检查清单（逐项）

| 清单项 | 结果 | 证据 |
|--------|------|------|
| 强调色可辨识（≥#E05050） | ✅ | `[data-theme=dark][data-accent]` 各强调色 ≥4.5:1 |
| 边框有对比（差≥10） | ✅ | `--line #2A2B2E` vs `--bg #17171A` |
| muted 可读（≥#A7AEB9） | ✅ | `--ink-4 #A7AEB9` |
| faint 可读（≥#86909C） | ✅ | `--ink-5 #86909C` |
| 输入框 focus 主色边框+发光 | ⚠️ 部分 | `.text-input` 无 `:focus` 规则 |
| 按钮 hover color-mix 阴影 | ⚠️ 部分 | `.btn-primary:hover{filter:brightness(1.04)}` |
| 表格行 hover 背景 | ➖ 不适用 | 无表格 |
| Modal 遮罩 ≥rgba(0,0,0,.4) | ✅ | `UiModal` 遮罩 `rgba(0,0,0,.4)` |

**残留反模式**（`tokens.css`/组件中硬编码浅色值，深色下可能偏亮）：
- `.soft-action{background:#fff}`（ResultView:325）、`.btn-ghost{background:#fff}`（base.css:141）、`.stat-card.red{color:#e74c3c}`（ResultView:383）、`DiagramPreview` 连线 `#D9D2C2/#C9C2B4/#B0A79A`、`TypeCard .check-badge{color:#fff}`。

> 这些已在最终评审列为「残留 A/B」（`--primary` 兼做实底填充白字 3.87:1 <4.5，`.check-badge` 白对金 2.2:1 装饰性）。**建议后续拆分 `--primary-fill`**（更深实底填充，白字 ≥4.5:1）而非复用亮色 `--primary`。

---

## 7. 优先级修复建议

### P0（必须修，影响核心规范）
1. **§9 Toast 重构**：位置改顶部居中 20px、加 3px 类型色条 + ✕ 关闭、四类型区分、z-index 10000、时长 2.5/2.0s、背景 `var(--bg-card)`；`c2vsdx-toast` 改 `{type,message}` 并更新全部调用点。（当前最明显偏离）

### P1（应修，深色模式/体系一致性）
2. **`.soft-action`/`.btn-ghost`/`.stat-card.red`/`DiagramPreview` 硬编码色 → token**：修深色反模式。
3. **圆角体系**：`--radius-card` 16→14/18、`--radius-btn` 12→10/14（或 README 记录理由）。
4. **A.11 按钮不灰置**：生成/保存按钮移除 `:disabled` 灰置，改 handler 守卫 + toast（或降 opacity 影响）。
5. **A.14 卡片响应式**：`width:min(875px, calc(100vw-64px))`。
6. **输入框 `:focus` 主色边框 + 外发光**（深色 §10.2）。

### P2（应做，性能/可维护）
7. **路由懒加载** `() => import(...)`（§A.15，性能）。
8. **toast 助手抽 `utils/toast.js`**（去重，顺带 §9 类型）。
9. **页脚 LightOS 加 `<a href="https://lazycat.cloud/">`**（A.3）。

### P3（可选，低优先）
10. 统计卡背景改用 §4.4 `rgba(...)` 或注明产品语义；`.check-badge` 用 `ACCENTS.on`；拆分 `--primary-fill`（残留 A）；remixicon 按需引入。

---

## 8. 已裁决的有意偏离（知会伙伴）

| 偏离 | 理由 | 记录 |
|------|------|------|
| 结果页用 Web 层紧凑布局 | OpenVS 原样继承 | README 已注明 |
| 结果页无 §4 左侧分类侧栏 | 结果为图形预览非检查数据表格，§4 骨架不适用 | **本文 2.2**（建议 README 补充理由） |
| 深色强调色值 | DESIGN §7 未定义每强调色深色值，按「深色更亮」原则取自 §7/§2.3.2 | 裁决记录 |
| REPO_URL → 上游 openvs.github.io | git remote 为空 | 裁决记录 |
| `--primary` 兼做实底填充（残留 A） | 拆分 `--primary-fill` 成本高，暂接受，3.87:1 >3:1 | 最终评审 |
