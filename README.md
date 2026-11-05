# C2VSDX Web

OpenVS Skills 的 Web 版：**后端完整继承** `yyjuan97/openvs.github.io` 的
`OpenVS_Skills/openvs-visio`（含 `graphviz-bin`、6 种图表布局、Visio COM 渲染），
本地归档在 `backend/c2vsdx`；前端用 Vue 3 按 Calicat 设计稿 1:1 重写。

## 功能

- 文本 → 6 种图表（流程图 / 时序图 / 组成图 / 关系图 / 架构图 / 泳道图）
- 图片 → 图表（配置视觉模型后）
- 生成进度、节点/连线统计、SVG 预览、缩放
- 在线微调（流程图）、下载真实 `.vsdx`
- 未配置 Visio 时仍可完成布局与预览；导出需 Windows + Visio

## 目录

```
backend/
  app.py            Flask API + 静态托管
  parser.py         文本/图片 → OpenVS JSON（规则解析 + 可选 LLM）
  jobs.py           内存任务、SSE、预览、渲染
  compact_layout.py 结果页紧凑布局（Web 展示层，不改原脚本）
  c2vsdx/           原样继承的 scripts + graphviz-bin + references
  tests/
frontend/
  src/views/        5 个页面
  src/components/   顶栏、页脚、类型卡、进度、骨架图、预览、微调抽屉
docs/
```

## 快速启动

```bash
# 1. 后端依赖
python3 -m pip install -r backend/requirements.txt

# 2. 前端构建
cd frontend && npm install && npm run build && cd ..

# 3. 启动（Windows 需已安装 Visio）
cd backend && python3 app.py
# 打开 http://127.0.0.1:5000
```

开发模式（前端热更新，代理到 5000）：

```bash
cd backend && python3 app.py
cd frontend && npm run dev   # http://127.0.0.1:5173
```

## 环境变量

| 变量 | 说明 |
|---|---|
| `OPENVS_LLM_BASE_URL` / `OPENVS_LLM_API_KEY` / `OPENVS_LLM_MODEL` | OpenAI 兼容文本解析接口；不配置则用内置规则解析 |
| `OPENVS_VISION_MODEL` / `OPENVS_VISION_API_KEY` / `OPENVS_VISION_BASE_URL` | 视觉模型；不配置时图片接口返回 422，前端会以 `demo=1` 演示 |
| `OPENVS_PROGRESS_DELAY` | 每个阶段动画基准秒数，默认 1.6；测试用 0 |

## 平台说明

- `.vsdx` 导出：Windows 10+ + Microsoft Visio 2016+（继承原实现）。
- Linux/macOS 可运行后端与前端、完成布局与预览；导出会给出明确提示。
- 原脚本的 `config.py` 会把随包 `graphviz-bin` 加入 PATH；Linux 源码运行需要系统
  Graphviz（`apt install graphviz`），或把可用的 `dot` 放进 PATH。
- Linux AppImage 已内置 Graphviz（`scripts/bundle_graphviz_linux.sh`），无需用户安装。

## 测试

```bash
cd backend && python -m pytest tests -q
cd frontend && npm run build
```

## 桌面打包（Electron）

`electron/` 是桌面壳：启动时拉起 PyInstaller 打好的 Flask 后端，再加载内置前端。

```bash
# 1. 打后端单文件（Windows 产出 .exe，Linux 产出 ELF）
python3 -m pip install pyinstaller
python3 scripts/build_backend.py

# 2. 打前端
cd frontend && npm run build && cd ..

# 3. 打桌面包
cd electron && npm ci
npx electron-builder --win portable --x64    # Windows 单文件 exe
npx electron-builder --linux AppImage --x64  # Linux AppImage
# Linux 打包前如需内置 Graphviz：
# bash scripts/bundle_graphviz_linux.sh
```

产物在 `electron/release/`：
- `C2VSDX-<version>-windows-portable.exe`（单文件便携版）
- `C2VSDX-<version>-linux-x86_64.AppImage`

### GitHub Actions

`.github/workflows/build-desktop.yml` 会在以下时机构建两个平台：

- push tag（如 `v1.0.0`）：构建 + 创建 GitHub Release 并上传 exe/AppImage
- 手动 `workflow_dispatch`：只构建并上传 artifacts

Windows job 使用 `windows-latest` + Visio 环境不可用，因此只验证打包；实际
`.vsdx` 导出仍需在装有 Visio 的机器上运行生成的 exe。

本地开发 Electron 壳：

```bash
cd backend && python3 app.py          # 后端 :5000
cd frontend && npm run dev            # 前端 :5173
cd electron && ELECTRON_DEV=1 npm start
```

## Windows 导出验证清单

1. 安装 Microsoft Visio 2016+，确认 `Visio.Application` 已注册。
2. `cd backend && python -m pip install -r requirements.txt`（含 `pywin32`）。
3. `cd frontend && npm run build`，再 `cd backend && python app.py`。
4. 打开页面生成一张流程图，结果页点“导出 VSDX 文件”。
5. 用 Visio 打开下载的 `.vsdx`，确认形状可编辑、连线保留。
6. `/api/health` 应返回 `"visio": true`。

## 与设计稿的差异

- 字体使用系统 Source Han Sans / Noto Sans SC 栈；图标使用 Remix Icon。
- 结果页预览使用 Web 层紧凑布局（`compact_layout.py`），让流程图按设计稿呈
  多行紧凑排布；Visio 渲染复用同一份布局数据。其余图表仍使用原布局引擎。
- 设计稿中的统计数字来自示例图；页面显示真实生成结果。
