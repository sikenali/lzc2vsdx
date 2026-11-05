# 设置中心（主题管理 + 关于）设计

日期：2026-11-05
范围：C2VSDX 前端设置中心弹窗、主题系统（浅色/深色 + 强调色 + 布局模式）、关于页。

## 意图与 why

顶栏 ⚙ 按钮目前只是 toast 占位。按 bid-platform 统一设计规范（`/home/jingle/opc/DESIGN.md` §5–§6）实现**功能化**的设置中心：主题管理与关于。用户明确要求：仅这 2 个标签；**主题管理需包含布局切换**。

## 目标

- 设置中心弹窗（§5）：头部 + `240px` 导航侧栏（主题管理/关于 2 项）+ 右侧内容区。
- 主题管理（§6）：外观主题（浅色羊皮纸 / 深色墨夜）、强调色（朱红/鎏金/玉绿/云蓝/黛墨）、布局切换（顶栏居中导航 / 侧边栏左侧导航）。
- 关于：品牌、版本、描述、技术栈、版权、链接。
- 全部持久化到 `localStorage`，**实时生效**（无整页 reload）。

## 非目标 / 反目标

- 不重命名全局 token 为 `--color-*`（保留现有 `--bg/--ink/--red…`，视觉值与规范一致）。
- 不做模板/技能/规则/模型/导出/个性等其余菜单项。
- 不做真实后端主题接口（纯前端 localStorage）。
- 布局切换不改业务流程，仅切换导航呈现（顶栏居中标签 ↔ 左侧竖排图标导航）。

## 约束

- 复用现有 Vue3 + Remix Icon；无新增依赖。
- 深色模式所有 token 需有对应值（对比度满足 §7 要求）。
- 强调色需同步影响已用 accent 的 `--red/--red-soft/--red-2/--shadow-btn`。

## 方案（已选）

1. **主题 store** `src/stores/theme.js`（reactive + localStorage `c2vsdx:theme`）：
   `{ mode:'light'|'dark', accent:'red'|'gold'|'green'|'blue'|'ink', layout:'topbar'|'sidebar' }`。
2. **tokens.css 重构**：浅色为默认；`[data-theme="dark"]` 覆盖背景/文字/边框；强调色由
   `--primary/--primary-soft/--on-primary` 驱动，并别名 `--red/--red-soft/--red-2/--shadow-btn`。
3. **App.vue**：按 `layout` 渲染 topbar shell（现状）或 sidebar shell（新增 `SideNav` 76px + 顶栏仅标题）。
4. **组件**：
   - `UiModal.vue`：`teleport` + 遮罩 `rgba(0,0,0,.4)` + `opacity .25s ease` + 圆角 `18px` + 阴影。
   - `SettingsModal.vue`：§5 结构，`menuItems=[{theme},{about}]`，侧栏切换右面板。
   - `ThemeSettingsView.vue`：§6 四张卡（页头卡、外观主题卡、强调色卡、布局切换卡）。
   - `AboutView.vue`：品牌/版本/技术栈/版权/链接。
   - `SideNav.vue`：§2.2（品牌图标点击回首页、导航按钮切 文本/图片 路由、底部版本）。
5. **入口**：AppHeader ⚙ 打开 SettingsModal；SideNav 两个导航按钮切 `/`、`/image`。
6. **布局切换**：实时响应 store（无 reload，独立应用无 Wujie 例外），toast 提示。

## 留给实现者

- 深色模式下各视图/组件的具体颜色微调（用 token 覆盖，不写死）。
- 关于页链接指向本仓库 GitHub 地址。
