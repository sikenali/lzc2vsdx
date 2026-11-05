import io
import json
import os
import time

os.environ.setdefault("OPENVS_PROGRESS_DELAY", "0")

import pytest

from app import create_app
from parser import parse_text


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def wait_done(client, job_id, timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        body = client.get(f"/api/jobs/{job_id}").get_json()
        if body["status"] in ("done", "error", "cancelled"):
            return body
        time.sleep(0.05)
    raise AssertionError("job did not finish")


def test_health(client):
    body = client.get("/api/health").get_json()
    assert body["status"] == "ok"
    assert isinstance(body["visio"], bool)


def test_empty_text_returns_422(client):
    resp = client.post("/api/text/analyze", json={"diagram_type": "flowchart", "text": ""})
    assert resp.status_code == 422
    assert "空" in resp.get_json()["error"]


def test_text_analyze(client):
    resp = client.post("/api/text/analyze", json={
        "diagram_type": "flowchart",
        "text": "用户登录流程\n用户输入手机号。\n系统校验验证码。\n登录成功。",
    })
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["title"] == "用户登录流程"
    assert body["stats"]["nodes"] >= 4


def test_text_analyze_accepts_model(client):
    for model in ("c2vsdx-graph-v1", "c2vsdx-graph-v2"):
        resp = client.post("/api/text/analyze", json={
            "diagram_type": "flowchart",
            "text": "流程\n用户下单。\n系统校验。",
            "model": model,
        })
        assert resp.status_code == 200
        assert resp.get_json()["data"]["nodes"]


def test_create_job_recomputes_stats(client):
    parsed = parse_text("flowchart", "用户登录流程\n用户输入手机号。\n系统校验验证码。")
    resp = client.post("/api/jobs", json={
        "mode": "text", "diagram_type": "flowchart", "data": parsed["data"],
        "title": parsed["title"], "stats": {"nodes": 999, "edges": 999, "labels": 999},
    })
    job = wait_done(client, resp.get_json()["id"])
    assert job["stats"]["nodes"] == len(parsed["data"]["nodes"])
    assert job["stats"]["nodes"] != 999


def test_tweak_running_job_returns_409(client):
    os.environ["OPENVS_PROGRESS_DELAY"] = "1"
    try:
        parsed = parse_text("flowchart", "流程\n用户下单。\n系统校验。")
        job_id = client.post("/api/jobs", json={
            "mode": "text", "diagram_type": "flowchart", "data": parsed["data"],
            "title": parsed["title"], "stats": parsed["stats"],
        }).get_json()["id"]
        resp = client.post(f"/api/jobs/{job_id}/tweak", json={"data": parsed["data"]})
        assert resp.status_code == 409
        wait_done(client, job_id)
    finally:
        os.environ["OPENVS_PROGRESS_DELAY"] = "0"


def test_create_job_and_preview(client):
    parsed = parse_text("flowchart", "用户登录流程\n用户输入手机号。\n系统校验验证码。\n登录成功。")
    resp = client.post("/api/jobs", json={
        "mode": "text", "diagram_type": "flowchart", "data": parsed["data"],
        "title": parsed["title"], "stats": parsed["stats"],
    })
    assert resp.status_code == 202
    job_id = resp.get_json()["id"]
    done = wait_done(client, job_id)
    assert done["status"] == "done"
    assert done["progress"] == 100
    assert done["preview"]["nodes"]
    assert done["preview"]["edges"]


def test_cancel_job(client):
    os.environ["OPENVS_PROGRESS_DELAY"] = "1"
    try:
        parsed = parse_text("flowchart", "用户登录流程\n用户输入手机号。\n系统校验验证码。")
        job_id = client.post("/api/jobs", json={
            "mode": "text", "diagram_type": "flowchart", "data": parsed["data"],
            "title": parsed["title"], "stats": parsed["stats"],
        }).get_json()["id"]
        time.sleep(0.05)
        client.post(f"/api/jobs/{job_id}/cancel")
        done = wait_done(client, job_id)
        assert done["status"] == "cancelled"
    finally:
        os.environ["OPENVS_PROGRESS_DELAY"] = "0"


def test_job_snapshot_includes_data_and_tweak(client):
    parsed = parse_text("flowchart", "用户登录流程\n用户输入手机号。\n系统校验验证码。\n登录成功。")
    job_id = client.post("/api/jobs", json={
        "mode": "text", "diagram_type": "flowchart", "data": parsed["data"],
        "title": parsed["title"], "stats": parsed["stats"],
    }).get_json()["id"]
    wait_done(client, job_id)
    body = client.get(f"/api/jobs/{job_id}").get_json()
    assert body["data"]["nodes"]
    tweaked = dict(body["data"])
    tweaked["nodes"] = [dict(n, label="微调节点") for n in body["data"]["nodes"]]
    resp = client.post(f"/api/jobs/{job_id}/tweak", json={"data": tweaked})
    assert resp.status_code == 202
    done = wait_done(client, job_id)
    assert done["status"] == "done"
    assert done["data"]["nodes"][0]["label"] == "微调节点"


def test_image_analyze_demo(client):
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + (1440).to_bytes(4, "big") + (900).to_bytes(4, "big") + b"\x00" * 8
    resp = client.post("/api/image/analyze?demo=1", data={"image": (io.BytesIO(png), "shot.png")},
                       content_type="multipart/form-data")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["analysis"]["demo"] is True
    assert body["stats"]["nodes"] == 6


def test_image_without_vision_or_demo_returns_422(client):
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
    resp = client.post("/api/image/analyze", data={"image": (io.BytesIO(png), "shot.png")},
                       content_type="multipart/form-data")
    assert resp.status_code == 422
    assert "视觉模型" in resp.get_json()["error"]


def test_blank_image_returns_422(client):
    resp = client.post("/api/image/analyze", data={"image": (io.BytesIO(b""), "shot.png")},
                       content_type="multipart/form-data")
    assert resp.status_code == 422
    assert "空" in resp.get_json()["error"]


def test_image_job_preview(client):
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + (1440).to_bytes(4, "big") + (900).to_bytes(4, "big") + b"\x00" * 8
    parsed = client.post("/api/image/analyze?demo=1", data={"image": (io.BytesIO(png), "shot.png")},
                         content_type="multipart/form-data").get_json()
    job_id = client.post("/api/jobs", json={
        "mode": "image", "diagram_type": "flowchart", "data": parsed["analysis"],
        "title": parsed["title"], "stats": parsed["stats"],
    }).get_json()["id"]
    done = wait_done(client, job_id)
    assert done["status"] == "done"
    assert len(done["preview"]["nodes"]) == 6
    assert all("points" in e for e in done["preview"]["edges"])


def test_invalid_tweak_returns_422(client):
    parsed = parse_text("flowchart", "用户登录流程\n用户输入手机号。\n系统校验验证码。")
    job_id = client.post("/api/jobs", json={
        "mode": "text", "diagram_type": "flowchart", "data": parsed["data"],
        "title": parsed["title"], "stats": parsed["stats"],
    }).get_json()["id"]
    wait_done(client, job_id)
    resp = client.post(f"/api/jobs/{job_id}/tweak", json={
        "data": {
            "nodes": [{"id": "x", "label": "x", "shape": "rectangle"}],
            "edges": [{"source": "x", "target": "missing"}],
        }
    })
    assert resp.status_code == 422


def test_download_returns_file_when_available(client, tmp_path):
    from app import manager

    parsed = parse_text("flowchart", "用户登录流程\n用户输入手机号。\n系统校验验证码。")
    job_id = client.post("/api/jobs", json={
        "mode": "text", "diagram_type": "flowchart", "data": parsed["data"],
        "title": parsed["title"], "stats": parsed["stats"],
    }).get_json()["id"]
    wait_done(client, job_id)
    job = manager.get(job_id)
    fake = tmp_path / "fake.vsdx"
    fake.write_bytes(b"PK\x03\x04fake")
    job.file_path = fake
    job.downloadable = True
    resp = client.get(f"/api/jobs/{job_id}/download")
    assert resp.status_code == 200
    assert "vsdx" in resp.headers["Content-Disposition"]
    assert resp.data.startswith(b"PK")


def test_no_visio_download_is_409(client):
    parsed = parse_text("flowchart", "用户登录流程\n用户输入手机号。\n系统校验验证码。")
    job_id = client.post("/api/jobs", json={
        "mode": "text", "diagram_type": "flowchart", "data": parsed["data"],
        "title": parsed["title"], "stats": parsed["stats"],
    }).get_json()["id"]
    done = wait_done(client, job_id)
    if done["downloadable"]:
        pytest.skip("running on a Windows + Visio host")
    assert done["warning"]
    resp = client.get(f"/api/jobs/{job_id}/download")
    assert resp.status_code == 409
