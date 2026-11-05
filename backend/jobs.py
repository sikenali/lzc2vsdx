"""内存任务管理：解析 → 布局 → 预览 → Visio 渲染，附带 SSE 进度。"""
from __future__ import annotations

import importlib
import json
import os
import shutil
import sys
import threading
import time
import traceback
import uuid
from pathlib import Path

C2VSDX_DIR = Path(__file__).parent / "c2vsdx"
RUNTIME_DIR = Path(os.environ.get("C2VSDX_RUNTIME", Path(__file__).parent / "runtime"))
sys.path.insert(0, str(C2VSDX_DIR))

import config  # noqa: F401,E402 保留原项目的 PATH 注入行为

# PyInstaller onefile 下 config.py 的 __file__ 不一定与 c2vsdx/ 同级，
# 这里显式把随包的 graphviz-bin 加入 PATH（Windows 渲染流程图/关系图需要）。
_GV_BIN = C2VSDX_DIR / "graphviz-bin"
if _GV_BIN.is_dir():
    os.environ["PATH"] = str(_GV_BIN) + os.pathsep + os.environ.get("PATH", "")

# Electron AppImage 会通过 GRAPHVIZ_BIN 指向内置的 Linux Graphviz
_GV_OVERRIDE = os.environ.get("GRAPHVIZ_BIN", "")
if _GV_OVERRIDE and Path(_GV_OVERRIDE).is_dir():
    os.environ["PATH"] = _GV_OVERRIDE + os.pathsep + os.environ.get("PATH", "")

STAGES = {
    "text": [
        {"key": "analyze", "label": "文本解析", "detail": "正在读取需求文本"},
        {"key": "structure", "label": "语义理解与结构抽取", "detail": "正在抽取节点与连线"},
        {"key": "render", "label": "VSDX 生成", "detail": "等待中"},
    ],
    "image": [
        {"key": "analyze", "label": "图片解析", "detail": "正在识别图片结构"},
        {"key": "structure", "label": "结构识别", "detail": "正在还原图形层级"},
        {"key": "render", "label": "VSDX 生成", "detail": "等待中"},
    ],
}

STAGE_RANGES = ((0, 35), (35, 80), (80, 100))


def _delay() -> float:
    try:
        return float(os.environ.get("OPENVS_PROGRESS_DELAY", "1.6"))
    except ValueError:
        return 0.9


def visio_available() -> bool:
    """只有 Windows 且注册了 Visio.Application 才尝试 COM 渲染。"""
    if sys.platform != "win32":
        return False
    try:
        import winreg

        winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "Visio.Application"))
        import win32com.client  # noqa: F401
        return True
    except Exception:
        return False


def validate_payload(mode: str, diagram_type: str, data: dict) -> None:
    """在创建任务前做一次继承脚本的校验，错误直接 422。"""
    if mode == "image":
        from render_image import validate
        validate(data)
        return
    import generate

    if diagram_type not in generate.BUILDERS:
        raise ValueError(f"未知图表类型: {diagram_type}")
    builder, _, _ = generate.BUILDERS[diagram_type]
    model = builder(data)
    errors = model.validate()
    if errors:
        raise ValueError("数据校验失败:\n  - " + "\n  - ".join(errors))


class Job:
    def __init__(self, mode: str, diagram_type: str, data: dict, title: str, stats: dict):
        self.id = uuid.uuid4().hex[:12]
        self.mode = mode
        self.diagram_type = diagram_type
        self.data = data
        self.title = title
        self.stats = stats
        self.stages = [dict(s, status="pending") for s in STAGES[mode]]
        self.progress = 0
        self.status = "running"
        self.error = ""
        self.warning = ""
        self.preview = None
        self.layout_data = None
        self.file_path = None
        self.downloadable = False
        self.created = time.time()
        self.version = 0
        self.cancel_requested = False
        self.dir = RUNTIME_DIR / self.id
        self.dir.mkdir(parents=True, exist_ok=True)

    def bump(self):
        self.version += 1

    def snapshot(self, include_preview: bool = True) -> dict:
        payload = {
            "id": self.id,
            "mode": self.mode,
            "diagram_type": self.diagram_type,
            "title": self.title,
            "stats": self.stats,
            "data": self.data,
            "stages": self.stages,
            "progress": self.progress,
            "status": self.status,
            "error": self.error,
            "warning": self.warning,
            "downloadable": self.downloadable,
        }
        if include_preview:
            payload["preview"] = self.preview
        return payload


