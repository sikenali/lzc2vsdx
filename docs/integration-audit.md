# 前后端功能与接口对接审计

日期：2026-11-04
范围：Vue 前端全部交互、Flask API、任务/SSE/渲染链路、Electron 壳。
环境：Linux 预览模式（无 Visio），Graphviz dot 可用。

## 结论

- 所有前端操作都有对应的本地逻辑或后端接口，没有“点了没反应”的按钮。
- 所有前端调用的接口均已实现，请求/响应字段与前端使用方式一致。
- 本轮审计发现并修复 9 处逻辑/对接问题（见下文“本轮修复”）。
- 自动化结果：浏览器验收 **40/40 通过**；后端 `pytest` **21 passed**；前端构建通过；无页面异常。

## 前端操作 → 后端接口对照

| 前端操作 | 接口 | 后端实现 | 状态 |
|---|---|---|---|
| 顶栏文本/图片切换 | 无（Vue Router） | — | 正常 |
| 顶栏返回 | 无（history） | — | 正常 |
| 顶栏设置 | 无（本地 toast） | — | 正常（仅提示） |
| 页脚两个图标 | 无（本地 toast） | — | 正常（仅提示） |
| 选择图表类型 | 随生成请求发送 `diagram_type` | `POST /api/text/analyze`、`POST /api/jobs` | 正常 |
| 模型下拉 | 随解析请求发送 `model` | `POST /api/text/analyze` | 正常 |
| 编辑/字数/段数/清空 | 无（本地状态） | — | 正常 |
| 文本生成 | `POST /api/text/analyze` → `POST /api/jobs` | `parse_text` → 任务线程 | 正常 |
| 图片点击/拖拽/粘贴/移除 | 无（本地 File） | — | 正常 |
| 图片生成 | `POST /api/image/analyze` → `POST /api/jobs` | `parse_image` → 任务线程 | 正常 |
| 进度页加载 | `GET /api/jobs/:id` + `GET /api/jobs/:id/events` | 任务快照 + SSE | 正常 |
| SSE 断开兜底 | 轮询 `GET /api/jobs/:id` | 同一快照接口 | 正常 |
| 取消生成 | `POST /api/jobs/:id/cancel` | 设置取消标记 | 正常 |
| 结果页加载/刷新 | `GET /api/jobs/:id` | 任务快照 | 正常 |
| 缩放/拖拽平移 | 无（本地 SVG） | — | 正常 |
| 导出 VSDX | `GET /api/jobs/:id/download` | `send_file` | 正常（Windows+Visio 才能生成文件） |
| 在线微调保存 | `POST /api/jobs/:id/tweak` | 校验 → 重启任务 | 正常（仅文本流程图） |
| 重新生成 | 无（Router） | — | 正常 |

## 后端接口清单

| 方法 | 路径 | 前端是否使用 | 说明 |
|---|---|---|---|
| GET | `/api/health` | 否 | 诊断接口：版本环境、Visio/Graphviz/LLM 状态 |
| POST | `/api/text/analyze` | 是 | 文本 → 原项目 schema；支持 `model` |
| POST | `/api/image/analyze` | 是 | 图片 → image-schema；`?demo=1` 演示 |
| POST | `/api/jobs` | 是 | 创建任务，服务端重新计算统计 |
| GET | `/api/jobs/:id` | 是 | 任务状态/阶段/预览/数据 |
| GET | `/api/jobs/:id/events` | 是 | SSE 进度流 |
| GET | `/api/jobs/:id/preview` | 否 | 单独预览接口（前端用任务快照里的 preview） |
| POST | `/api/jobs/:id/cancel` | 是 | 取消任务 |
| GET | `/api/jobs/:id/download` | 是 | 下载 `.vsdx` |
| POST | `/api/jobs/:id/tweak` | 是 | 微调后重新布局/渲染 |
| GET | `/`、`/<path>` | 是 | SPA 静态托管与 history 回退 |

> `/api/health` 与 `/api/jobs/:id/preview` 已实现但前端不主动使用；前者用于运维诊断，后者是任务快照预览的等价接口。

## 关键数据契约

- 文本解析返回：`{ title, data, stats }`
- 图片解析返回：`{ title, analysis, stats }`
- 创建任务请求：`{ mode, diagram_type, data, title, stats }`
- 任务快照：`{ id, mode, diagram_type, title, stats, data, stages, progress, status, error, warning, downloadable, preview }`
- 预览：`{ width, height, nodes[], edges[], lifelines? }`
- SSE：每帧一个完整任务快照，终止帧带 `event: end`
- 微调请求：`{ data }`（完整替换节点/连线）
- 下载：`application/vnd.ms-visio.drawing` 附件，文件名取任务标题

## 本轮审计发现并修复

