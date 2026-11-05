# 界面与前后端联调验收报告

日期：2026-11-04
环境：Linux（无 Visio，预览模式）；后端 `127.0.0.1:5000`，Graphviz dot 可用。

## 结论

- 界面功能：**已实现**。
- 前后端对接：**成功**。
- 自动化验收：**40 / 40 通过**，浏览器 `pageerror` 0，非预期 console error 0。
- 后端测试：`pytest` **21 passed**。
- 前端构建：`npm run build` 通过。

## 验收范围

| 模块 | 检查项 | 结果 |
|---|---|---|
| 顶栏 | 文本/图片切换、副标题、返回、设置 toast | 通过 |
| 页脚 | 品牌、企业信用/招标网站按钮 toast | 通过 |
| 文本页 | 6 张类型卡、单选切换、字数/段数、点击编辑、失焦展示、清空、模型下拉 | 通过 |
| 文本页 | 空文本拦截、生成跳转、返回后恢复上次输入 | 通过 |
| 图片页 | 上传卡、格式徽标、点击/拖拽/粘贴上传、预览、移除 | 通过 |
| 图片页 | 非法格式、>10MB、未上传拦截、生成跳转 | 通过 |
| 进度页 | 三步步骤条、进度推进、节点/连线统计、自动跳结果 | 通过 |
| 进度页 | 取消生成回到输入页、后端错误显示可读错误卡 | 通过 |
| 结果页 | 标题、状态、三张统计卡、SVG 预览 | 通过 |
| 结果页 | 缩放 50%–200%、放大后拖拽平移、刷新恢复 | 通过 |
| 结果页 | 导出（Linux 提示需 Windows）、重新生成 | 通过 |
| 结果页 | 在线微调：编辑节点、增删节点/连线、保存后重新生成 | 通过 |
| 图片结果 | 演示数据提示、统计、预览、微调限制提示 | 通过 |
| API | `/api/health`、6 种图表解析 | 通过 |
| API | 非法任务 422、未知 API 404 | 通过 |
| API | SSE 事件流、完成状态、下载 409（无 Visio） | 通过 |
| 联动 | 模型参数随请求发送、SSE 断开轮询兜底、运行中微调 409 | 通过 |

## 联调链路验证

1. 文本页 → `POST /api/text/analyze` → `POST /api/jobs` → `/text/progress/:id`
2. 进度页 SSE `/api/jobs/:id/events` → 自动跳 `/result/:id`
3. 结果页 `GET /api/jobs/:id` 恢复数据 → SVG 预览
4. 微调 `POST /api/jobs/:id/tweak` → 进度 → 结果
5. 图片页 `POST /api/image/analyze` → `POST /api/jobs` → `/image/progress/:id`
6. 取消 `POST /api/jobs/:id/cancel` → 回到输入页
7. 导出 `GET /api/jobs/:id/download`

## 错误路径验证

单独启动无 Graphviz 的后端（端口 5003）生成任务，进度页显示：

> 布局需要 Graphviz dot：Windows 请保留 backend/c2vsdx/graphviz-bin；Linux/macOS 请安装系统 Graphviz（apt install graphviz）

并给出“返回重新上传”按钮，没有卡死或 500。

## 已修复的验收问题

- 极小图片（如 1×1）预览容器塌缩，导致“移除图片”按钮被裁切、无法点击。已给预览容器加最小尺寸并居中。
- 页脚两个图标按钮原本无响应，已接入 toast 反馈。

## 已知限制

- `.vsdx` 实际导出需 Windows + Visio，本机无法验证真实下载文件。
- 图片真实识别需配置视觉模型；未配置时使用演示数据并在结果页持续标注。
- 在线微调当前仅支持“文本生成的流程图”。
- 模型下拉是界面选项，当前未改变后端解析模型（后端默认规则解析，配置 LLM 后走环境变量模型）。

## 设置中心（主题管理 + 关于）验收

