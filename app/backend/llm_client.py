"""Multi-provider LLM client: OpenAI-compatible and Anthropic endpoints."""

import json

import httpx

from llm_prompts import text_prompt, image_prompt, auto_type_prompt

# Providers whose OpenAI-compatible API supports response_format=json_object.
_RESPONSE_FORMAT_PROVIDERS = {"deepseek", "qwen", "openai", "ollama"}


def extract_json(text: str) -> dict:
    """Strip ```json fences / prose and return the parsed JSON object."""
    # Drop code fences if present.
    stripped = text.strip()
    if stripped.startswith("```"):
        # Remove opening fence line (```json or ```).
        lines = stripped.split("\n")
        if lines[0].strip().startswith("```"):
            lines = lines[1:]
        while lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    # Find the first balanced {...} region.
    start = stripped.find("{")
    if start == -1:
        raise ValueError(f"No JSON object found in LLM response: {text[:200]!r}")
    depth = 0
    in_str = False
    esc = False
    for i, ch in enumerate(stripped[start:], start):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(stripped[start : i + 1])
    raise ValueError(f"Unbalanced JSON in LLM response: {text[:200]!r}")


def _headers(cfg: dict, provider: str) -> dict:
    headers = {}
    if provider == "claude":
        headers["x-api-key"] = cfg.get("api_key", "")
        headers["anthropic-version"] = "2023-06-01"
    else:
        headers["Authorization"] = f"Bearer {cfg.get('api_key', '')}"
    return headers


def _content_from_response(data: dict, provider: str) -> str:
    if provider == "claude":
        return "".join(
            block.get("text", "") for block in data.get("content", [])
        )
    return data["choices"][0]["message"]["content"]


def _openai_compat(messages: list, cfg: dict, http) -> dict:
    post = http if http is not None else httpx.post
    payload = {
        "model": cfg.get("text_model", cfg.get("model", "")),
        "messages": messages,
        "temperature": 0.1,
    }
    if cfg.get("provider") in _RESPONSE_FORMAT_PROVIDERS:
        payload["response_format"] = {"type": "json_object"}
    resp = post(
        f"{cfg['base_url']}/chat/completions",
        json=payload,
        headers=_headers(cfg, cfg.get("provider", "")),
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def _anthropic(messages: list, cfg: dict, http) -> dict:
    post = http if http is not None else httpx.post
    payload = {
        "model": cfg.get("text_model", cfg.get("model", "")),
        "max_tokens": 8192,
        "temperature": 0.1,
        "system": "",
        "messages": [],
    }
    for m in messages:
        if m["role"] == "system":
            payload["system"] = m["content"]
        else:
            payload["messages"].append(m)
    resp = post(
        f"{cfg['base_url']}/messages",
        json=payload,
        headers=_headers(cfg, "claude"),
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def _post(messages: list, cfg: dict, http, vision: bool = False) -> dict:
    provider = cfg.get("provider", "")
    if provider == "claude":
        return _anthropic(messages, cfg, http)
    return _openai_compat(messages, cfg, http)


def analyze_text(text: str, diagram_type: str, config: dict, http) -> dict:
    """Parse a text description into diagram JSON via the LLM."""
    messages = [
        {"role": "system", "content": text_prompt(diagram_type)},
        {"role": "user", "content": text},
    ]
    data = _post(messages, config, http)
    return extract_json(_content_from_response(data, config.get("provider", "")))


def analyze_image(image_b64: str, mime: str, image_aspect: float, config: dict, http) -> dict:
    """Analyze a diagram image into JSON; injects image_aspect into the result."""
    provider = config.get("provider", "")
    user_content: list = []
    if provider == "claude":
        user_content = [
            {
                "type": "image",
                "source": {"type": "base64", "media_type": mime, "data": image_b64},
            },
            {"type": "text", "text": image_prompt()},
        ]
    else:
        user_content = [
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_b64}"}},
            {"type": "text", "text": image_prompt()},
        ]
    messages = [{"role": "user", "content": user_content}]
    data = _post(messages, config, http, vision=True)
    result = extract_json(_content_from_response(data, provider))
    result["image_aspect"] = image_aspect
    return result


def analyze_auto_type(text: str, config: dict, http) -> str:
    """Choose a diagram_type from a text description; returns the type string."""
    messages = [
        {"role": "system", "content": auto_type_prompt()},
        {"role": "user", "content": text},
    ]
    data = _post(messages, config, http)
    content = _content_from_response(data, config.get("provider", ""))
    obj = extract_json(content)
    return str(obj.get("diagram_type", obj.get("type", "")))
