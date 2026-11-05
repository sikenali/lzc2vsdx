"""C2VSDX Web 服务：完整继承 OpenVS Skills 后端，前端由 Vue 提供。"""
from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_file, send_from_directory, stream_with_context

from jobs import JobManager, validate_payload, visio_available
import parser as parser_module
from parser import ParseError, count_stats, parse_image, parse_text

BASE_DIR = Path(__file__).parent
DIST_DIR = Path(os.environ.get("C2VSDX_DIST", BASE_DIR.parent / "frontend" / "dist"))
manager = JobManager()


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

    @app.errorhandler(413)
    def too_large(_):
        return jsonify({"error": "图片超过 10MB"}), 413

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "visio": visio_available(),
            "graphviz": shutil.which("dot") is not None,
            "llm": bool(parser_module.llm_config()),
            "vision": bool(parser_module.vision_config()),
        })

    @app.post("/api/text/analyze")
    def analyze_text():
        body = request.get_json(silent=True) or {}
        diagram_type = body.get("diagram_type", "flowchart")
        text = body.get("text", "")
        model = body.get("model")
        try:
            result = parse_text(diagram_type, text, model)
            validate_payload("text", diagram_type, result["data"])
        except (ParseError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 422
        return jsonify(result)

    @app.post("/api/image/analyze")
    def analyze_image():
        upload = request.files.get("image")
        if not upload or not upload.filename:
            return jsonify({"error": "请选择图片文件"}), 422
        raw = upload.read()
        demo = request.args.get("demo") in ("1", "true")
        try:
            result = parse_image(raw, upload.filename, demo=demo)
            from render_image import validate as validate_image
            validate_image(result["analysis"])
        except ParseError as exc:
            return jsonify({"error": str(exc)}), 422
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 422
        except Exception as exc:
            return jsonify({"error": f"图片解析失败: {exc}"}), 502
        return jsonify(result)

    @app.post("/api/jobs")
    def create_job():
        body = request.get_json(silent=True) or {}
        mode = body.get("mode")
        diagram_type = body.get("diagram_type")
        data = body.get("data")
        title = body.get("title") or "生成结果"
        stats = body.get("stats")
        if mode not in ("text", "image"):
            return jsonify({"error": "mode 必须是 text 或 image"}), 422
        if mode == "text" and diagram_type not in (
            "flowchart", "sequence", "composition", "component", "architecture", "swimlane"
        ):
            return jsonify({"error": "未知图表类型"}), 422
        if not isinstance(data, dict):
            return jsonify({"error": "缺少 data"}), 422
        try:
            validate_payload(mode, diagram_type or "flowchart", data)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 422
        # 统计以服务端数据为准，避免前端缓存或篡改造成不一致
        stats = count_stats(diagram_type, data) if mode == "text" else {
            "nodes": len(data.get("shapes", [])) + len(data.get("floating_texts", [])),
            "edges": len(data.get("connections", [])),
            "labels": (
                sum(1 for s in data.get("shapes", []) if s.get("text"))
                + sum(1 for c in data.get("connections", []) if c.get("label"))
                + sum(1 for t in data.get("floating_texts", []) if t.get("text"))
            ),
        }
        job = manager.create(mode, diagram_type or "flowchart", data, title, stats)
        return jsonify(job.snapshot()), 202

    @app.get("/api/jobs/<job_id>")
    def get_job(job_id: str):
        job = manager.get(job_id)
        if not job:
            return jsonify({"error": "任务不存在"}), 404
        return jsonify(job.snapshot())

    @app.get("/api/jobs/<job_id>/preview")
    def get_preview(job_id: str):
        job = manager.get(job_id)
        if not job:
            return jsonify({"error": "任务不存在"}), 404
        if not job.preview:
            return jsonify({"error": "预览尚未生成"}), 409
        return jsonify(job.preview)

    @app.get("/api/jobs/<job_id>/events")
    def job_events(job_id: str):
        job = manager.get(job_id)
        if not job:
            return jsonify({"error": "任务不存在"}), 404

        def stream():
            last = -1
            deadline = time.time() + 1800
            while time.time() < deadline:
                if job.version != last:
                    last = job.version
                    yield f"data: {json.dumps(job.snapshot(), ensure_ascii=False)}\n\n"
                if job.status in ("done", "error", "cancelled"):
                    break
                time.sleep(0.15)
            yield "event: end\ndata: {}\n\n"

        return Response(stream_with_context(stream()), mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.post("/api/jobs/<job_id>/cancel")
    def cancel_job(job_id: str):
        if not manager.cancel(job_id):
            return jsonify({"error": "任务不存在"}), 404
        return jsonify(manager.get(job_id).snapshot())

    @app.get("/api/jobs/<job_id>/download")
    def download(job_id: str):
        job = manager.get(job_id)
        if not job:
            return jsonify({"error": "任务不存在"}), 404
        if not job.downloadable or not job.file_path or not Path(job.file_path).exists():
            return jsonify({"error": job.warning or "文件尚未生成"}), 409
        safe = "".join(c for c in job.title if c not in '\\/:*?"<>|').strip() or "diagram"
        return send_file(job.file_path, as_attachment=True, download_name=f"{safe}.vsdx")

    @app.post("/api/jobs/<job_id>/tweak")
    def tweak(job_id: str):
        job = manager.get(job_id)
        if not job:
            return jsonify({"error": "任务不存在"}), 404
        body = request.get_json(silent=True) or {}
        data = body.get("data")
        if job.status == "running":
            return jsonify({"error": "任务仍在运行，无法微调"}), 409
        if not isinstance(data, dict):
            return jsonify({"error": "缺少 data"}), 422
        try:
            validate_payload(job.mode, job.diagram_type, data)
            stats = count_stats(job.diagram_type, data) if job.mode == "text" else {
                "nodes": len(data.get("shapes", [])) + len(data.get("floating_texts", [])),
                "edges": len(data.get("connections", [])),
                "labels": (
                    sum(1 for s in data.get("shapes", []) if s.get("text"))
                    + sum(1 for c in data.get("connections", []) if c.get("label"))
                    + sum(1 for t in data.get("floating_texts", []) if t.get("text"))
                ),
            }
        except Exception as exc:
            return jsonify({"error": str(exc)}), 422
        manager.restart(job, data, body.get("title") or job.title, stats)
        return jsonify(job.snapshot()), 202

    # ---- 前端静态资源（生产构建产物） ----
    @app.get("/")
    def index():
        if (DIST_DIR / "index.html").exists():
            return send_from_directory(DIST_DIR, "index.html")
        return jsonify({"message": "C2VSDX API 运行中；前端开发请访问 Vite 端口 5173。"})

    @app.get("/<path:path>")
    def static_files(path: str):
        if path.startswith("api/"):
            return jsonify({"error": "not found"}), 404
        target = DIST_DIR / path
        if target.exists() and target.is_file():
            return send_from_directory(DIST_DIR, path)
        if (DIST_DIR / "index.html").exists():
            return send_from_directory(DIST_DIR, "index.html")
        return jsonify({"error": "not found"}), 404

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