日期：2026-11-05
范围：新增设置中心，包含主题 store（模式/强调色/布局）、深色与强调色 tokens、主题管理视图、关于视图、设置弹窗与侧边布局外壳。

| 检查项 | 结果 |
|---|---|
| 主题 store：模式/强调色/布局切换并持久化，非法值回退默认 | 通过 |
| 深色模式与强调色 CSS 变量 tokens | 通过 |
| 设置弹窗开关 | 通过 |
| 主题管理渲染与切换（模式/强调色/布局） | 通过 |
| 关于页渲染 | 通过 |
| 布局切换（侧边布局外壳） | 通过 |

验证证据（`cd frontend && node --test src/theme.test.mjs && npm run build && node /tmp/opencode/shotenv/settings.mjs && node /tmp/opencode/shotenv/verify.mjs`）：

- `theme.test.mjs`：**5 / 5 通过**。
- `npm run build`：成功。
- `settings.mjs`：**4 / 4 通过**（设置弹窗开关、主题管理渲染与切换、关于页渲染、布局切换）。
- `verify.mjs`：**40 / 40 通过**，`pageerror` 0，非预期 console error 0，无回归（含“设置按钮打开设置弹窗并关闭”断言）。

## 复现命令

```bash
cd backend && python3 -m pytest tests -q
cd frontend && npm run build
# 浏览器验收脚本位于 /tmp/opencode/shotenv/verify.mjs（本机）
node verify.mjs
```

---

## UI 优化（DESIGN.md 对齐，功能零改动）

按 `docs/superpowers/specs/2026-11-05-ui-polish-design.md`（源自 `docs/design-audit.md`）实现：

- **§9 Toast 重构**：顶部居中 20px、3px 类型色条（success/error/warning/info→绿/红/橙/蓝）、✕ 关闭、z-index 10000、`var(--bg-card)` 底、时长 2.5/2.0s；事件契约 `c2vsdx-toast` 改为 `{type,message}`；抽 `utils/toast.js` 统一助手。
- **`--primary-fill`/`--primary-on` 拆分**：实底填充（btn-primary、step-circle.running、check-badge、BrandLogo、ThemeSettingsView 勾徽标）深色白字 ≥4.5:1（red 5.44 / gold 7.62 / green 4.05 / blue 4.93 / ink 11.19）。
- **圆角入体系**：`--radius-card` 16→14（lg）；`--radius-btn` 12 保留（§4.3）。
- **硬编码色→token**：`.soft-action`/`.btn-ghost` `#fff`→`var(--bg-card)`；`.stat-card.red` `#e74c3c`→`var(--red)`；`.check-badge` 边界 `#d9d2c2`→`var(--line)`。
- **A.11 按钮不灰置**：生成/保存按钮移除 `:disabled`，handler 内 `toast('info','进行中请稍候')` 守卫。
- **A.14 响应式**：ImageView 上传卡 `width:min(875px, calc(100vw-64px))`。
- **输入框 focus**：`.text-input:focus`/`.model-select:focus` 主色边框/outline + `--red-soft` 外发光。
- **A.3 页脚**：LightOS 加 `<a href="https://lazycat.cloud/">`。
- **路由懒加载**：5 视图 `() => import(...)`，index JS 160→125KB，拆 8 chunk。

验证证据（`cd frontend && node --test src/ui-polish.test.mjs && node --test src/theme.test.mjs && npm run build && node /tmp/opencode/shotenv/settings.mjs && node /tmp/opencode/shotenv/verify.mjs`）：

- `ui-polish.test.mjs`：**6 / 6 通过**（toast 契约、primary-fill/on、实底填充 token、按钮不灰置、响应式、懒加载、页脚链接）。
- `theme.test.mjs`：**6 / 6 通过**（无回归）。
- `npm run build`：成功（index 125.47KB / gzip 47.97KB，8 个 chunk）。
- `settings.mjs`：**4 / 4 通过**。
- `verify.mjs`：**40 / 40 通过**，`pageerror` 0（懒加载后各页均可达）。
