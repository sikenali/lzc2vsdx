# C2VSDX Web 版设计文档

日期：2026-11-04
状态：待确认

## 1. 目标与范围

把 `yyjuan97/openvs.github.io` 的 OpenVS Skills 能力**完整继承**到本项目，只重新实现前端。后端脚本、数据模型、布局引擎、Graphviz 依赖与 Visio COM 渲染全部保持原样。

### 目标

- 用 Vue 3 + Vite 实现 5 个页面，按 Calicat 设计稿 1:1 还原：
  1. 文本生成页
  2. 图片生成页
  3. 文本生成中状态页
  4. 图片生成中状态页
  5. 生成结果页
- 保留并复用原项目的：
  - 6 种图表数据模型与校验（flowchart / sequence / composition / component / architecture / swimlane）
  - 图片分析 JSON schema 与 `render_image.py`
  - 所有 Visio COM 渲染器（`flowchart/renderer.py` 等）
  - `generate.py` 的命令行入口语义
- 提供一个 Web 后端（Flask），把上述能力串成可交互的生成流程，并输出真实 `.vsdx`。

### 非目标

- 不重写后端功能：不替换 Graphviz、不重写 Visio COM 渲染器、不实现纯 Python `.vsdx` 写入器。
- 不改变原 6 种图表类型的 JSON schema。
- 不实现账号、数据库、多人协作、历史记录。
- 不打包 Windows exe。

### 关键约束

- 最终 `.vsdx` 生成仍要求 **Windows + Microsoft Visio 2016+**，且依赖随包的 `graphviz-bin`，这是完整继承原实现的直接结果。
- 开发环境为 Linux 时，布局、API、前端、预览可完整验证；`.vsdx` 导出只能做 dry-run，需在 Windows 上完成端到端验证。
- 前端所有页面以 1440px 设计宽度为基准，向下响应式收缩。

## 2. 方案选择

| 方案 | 内容 | 取舍 |
|---|---|---|
| A | 纯 Python 全链路（自研布局 + 自研 .vsdx 写入） | 跨平台，但重写渲染器，偏离“继承其余实现” |
| B | 仅前端 + Mock | 最快还原，但不继承功能 |
| **C（已选）** | 后端（含 graphviz-bin、Visio COM 渲染）完全继承；只重写前端为 Vue | 功能与源码行为一致；导出依赖 Windows + Visio |

选择 C 的理由：用户明确要求“完全继承功能，只是前端页面重新实现”。

## 3. 总体架构

```
浏览器 (Vue 3 SPA)
   │  REST + SSE
   ▼
Flask API (backend/app.py)
   │
   ├─ 文本解析器（本地规则；可选 LLM）
   ├─ 图片分析器（可选视觉 LLM）
   ├─ 任务队列（内存，单进程线程池）
   ▼
backend/openvs/  ← 继承自 OpenVS_Skills/openvs-visio/scripts
   ├─ models + validate（原样）
   ├─ layout_engine（flowchart / component 改为纯 Python）
   ├─ renderer（原样，Windows + Visio COM）
   └─ generate.py（保留 CLI，Web 层调用同一 run()）
```

目录结构：

```
lzc2vsdx/
├─ frontend/                 Vue 3 + Vite + Vue Router
│  ├─ src/views/             TextView / ImageView / TextProgressView / ImageProgressView / ResultView
│  ├─ src/components/        AppHeader / AppFooter / TypeCard / ProgressSteps / DiagramPreview
│  ├─ src/styles/tokens.css  设计令牌（颜色、字体、阴影）
│  └─ src/api/client.ts
├─ backend/
│  ├─ app.py                 Flask 入口、API、SSE、静态文件托管
│  ├─ parser.py              文本 → JSON；图片 → JSON
│  ├─ jobs.py                内存任务与进度
│  ├─ openvs/                继承脚本 + graphviz-bin（原样）
│  └─ runtime/               生成的 .vsdx 与预览 JSON
├─ docs/superpowers/specs/
└─ README.md
```

## 4. 后端继承边界

以下内容从 `OpenVS_Skills/openvs-visio/scripts` 原样复制到 `backend/openvs/`，不做算法或行为修改：

- `flowchart` / `sequence` / `composition` / `component` / `architecture` / `swimlane` 的 models、校验、layout_engine、renderer
- `image2visio/` 与 `render_image.py`
- `config.py`（含 Graphviz PATH 注入）
- `graphviz-bin/`（随包二进制）
- `generate.py` 的 CLI 语义与退出码

只新增 Web 层胶水代码：

