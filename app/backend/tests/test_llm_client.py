# test_llm_client.py
import llm_client
from llm_client import extract_json

def test_extract_json_strips_fences():
    assert extract_json('```json\n{"a":1}\n```') == {"a": 1}
    assert extract_json('前置文字 {"a": 1} 后置') == {"a": 1}

class FakeResp:
    def __init__(self, text): self._t = text
    def raise_for_status(self): pass
    def json(self): return {"choices":[{"message":{"content": self._t}}]}

def test_analyze_text_builds_openai_compat_request(monkeypatch):
    captured = {}
    def fake_post(url, json=None, headers=None, timeout=None):
        captured.update({"url": url, "json": json})
        return FakeResp('{"nodes":[],"edges":[]}')
    monkeypatch.setattr("llm_client.httpx.post", fake_post)
    cfg = {"provider":"deepseek","base_url":"https://api.deepseek.com/v1","api_key":"k","text_model":"deepseek-chat"}
    out = llm_client.analyze_text("登录流程", "flowchart", cfg, None)
    assert out == {"nodes":[],"edges":[]}
    assert captured["url"].endswith("/chat/completions")
    assert "temperature" in captured["json"]