class JobManager:
    def __init__(self):
        self.jobs: dict[str, Job] = {}
        self.lock = threading.Lock()
        self.render_lock = threading.Lock()  # Visio COM 单实例，渲染串行

    def _prune(self):
        now = time.time()
        for job_id, job in list(self.jobs.items()):
            if now - job.created > 3600 and job.status in ("done", "error", "cancelled"):
                self.jobs.pop(job_id, None)
                shutil.rmtree(job.dir, ignore_errors=True)

    def create(self, mode: str, diagram_type: str, data: dict, title: str, stats: dict) -> Job:
        job = Job(mode, diagram_type, data, title, stats)
        with self.lock:
            self._prune()
            self.jobs[job.id] = job
        threading.Thread(target=self._run, args=(job,), daemon=True).start()
        return job

    def get(self, job_id: str) -> Job | None:
        return self.jobs.get(job_id)

    def restart(self, job: Job, data: dict, title: str, stats: dict) -> Job:
        job.created = time.time()
        job.data = data
        job.title = title or job.title
        job.stats = stats or job.stats
        job.stages = [dict(s, status="pending") for s in STAGES[job.mode]]
        job.progress = 0
        job.status = "running"
        job.error = ""
        job.warning = ""
        job.preview = None
        job.layout_data = None
        job.file_path = None
        job.downloadable = False
        job.cancel_requested = False
        job.bump()
        threading.Thread(target=self._run, args=(job,), daemon=True).start()
        return job

    def cancel(self, job_id: str) -> bool:
        job = self.get(job_id)
        if not job:
            return False
        job.cancel_requested = True
        job.bump()
        return True

    def _stage(self, job: Job, index: int, detail: str | None = None):
        for i, stage in enumerate(job.stages):
            if i < index:
                stage["status"] = "done"
            elif i == index:
                stage["status"] = "running"
            else:
                stage["status"] = "pending"
        if detail:
            job.stages[index]["detail"] = detail
        job.bump()

    def _advance(self, job: Job, index: int, detail: str, duration: float):
        start, end = STAGE_RANGES[index]
        job.stages[index]["detail"] = detail
        steps = 16
        for n in range(1, steps + 1):
            if job.cancel_requested:
                return False
            job.progress = round(start + (end - start) * n / steps)
            job.bump()
            time.sleep(duration / steps)
        job.stages[index]["detail"] = f"已完成 · {duration:.1f}s"
        return True

    def _run(self, job: Job):
        try:
            if not self._advance(job, 0, job.stages[0]["detail"], _delay() * 0.6):
                return self._cancelled(job)

            self._stage(job, 1, job.stages[1]["detail"])
            preview = self._build_preview(job)
            nodes = len(preview.get("nodes", []))
            if not self._advance(job, 1, f"进行中 · 已识别 {nodes} 个节点", _delay()):
                return self._cancelled(job)
            job.preview = preview
            job.bump()

            self._stage(job, 2, "正在生成 .vsdx 文件")
            if not self._advance(job, 2, "正在生成 .vsdx 文件", _delay() * 0.5):
                return self._cancelled(job)

            self._render(job)
            if job.cancel_requested:
                # 渲染阶段收到取消：丢弃已生成文件，保持状态一致
                if job.file_path and Path(job.file_path).exists():
                    Path(job.file_path).unlink(missing_ok=True)
                job.downloadable = False
                job.file_path = None
                job.status = "cancelled"
                job.progress = min(job.progress, 99)
                job.bump()
                return
            job.progress = 100
            job.status = "done"
            job.bump()
        except Exception as exc:
            job.status = "error"
            job.error = str(exc)
            job.progress = min(job.progress, 99)
            print(f"[job {job.id}] failed: {exc}\n{traceback.format_exc()}")
            job.bump()

    def _cancelled(self, job: Job):
        job.status = "cancelled"
        job.progress = min(job.progress, 99)
        job.bump()

    # ------------------------------------------------------------ preview

    def _build_preview(self, job: Job) -> dict:
        if job.mode == "image":
            from render_image import validate
            validate(job.data)
            return self._image_preview(job.data)

        import generate
        builder, layout_mod, _ = generate.BUILDERS[job.diagram_type]
        data = builder(job.data)
        errors = data.validate()
        if errors:
            raise ValueError("数据校验失败:\n  - " + "\n  - ".join(errors))
        try:
            data = importlib.import_module(layout_mod).compute_layout(data)
        except Exception as exc:
            message = str(exc).lower()
            if "executable" in message or "dot" in message or "libgvc" in message:
                raise ValueError(
                    "布局需要 Graphviz dot：Windows 请保留 backend/c2vsdx/graphviz-bin；"
                    "Linux/macOS 请安装系统 Graphviz（apt install graphviz）"
                ) from exc
            raise
        if job.diagram_type == "flowchart":
            from compact_layout import compute as compact
            data = compact(data)
        job.layout_data = data
        return self._text_preview(job.diagram_type, data)

    def _text_preview(self, diagram_type: str, data) -> dict:
        if diagram_type == "flowchart":
            return self._flowchart_preview(data)
        if diagram_type == "sequence":
            return self._sequence_preview(data)
        if diagram_type == "composition":
            return self._composition_preview(data)
        if diagram_type == "component":
            return self._component_preview(data)
        if diagram_type == "architecture":
            return self._architecture_preview(data)
        if diagram_type == "swimlane":
            return self._swimlane_preview(data)
        raise ValueError(f"未知图表类型: {diagram_type}")

    @staticmethod
    def _bounds(nodes, margin=0.8):
        if not nodes:
            return 10, 6
        min_x = min(n["x"] - n["w"] / 2 for n in nodes)
        max_x = max(n["x"] + n["w"] / 2 for n in nodes)
        min_y = min(n["y"] - n["h"] / 2 for n in nodes)
        max_y = max(n["y"] + n["h"] / 2 for n in nodes)
        return max(max_x - min_x + 2 * margin, 4), max(max_y - min_y + 2 * margin, 3)

    @staticmethod
    def _route_edges(nodes, edges):
        """给没有坐标的边补上正交折线，供前端 SVG 预览使用。"""
        by_id = {n["id"]: n for n in nodes}
        for edge in edges:
            src, tgt = by_id.get(edge["source"]), by_id.get(edge["target"])
            if not src or not tgt:
                edge["points"] = []
                continue
            sx, sy, tx, ty = src["x"], src["y"], tgt["x"], tgt["y"]
            if abs(sy - ty) < 0.01:
                if tx >= sx:
                    edge["points"] = [[sx + src["w"] / 2, sy], [tx - tgt["w"] / 2, ty]]
                else:
                    edge["points"] = [[sx - src["w"] / 2, sy], [tx + tgt["w"] / 2, ty]]
            elif ty > sy:
                mid = (sy + src["h"] / 2 + ty - tgt["h"] / 2) / 2
                edge["points"] = [[sx, sy + src["h"] / 2], [sx, mid], [tx, mid], [tx, ty - tgt["h"] / 2]]
            else:
                mid = (sy - src["h"] / 2 + ty + tgt["h"] / 2) / 2
                edge["points"] = [[sx, sy - src["h"] / 2], [sx, mid], [tx, mid], [tx, ty + tgt["h"] / 2]]

    @staticmethod
    def _offset(nodes, margin=0.8):
        min_x = min(n["x"] - n["w"] / 2 for n in nodes) if nodes else 0
        min_y = min(n["y"] - n["h"] / 2 for n in nodes) if nodes else 0
        return margin - min_x, margin - min_y

    def _flowchart_preview(self, data) -> dict:
        nodes = []
        for node in data.nodes:
            nodes.append({
                "id": node.id,
                "label": node.label,
                "x": node.x,
                "y": node.y,
                "w": node.width,
                "h": node.height,
                "shape": node.shape.value,
            })
        dx, dy = self._offset(nodes)
        for n in nodes:
            n["x"] += dx
            n["y"] += dy
        width, height = self._bounds(nodes)

        by_id = {n["id"]: n for n in nodes}
        edges = []
        for edge in data.edges:
            src, tgt = by_id.get(edge.source), by_id.get(edge.target)
            if not src or not tgt:
                continue
            sx, sy = src["x"], src["y"]
            tx, ty = tgt["x"], tgt["y"]
            if abs(sy - ty) < 0.01:
                if tx >= sx:
                    points = [[sx + src["w"] / 2, sy], [tx - tgt["w"] / 2, ty]]
                else:
                    points = [[sx - src["w"] / 2, sy], [tx + tgt["w"] / 2, ty]]
            elif ty > sy:
                points = [[sx, sy + src["h"] / 2], [sx, (sy + src["h"] / 2 + ty - tgt["h"] / 2) / 2],
                          [tx, (sy + src["h"] / 2 + ty - tgt["h"] / 2) / 2], [tx, ty - tgt["h"] / 2]]
            else:
                points = [[sx + src["w"] / 2, sy], [tx, sy], [tx, ty - tgt["h"] / 2]]
            edges.append({"source": edge.source, "target": edge.target, "label": edge.label,
                          "points": points, "dashed": False})
        return {"width": width, "height": height, "nodes": nodes, "edges": edges}

    def _sequence_preview(self, data) -> dict:
        nodes = []
        px = {p.id: p.x for p in data.participants}
        for p in data.participants:
            nodes.append({"id": p.id, "label": p.label, "x": p.x, "y": 0.9,
                          "w": 1.4, "h": 0.5, "shape": "rectangle"})
        edges = []
        for m in data.messages:
            sx = px.get(m.from_id, 0)
            tx = px.get(m.to_id, 0)
            edges.append({"source": m.from_id, "target": m.to_id, "label": m.label,
                          "points": [[sx, m.y], [tx, m.y]], "dashed": m.msg_type.value == "return"})
        width, height = self._bounds(nodes)
        height = max(height, (data.messages[-1].y + 0.8) if data.messages else 4)

        fragments = []
        for f in data.fragments:
            if f.start_y is None or f.end_y is None:
                continue
            ids = f.participant_ids or [p.id for p in data.participants]
            xs = [px[i] for i in ids if i in px]
            if not xs:
                continue
            fragments.append({
                "id": f.id,
                "label": f.label,
                "type": f.frag_type.value,
                "x1": min(xs) - 0.7,
                "x2": max(xs) + 0.7,
                "y1": f.start_y,
                "y2": f.end_y,
            })
        if fragments:
            width = max(width, max(f["x2"] for f in fragments) + 0.8)
            height = max(height, max(f["y2"] for f in fragments) + 0.4)
        return {"width": width, "height": height, "nodes": nodes, "edges": edges,
                "lifelines": [
                    {"id": p.id, "x": p.x, "y1": 1.15, "y2": height - 0.3} for p in data.participants
                ],
                "fragments": fragments}

    def _composition_preview(self, data) -> dict:
        nodes = [{"id": n.id, "label": n.label, "x": n.x or 0, "y": n.y or 0,
                  "w": n.width or 1.4, "h": n.height or 0.5, "shape": "rounded" if n.level == 0 else "rectangle"}
                 for n in data.nodes]
        dx, dy = self._offset(nodes)
        for n in nodes:
            n["x"] += dx
            n["y"] += dy
        edges = []
        for n in data.nodes:
            if n.parent_id:
                edges.append({"source": n.parent_id, "target": n.id, "label": "", "dashed": True})
        self._route_edges(nodes, edges)
        width, height = self._bounds(nodes)
        return {"width": width, "height": height, "nodes": nodes, "edges": edges}

    def _component_preview(self, data) -> dict:
        nodes = []
        for c in data.components:
            provided = data.get_provided_interfaces(c.id)
            required = data.get_required_interfaces(c.id)
            label = c.label
            if provided:
                label += "\n提供: " + "、".join(i.label for i in provided)
            if required:
                label += "\n依赖: " + "、".join(i.label for i in required)
            nodes.append({
                "id": c.id, "label": label, "x": c.x or 0, "y": c.y or 0,
                "w": c.width or 2,
                "h": (c.height or 1) + 0.24 * (len(provided) + len(required)),
                "shape": "rectangle",
            })
        dx, dy = self._offset(nodes)
        for n in nodes:
            n["x"] += dx
            n["y"] += dy
        edges = [{"source": d.from_id, "target": d.to_id, "label": d.label, "dashed": True}
                 for d in data.dependencies]
        self._route_edges(nodes, edges)
        width, height = self._bounds(nodes)
        return {"width": width, "height": height, "nodes": nodes, "edges": edges}

    def _architecture_preview(self, data) -> dict:
        nodes = []
        for layer in data.layers:
            nodes.append({"id": layer.id, "label": layer.label, "x": 4, "y": layer.y or 0,
                          "w": 7, "h": layer.height or 2, "shape": "layer"})
        for c in data.components:
            nodes.append({"id": c.id, "label": c.label, "x": c.x or 0, "y": c.y or 0,
                          "w": c.width or 1.6, "h": c.height or 0.8, "shape": "rectangle"})
        dx, dy = self._offset(nodes)
        for n in nodes:
            n["x"] += dx
            n["y"] += dy
        edges = [{"source": c.from_id, "target": c.to_id, "label": c.label, "dashed": False}
                 for c in data.connections]
        self._route_edges(nodes, edges)
        width, height = self._bounds(nodes)
        return {"width": width, "height": height, "nodes": nodes, "edges": edges}

    def _swimlane_preview(self, data) -> dict:
        nodes = [{"id": lane.id, "label": lane.label, "x": lane.x or 0, "y": 0,
                  "w": lane.width or 2, "h": 1, "shape": "lane"} for lane in data.lanes]
        nodes += [{"id": n.id, "label": n.label, "x": n.x or 0, "y": n.y or 0,
                   "w": n.width or 1.4, "h": n.height or 0.5,
                   "shape": n.shape.value if hasattr(n.shape, "value") else "rectangle"}
                  for n in data.nodes]
        dx, dy = self._offset(nodes)
        for n in nodes:
            n["x"] += dx
            n["y"] += dy
        edges = [{"source": e.source, "target": e.target, "label": e.label, "dashed": False}
                 for e in data.edges]
        self._route_edges(nodes, edges)
        width, height = self._bounds(nodes)
        return {"width": width, "height": height, "nodes": nodes, "edges": edges}

    def _image_preview(self, analysis: dict) -> dict:
        aspect = float(analysis.get("image_aspect") or 1.78)
        if aspect >= 1.15:
            pw, ph = 11.0, 8.5
        elif aspect <= 0.87:
            pw, ph = 8.5, 11.0
        else:
            pw, ph = 10.0, 10.0
        nodes = []
        for s in analysis.get("shapes", []):
            nodes.append({
                "id": str(s["id"]),
                "label": s.get("text", ""),
                "x": (float(s["x"]) + float(s["width"]) / 2) * pw,
                "y": (float(s["y"]) + float(s["height"]) / 2) * ph,
                "w": float(s["width"]) * pw,
                "h": float(s["height"]) * ph,
                "shape": s.get("type", "rectangle"),
                "fill": s.get("fill_color"),
                "border": s.get("border_color"),
                "text_color": s.get("text_color"),
            })
        for i, text in enumerate(analysis.get("floating_texts", [])):
            nodes.append({
                "id": f"text{i}",
                "label": text.get("text", ""),
                "x": (float(text["x"]) + float(text["width"]) / 2) * pw,
                "y": (float(text["y"]) + float(text["height"]) / 2) * ph,
                "w": float(text["width"]) * pw,
                "h": float(text["height"]) * ph,
                "shape": "textbox",
                "text_color": text.get("color"),
            })
        edges = []
        for c in analysis.get("connections", []):
            edges.append({
                "source": str(c["from_shape_id"]),
                "target": str(c["to_shape_id"]),
                "label": c.get("label", ""),
                "points": [[float(c["start_x"]) * pw, float(c["start_y"]) * ph],
                           [float(c["end_x"]) * pw, float(c["end_y"]) * ph]],
                "dashed": c.get("line_style") in ("dashed", "dotted"),
                "color": c.get("line_color"),
                "width": c.get("line_width"),
            })
        return {"width": pw, "height": ph, "nodes": nodes, "edges": edges}

    # ------------------------------------------------------------ render

    def _render(self, job: Job):
        with self.render_lock:
            self._render_locked(job)

    def _render_locked(self, job: Job):
        out = job.dir / f"{job.title or 'diagram'}.vsdx"
        json_path = job.dir / "data.json"
        json_path.write_text(json.dumps(job.data, ensure_ascii=False, indent=2), encoding="utf-8")

        if not visio_available():
            job.warning = "当前环境没有 Microsoft Visio：布局与预览已生成，导出 .vsdx 需在 Windows + Visio 上运行。"
            job.downloadable = False
            return

        if job.mode == "image":
            import render_image
            render_image.run(str(json_path), str(out), dry_run=False)
        elif job.diagram_type == "flowchart" and job.layout_data is not None:
            import generate
            _, _, renderer_mod = generate.BUILDERS["flowchart"]
            renderer = importlib.import_module(renderer_mod)
            renderer.render_to_visio(job.layout_data, str(out), visible=False)
        else:
            import generate
            generate.run(job.diagram_type, str(json_path), str(out), dry_run=False, visible=False)

        job.file_path = out
        job.downloadable = True