- `app.py`：Flask API、SSE、静态托管
- `parser.py`：文本/图片 → 原项目 JSON schema（原项目由外部 Agent 完成这一步，Web 版需要内置适配器）
- `jobs.py`：内存任务与进度

`generate.py` 的 `run()` 被 Web 层直接调用；不复制、不修改其内部流程。

## 5. 后端 API

所有接口前缀 `/api`。任务为内存态，单进程；服务重启后任务丢失。

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 返回版本、Visio 可用性、LLM 配置状态 |
| POST | `/api/text/analyze` | `{diagram_type, text}` → `{title, data, stats}` |
| POST | `/api/image/analyze` | multipart `image` → `{title, analysis, stats}` |
| POST | `/api/jobs` | `{mode: text/image, diagram_type, data}` → `{job_id}` |
| GET | `/api/jobs/<id>` | 状态、阶段、百分比、结果摘要 |
| GET | `/api/jobs/<id>/events` | SSE：阶段切换、百分比、节点数、完成/失败 |
| POST | `/api/jobs/<id>/cancel` | 取消（渲染阶段不可中断，返回当前状态） |
| GET | `/api/jobs/<id>/preview` | 布局后的节点/边坐标，供结果页 SVG 渲染 |
| GET | `/api/jobs/<id>/download` | 下载 `.vsdx` |
| POST | `/api/jobs/<id>/tweak` | 在线微调：接收节点/边补丁，重新布局并渲染 |

### 进度阶段

文本模式：
- 文本解析（0–35%）
- 语义理解与结构抽取（35–80%）
- VSDX 生成（80–100%）

图片模式：
- 图片解析（0–35%）
- 结构识别（35–80%）
- VSDX 生成（80–100%）

SSE 事件：`stage`、`progress`、`stats`、`done`、`error`。

### 解析策略

- **文本**：默认使用本地规则解析器。识别段落、序号、`首先/然后/接着/最后`、`如果/若/否则/失败/成功`、箭头等；按图表类型生成对应 schema。设置 `OPENVS_LLM_BASE_URL`、`OPENVS_LLM_API_KEY`、`OPENVS_LLM_MODEL` 后优先走 OpenAI 兼容接口，并使用原项目 `references/parse-prompts/*.txt` 作为提示词。
- **图片**：设置 `OPENVS_VISION_MODEL` 后调用视觉模型产出 `image-schema` JSON。未配置时接口返回 422 与明确提示；开发/演示可用 `?demo=1` 返回标注为 demo 的示例分析，避免把假数据当真实结果。

### 失败处理

- JSON 校验失败 → 422，返回原 `ValidationError` 文本。
- 非 Windows / 无 Visio → 任务失败，错误信息指明“导出需要 Windows + Visio；布局与预览已生成”。
- 生成文件保存在 `backend/runtime/<job_id>/`，下载名使用图表标题。

## 6. 前端设计还原

### 设计令牌（来自设计稿）

| 令牌 | 值 |
|---|---|
| 页面底色 | `#FAF7F2` |
| 主红 | `#C0392B` |
| 主红浅底 | `#FBE9E7` |
| 主文字 | `#1F1D1A` |
| 次文字 | `#3A3A3A` |
| 弱文字 | `#8A8578` |
| 更弱文字 | `#A7A296` |
| 描边 | `#E5DFD3` |
| 浅描边 | `#EDE9E0` |
| 卡片底 | `#FFFFFF` |
| 浅米底 | `#F7F3EA` |
| 页脚底 | `#FCFBF8` |
| 成功绿 | `#4E9B7A` / 底 `#E4F0EA` |
| 警示橙 | `#F39C12` / 底 `#FEF5E7` |
| 蓝色 | `#4A72A8` / 底 `#E8F0F8` |
| 金色 | `#D3A93F` / 底 `#F7EEE0` |
| 圆角 | 卡片 14–16，按钮 10–12，胶囊 9999 |
| 字体 | Source Han Sans（Noto Sans SC）系统栈 |
| 图标 | Remix Icon（npm 包，离线） |

### 页面结构

**公共部分**
- 顶栏 72px：左品牌区（40px 红色 Logo、C2VSDX、分隔线、副标题），中间切换标签（图片生成 / 文本生成），右侧圆形返回与设置按钮。
- 页脚 58px：左品牌说明，中企业信用/招标网站小按钮，右版权。
- 主内容区左右 padding 32px，内容最大宽 1180px。

