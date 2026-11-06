# C2VSDX — 自然语言或图片，一键生成可编辑 Visio 图表

<p align="center">
  <strong>输入需求文本或上传图片，自动识别并生成可编辑的 Visio 流程图 · 跨平台桌面应用</strong>
</p>

<p align="center">
  <img src="electron/build/icon.png" width="120" height="120" alt="C2VSDX Logo">
</p>

<p align="center">
  <img alt="Electron" src="https://img.shields.io/badge/Electron-34-47848F?logo=electron&logoColor=white">
  <img alt="Vue" src="https://img.shields.io/badge/Vue-3-4FC08D?logo=vuedotjs&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow">
</p>

## 软件介绍

C2VSDX 是一款把自然语言或图片转成 Visio 图表的工具。文本侧用内置规则（或可选的 OpenAI 兼容 LLM）解析出 6 种图表结构；图片侧配置视觉模型后自动识别图形与连线；再由本地 Graphviz 布局、SVG 预览，在装有 Visio 的机器上导出可编辑 `.vsdx`。基于 Electron + Vue 3 + Flask 构建，覆盖 Windows 便携与 Linux AppImage 两条桌面交付路径。

**核心功能**

| 功能 | 说明 |
|------|------|
| 文本生成 | 流程图 / 时序图 / 组成图 / 关系图 / 架构图 / 泳道图，6 种图表 |
| 图片识别 | 上传 PNG/JPG/SVG/WebP，配置视觉模型后自动识别为图表 |
| 生成进度 | 分阶段进度条、节点/连线统计、SVG 预览、缩放与拖拽 |
| 在线微调 | 流程图节点/连线可视化编辑，保存后重新生成 |
| 导出 `.vsdx` | 真实可编辑 Visio 文件（需 Windows + Microsoft Visio 2016+） |
| 桌面打包 | Windows 便携 exe（单文件免安装）+ Linux AppImage（单文件免安装） |

## 技术实现

### 交付路径

1. **Windows 便携 exe**：`lzc2vsdx-win-x86_64-<version>.exe`（Electron portable 单文件，双击即用、免安装），约 101MB。
2. **Linux AppImage**：`lzc2vsdx-linux-x86_64-<version>.AppImage`（Electron 单包，内置 Graphviz），约 147MB，在任意 x86_64 Linux 桌面直接运行。

### 为什么是 Electron

桌面壳只需做一件事：启动时拉起 PyInstaller 打好的 Flask 后端（`c2vsdx-backend`），再加载内置的前端构建产物。后端与前端都由同一个 Electron 主进程管理，配置经 `userData/config.json` 持久化并注入后端环境变量，用户无需接触终端。

### 核心模块

| 模块 | 说明 |
|------|------|
| `backend/app.py` | Flask API + 静态托管（健康检查 / 分析 / 任务 / SSE 事件流 / 下载 / 微调） |
| `backend/parser.py` | 文本/图片 → OpenVS JSON（内置规则解析 + 可选 LLM / 视觉模型） |
| `backend/jobs.py` | 内存任务、SSE 进度、预览渲染、`.vsdx` 导出调度 |
| `backend/compact_layout.py` | 结果页紧凑布局（Web 展示层，不改底层脚本） |
| `backend/c2vsdx/` | 6 种图表布局引擎 + Graphviz 二进制 + references 规范 |
| `frontend/src/` | Vue 3 前端（5 个页面 + 顶栏 / 页脚 / 类型卡 / 进度 / 预览 / 微调抽屉） |
| `electron/main.js` | Electron 主进程：启动后端 + 注入 `OPENVS_*` 环境变量 + IPC 桥 |
| `electron/preload.js` | `contextBridge` 暴露 `window.c2vsdx`（模型配置读写） |
| `scripts/build_backend.py` | PyInstaller 把 Flask 后端打成单文件可执行程序 |
| `.github/workflows/ci.yml` | 远端构建验证（后端 pytest + 前端单测 + 构建） |
| `.github/workflows/build-desktop.yml` | 远端打包 Windows exe + Linux AppImage + 发布 Release |

### 构建

```bash
# 1. 打后端单文件（Windows 产出 .exe，Linux 产出 ELF）
python3 -m pip install -r backend/requirements.txt pyinstaller
python3 scripts/build_backend.py

# 2. 打前端
cd frontend && npm ci && npm run build && cd ..

# 3. 打桌面包
cd electron && npm ci
npx electron-builder --win portable --x64    # Windows 单文件 exe
npx electron-builder --linux AppImage --x64  # Linux AppImage
# Linux 打包前如需内置 Graphviz：bash scripts/bundle_graphviz_linux.sh
```

产物在 `electron/release/`：
- `lzc2vsdx-win-x86_64-<version>.exe`（单文件便携版）
- `lzc2vsdx-linux-x86_64-<version>.AppImage`

### 模型管理（视觉 / 文本）

设置中心「模型管理」页配置 OpenAI 兼容模型，持久化到 `userData/config.json`，重启应用后由 Electron 注入后端：

| 变量 | 说明 |
|------|------|
| `OPENVS_VISION_BASE_URL` / `OPENVS_VISION_API_KEY` / `OPENVS_VISION_MODEL` | 图片识别视觉模型；未配置时图片走演示数据 |
| `OPENVS_LLM_BASE_URL` / `OPENVS_LLM_API_KEY` / `OPENVS_LLM_MODEL` | 文本解析 LLM；未配置时用内置规则解析 |
| `OPENVS_PROGRESS_DELAY` | 每个阶段动画基准秒数，默认 1.6；测试用 0 |

### GitHub Actions

- `ci.yml`：push 到 `main` / PR 时跑后端 pytest + 前端单测 + 构建验证。
- `build-desktop.yml`：push tag（如 `v1.0.0`）构建两个平台并创建 GitHub Release；手动 `workflow_dispatch` 只构建上传 artifacts。

### 本地开发

```bash
cd backend && python3 app.py          # 后端 :5000
cd frontend && npm run dev            # 前端 :5173
cd electron && ELECTRON_DEV=1 npm start
```

### 测试

```bash
cd backend && python -m pytest tests -q
cd frontend && node --test src/*.test.mjs && npm run build
```

---

## 软件声明

### 重要声明

1. **仅限个人学习研究**
   本项目仅供网络协议分析、自动化脚本调试等技术实验使用，严禁投入盈利项目、商业场景以及一切违反当地法律法规的活动。

2. **无官方隶属关系**
   本项目与 Microsoft、Visio 及任何图表工具厂商不存在官方合作、授权或从属关系。图表导出依赖用户本机安装的 Microsoft Visio 2016+。

3. **知识产权与免责声明**
   图表内容版权归用户生成内容与第三方素材权利方所有。项目不保证服务的持续性、稳定性与适配性，对于使用本项目产生的一切直接、间接损失不承担任何责任。

## License

[MIT](./LICENSE)

<p align="center">Powered by LightOS</p>