1. **模型下拉原本只是界面选项**：已随 `POST /api/text/analyze` 发送 `model`；`c2vsdx-graph-v1` 强制规则解析，`v2` 在配置 LLM 时优先 LLM。
2. **SSE 提前断开会导致进度页卡住**：已增加 1 秒轮询兜底，SSE 异常时继续用 `GET /api/jobs/:id` 更新。
3. **运行中任务可被微调造成线程竞争**：`tweak` 对 `status=running` 返回 409。
4. **渲染阶段取消不生效**：渲染结束后检查取消标记，取消则丢弃文件并标记 `cancelled`。
5. **任务统计信任前端**：创建/微调时由服务端重新计算 `stats`，避免缓存或篡改不一致。
6. **图片结果类型标签缺失**：补充 `relationship / org_chart / mind_map / network / other` 映射。
7. **下载失败会跳转到 JSON 错误页**：改为 `fetch` + Blob 下载，失败时 toast；Electron 增加保存对话框（`will-download`）。
8. **极小图片预览导致移除按钮被裁切**：预览容器增加最小尺寸并居中。
9. **图片浮动文本未校验/未计入统计**：增加字段校验，预览渲染浮动文本，统计计入标签数。
10. **任务/运行目录无限增长**：超过 1 小时且已终止的任务自动清理内存与运行目录。
11. **微调新增节点 ID 可能重复**：加入自增序号。
12. **页脚按钮无反馈**：接入 toast。

## 错误路径

- 空文本 → 422
- 空图片 / 非法格式 / >10MB → 422
- 非法任务数据 / 非法微调 → 422
- 未知 API → JSON 404
- 无 Graphviz → 进度页显示可读错误卡
- 无 Visio → 任务完成但 `downloadable=false`，下载返回 409，前端提示
- 任务运行中微调 → 409

## 已验证证据

- 浏览器 40 项检查：文本/图片/进度/结果/微调/取消/缩放/刷新/API/SSE 全通过。
- 额外检查：模型参数随请求发送、SSE 断开后轮询兜底、图片 architecture 标题、取消状态显示。
- 后端 21 项测试：解析、任务、预览、取消、微调、下载文件、无 Visio 409、非法输入等。
- 前端 `npm run build` 通过；Electron `main.js` 语法检查通过。

## 剩余限制

- `.vsdx` 真实生成/打开需 Windows + Visio；Linux 只能验证接口、布局与预览。后端下载接口已用假文件测试 200/附件头。
- 图片真实识别需视觉模型；未配置时演示数据并在结果页标注。
- 在线微调仅文本生成的流程图；图片/其他图表显示提示。
- 设置面板、页脚链接目前是提示占位，不是真实后端功能。
- 任务保存在内存，重启后丢失；单机单用户，无鉴权。
- Electron 保存对话框与 Windows COM 渲染未在 CI 中做 GUI 级验证。

---

## OpenVS 功能清单对比（2026-11-05）

对照上游 OpenVS 的 6 种图形能力逐项端到端验证（解析 → 建任务 → 渲染 → 预览）：

| OpenVS 功能 | 实现 | 端到端结果 |
|---|---|---|
| 流程图 | `_parse_flowchart` + Graphviz 布局 | ✅ done，6 节点 5 连线 |
| 时序图 | `_parse_sequence` + 参与/消息/片段 | ✅ done，2 参与 3 消息 |
| 功能组成图 | `_parse_composition`（支持缩进/编号层级） | ✅ done，6 节点层级树 |
| 关系图 | `_parse_component` + provided/required 接口 | ✅ done，2 组件 1 依赖 3 接口 |
| 架构图 | `_parse_architecture`（识别“xx层”分层） | ✅ done，3 层 3 组件 |
| 泳道图 | `_parse_swimlane`（按角色识别泳道） | ✅ done，4 泳道 4 节点 |
| 文字一键成图 | `POST /api/text/analyze` | ✅ |
| 图片一键成图 | `POST /api/image/analyze`（?demo=1） | ✅ |
| 生成可编辑 `.vsdx` | `GET /api/jobs/:id/download` | ✅（Windows+Visio） |
| 无需装 Python | PyInstaller 单文件 + Electron | ✅ |

本轮对比后增强（使解析更贴近 OpenVS 语义）：

1. **功能组成图支持真正的层级**：按缩进/编号（1、1.1、1.1.1）生成 `level` 与 `parent_id` 树，而非全平铺到根。
2. **关系图补 required 接口**：每条依赖在调用方挂一个 required 接口，体现“接口提供与依赖关系”。
3. **架构图支持显式分层**：输入中出现“接入层/业务层/数据层”等以“层”结尾的行时按层归组。
4. **泳道图按角色自动识别泳道**：从“用户/前端/服务端/数据库…”中自动提取出现过的角色作为泳道。
5. **预览增强**：时序图 `fragments`（alt/opt/loop）框渲染；关系图组件内嵌接口列表；图片 `parallelogram/document/storage` 特殊形状；连线颜色/线宽/虚线样式透传；节点多行文本正确换行。
6. **图片解析兜底宽高比**：视觉模型未返回 `image_aspect` 时按实际图片尺寸计算。

已通过：后端 `pytest` 21 passed、前端构建、浏览器 40/40 无异常、6 类图表端到端全部 done。