**1. 文本生成页**
- 左侧 360px：标题行（红条 + 标题 + 说明 + 已选数量），6 张类型卡片（36px 图标底、标题、副标题、18px 勾选徽标）。单选，切换立即更新。
- 右侧：512px 高编辑器卡片。头部 52px（图标 + 标题 + 字数/段数），正文 20/24 padding，标题 + 6 段正文 + 占位提示；底栏 52px（模型下拉 + 清空按钮）。
- 下方居中主按钮 52px（红色、投影），按钮下说明文字。
- 交互：输入实时统计字数/段数；清空；类型单选；生成后进入文本进度页。

**2. 图片生成页**
- 居中 875×345 上传卡片：80px 浅红圆形 + 上传图标，18px 主提示，14px 格式说明，四个 28px 格式徽标（P/J/S/W）。
- 支持点击、拖拽、粘贴；校验格式与 10MB 上限；选中后显示预览缩略图与移除按钮。
- 下方主按钮与说明同文本页。

**3. 文本生成中页**
- 顶部进度卡片：三步骤条（32px 圆、标题/副标题、连接线），整体进度行（图标 + 文案 + 百分比 + 剩余秒数），6px 进度轨道。
- 下方“图形结构构建中”卡片：标题行（红条 + 标题 + 说明 + 节点/连线统计），骨架预览区（虚线节点、浅色占位条、抽取箭头、底部说明）。
- 底部“生成中…”红色按钮 + “取消生成”白按钮 + 说明。
- 动画：步骤依次完成，百分比与剩余秒数平滑推进，骨架节点渐显。

**4. 图片生成中页**
- 结构同上，文案改为“图片解析 / 结构识别 / VSDX 生成”，骨架图为流程节点布局，中间高亮节点。
- 统计数字随 SSE 更新。

**5. 生成结果页**
- 标题行：24px 标题 + “已生成”绿色胶囊；右侧“重新生成”“在线微调”。
- 三张统计卡（80px 高）：图形节点（绿）、连接线（橙）、文本标签（红），数字 30px，右侧 26px 图标。
- 图形预览卡：标题行（红条 + 标题 + 8px 网格说明 + 缩放组 −/100%/+），预览区浅米底 + 细描边。
- 预览用 SVG 渲染真实节点/边：矩形、菱形、圆角/胶囊、颜色按节点类型；支持 50%–200% 缩放与拖拽平移。
- 底部：返回重新上传、导出 VSDX（真实下载）。
- “在线微调”打开侧边抽屉：节点文字编辑、增删节点/边，提交后重新布局渲染。

### 路由

```
/                     文本生成
/image                图片生成
/text/progress/:id    文本生成中
/image/progress/:id   图片生成中
/result/:id           结果
```

### 状态管理

轻量组合式函数 + `sessionStorage` 保存当前任务摘要；不使用 Pinia。刷新进度页时通过 `/api/jobs/<id>` 恢复。

### 响应式

- ≥1200px：按设计稿双栏。
- 768–1199px：左栏 320px，编辑器自适应。
- <768px：单栏堆叠，顶栏隐藏副标题，按钮全宽，预览区横向滚动。

## 7. 视觉验收

- 在 1440×900 视口逐页截图，与 Calicat 截图并排比对。
- 允许的差异：字体渲染（Source Han Sans 版本）、Remix 图标具体字形、浏览器抗锯齿。
- 不允许的差异：布局顺序、间距层级、颜色、圆角、字号层级、文案。

## 8. 测试与验证

- `pytest`：后端继承脚本可导入、原布局引擎可运行（Linux 上通过 Graphviz 二进制或跳过标记）。
- `pytest`：API（解析、任务状态、预览、取消、错误码）。Linux 上以 dry-run 验证布局；Visio 渲染用 mock 或跳过。
- `npm run build`：前端构建通过。
- 浏览器手动走通 5 个页面与 3 种主要流程。
- Windows 环境：实际导出 `.vsdx`，用 Visio 打开确认可编辑。

## 9. 风险与应对

| 风险 | 应对 |
|---|---|
| 本地文本解析质量有限 | 规则解析保底；LLM 适配器可无缝升级 |
| Linux 无法端到端导出 | 布局/预览/前端全验证；Windows 侧提供一键启动与验证清单 |
| Visio COM 单实例冲突 | 任务串行执行，渲染队列长度 1 |
| 图片解析无视觉模型 | 明确 422 + demo 模式，不伪造生产结果 |
| 字体缺失导致宽度偏差 | 使用系统字体栈；布局按估算宽度，不依赖实际字体度量 |

## 10. 交付物

- 可运行的 Vue 前端（5 页 1:1）。
- Flask 后端与继承的 OpenVS 脚本。
- 完整继承的后端脚本与 `graphviz-bin`。
- 启动说明、环境变量说明、Windows 导出说明。
- 布局与 API 测试。
