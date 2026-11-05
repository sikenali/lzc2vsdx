"""文本 / 图片 → OpenVS 结构化 JSON。

原项目把这一步交给调用方 Agent；Web 版内置一个规则解析器作为默认实现，
并在配置了 OpenAI 兼容接口时优先使用 LLM。输出的 JSON 严格沿用
backend/c2vsdx/references 中的 schema。
"""
from __future__ import annotations

import base64
import json
import os
import re
import struct
import urllib.request
from pathlib import Path

REF_DIR = Path(__file__).parent / "c2vsdx" / "references"
PARSE_PROMPTS = REF_DIR / "parse-prompts"

TITLE_MAX = 30
LABEL_MAX = 20

# 句子切分：以段落/句号为主，分号不拆（保持一个流程阶段为一个节点）
SENTENCE_SPLIT = re.compile(r"[。\n]+")
CLAUSE_SPLIT = re.compile(r"[，：、,]")
ROLE_WORDS = ("用户", "前端", "后端", "服务端", "客户端", "系统", "管理员", "运营")
CONDITION_RE = re.compile(r"(校验|判断|是否|^如果|^若|^检查)")
FAILURE_WORDS = ("错误", "失败", "未注册", "不存在", "锁定", "超时", "异常")


class ParseError(ValueError):
    pass


# ---------------------------------------------------------------- 文本解析

def _clean(text: str) -> str:
    return re.sub(r"[ \t\u3000]+", " ", text.replace("\r\n", "\n")).strip()


def _split_title(text: str) -> tuple[str, str]:
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if not lines:
        raise ParseError("文本为空")
    first = lines[0]
    if len(first) <= TITLE_MAX and not re.search(r"[。！？；，,:：]", first) and len(lines) > 1:
        return first, "\n".join(lines[1:])
    return "", text


def _sentences(body: str) -> list[str]:
    parts = [p.strip() for p in SENTENCE_SPLIT.split(body)]
    return [p for p in parts if len(p) >= 2]


def _label(sentence: str) -> str:
    s = sentence.strip()
    for role in ROLE_WORDS:
        if s.startswith(role):
            s = s[len(role):].lstrip("在的")
            break
    s = re.sub(r"^(首先|然后|接着|随后|最后|之后|再|并|会|将|需要|进行|在|于)", "", s)
    s = re.sub(r"点击「([^」]+)」", r"\1", s)
    s = s.replace("「", "").replace("」", "")
    if len(s) > LABEL_MAX:
        first_clause = CLAUSE_SPLIT.split(s)[0]
        s = first_clause if len(first_clause) >= 4 else s[:LABEL_MAX]
    s = re.sub(r"(后|之后|时|完成后)$", "", s)
    return s[:LABEL_MAX].strip("，。；： ")


def _module_label(sentence: str) -> str:
    """模块/组件/分层名称：保留“用户系统”这类主体词，不做角色前缀剥离。"""
    s = re.sub(r"^(首先|然后|接着|随后|最后|之后|再|并|会|将|需要|进行|在|于)", "", sentence.strip())
    if len(s) > LABEL_MAX:
        s = CLAUSE_SPLIT.split(s)[0]
    return s[:LABEL_MAX].strip("，。；： ")


def _is_condition(sentence: str) -> bool:
    return bool(CONDITION_RE.search(sentence))


def _parse_flowchart(text: str) -> dict:
    title, body = _split_title(text)
    sentences = _sentences(body)
    if not sentences:
        raise ParseError("文本中没有可解析的流程步骤")
    # 与解析规范一致：单图节点总数不超过 20（首尾节点各占 1 个）
    sentences = sentences[:18]

    nodes = [{"id": "start", "label": "开始", "shape": "stadium"}]
    edges: list[dict] = []
    prev = "start"
    sentence_by_id = {}

    for i, sentence in enumerate(sentences, start=1):
        node_id = f"n{i}"
        label = _label(sentence) or f"步骤{i}"
        shape = "diamond" if _is_condition(label) else "rectangle"
        nodes.append({"id": node_id, "label": label, "shape": shape})
        edges.append({"source": prev, "target": node_id, "label": ""})
        sentence_by_id[node_id] = sentence
        prev = node_id

    # 判断节点：主链标“成功”；句子里提到失败/错误时补一个“提示错误”分支
    branch_index = 0
    for edge in list(edges):
        source_node = next((n for n in nodes if n["id"] == edge["source"]), None)
        if source_node and source_node["shape"] == "diamond" and edge["label"] == "":
            edge["label"] = "成功"
            sentence = sentence_by_id.get(source_node["id"], "")
            if any(w in sentence for w in FAILURE_WORDS):
                branch_index += 1
                failure_id = f"fail{branch_index}"
                nodes.append({"id": failure_id, "label": "提示错误", "shape": "rectangle"})
                edges.append({"source": source_node["id"], "target": failure_id, "label": "失败"})

    nodes.append({"id": "end", "label": "结束", "shape": "stadium"})
    edges.append({"source": prev, "target": "end", "label": ""})

    return {
        "title": title or "流程图",
        "data": {"nodes": nodes, "edges": edges},
    }


def _parse_sequence(text: str) -> dict:
    title, body = _split_title(text)
    sentences = _sentences(body)
    if not sentences:
        raise ParseError("文本中没有可解析的交互步骤")

    roles = [r for r in ROLE_WORDS if any(r in s for s in sentences)]
    if len(roles) < 2:
        roles = ["用户", "系统"]
    participants = [{"id": f"p{i}", "label": role} for i, role in enumerate(roles)]

    messages = []
    for i, sentence in enumerate(sentences, start=1):
        sender = participants[(i - 1) % len(participants)]
        receiver = participants[i % len(participants)]
        messages.append({
            "id": f"m{i}",
            "from_id": sender["id"],
            "to_id": receiver["id"],
            "label": _label(sentence) or f"消息{i}",
            "msg_type": "sync",
        })
    return {"title": title or "时序图", "data": {"participants": participants, "messages": messages, "fragments": []}}


def _parse_composition(text: str) -> dict:
    title, body = _split_title(text)
    lines = [ln for ln in body.split("\n") if ln.strip()]
    if not lines:
        raise ParseError("文本中没有可解析的模块")

    nodes = [{"id": "root", "label": title or "系统", "parent_id": None, "level": 0}]
    stack: list[tuple[int, str]] = [(0, "root")]
    for i, raw in enumerate(lines, start=1):
        indent = len(raw) - len(raw.lstrip(" \t"))
        numbered = re.match(r"^\s*(\d+(?:\.\d+)*)[.、)．]?\s*", raw)
        if numbered:
            level = max(1, len(numbered.group(1).split(".")))
            label = raw[numbered.end():].strip()
        elif indent:
            level = max(1, indent // 2 + 1)
            label = raw.strip()
        else:
            level = 1
            label = raw.strip()
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1] if stack else "root"
        node_id = f"n{i}"
        nodes.append({
            "id": node_id,
            "label": _module_label(label) or f"模块{i}",
            "parent_id": parent,
            "level": level,
        })
        stack.append((level, node_id))
    return {"title": title or "组成图", "data": {"nodes": nodes}}


def _parse_component(text: str) -> dict:
    title, body = _split_title(text)
    sentences = _sentences(body)
    if not sentences:
        raise ParseError("文本中没有可解析的组件")

    components = []
    for i, sentence in enumerate(sentences, start=1):
        components.append({"id": f"c{i}", "label": _module_label(sentence) or f"组件{i}"})

    interfaces = []
    dependencies = []
    for i, comp in enumerate(components, start=1):
        interfaces.append({
            "id": f"i{i}",
            "label": f"{comp['label']}接口",
            "iface_type": "provided",
            "component_id": comp["id"],
        })
        if i > 1:
            dependencies.append({
                "id": f"d{i}",
                "from_id": components[i - 2]["id"],
                "to_id": comp["id"],
                "label": "",
            })
    # 每条依赖在调用方挂一个 required 接口，体现“接口提供与依赖关系”
    for i, dep in enumerate(dependencies, start=1):
        interfaces.append({
            "id": f"req{i}",
            "label": f"{dep['label'] or '依赖'}接口",
            "iface_type": "required",
            "component_id": dep["from_id"],
        })
    return {
        "title": title or "关系图",
        "data": {"components": components, "interfaces": interfaces, "dependencies": dependencies},
    }


def _parse_architecture(text: str) -> dict:
    title, body = _split_title(text)
    lines = [ln.strip() for ln in body.split("\n") if ln.strip()]
    sentences = lines or _sentences(body)
    if not sentences:
        raise ParseError("文本中没有可解析的架构信息")

    layer_names = [ln for ln in lines if len(ln) <= 12 and ln.endswith("层")]
    if len(layer_names) >= 2:
        layers = [{"id": f"l{i}", "label": name, "level": i} for i, name in enumerate(layer_names)]
        components = []
        current = 0
        for line in lines:
            if line in layer_names:
                current = layer_names.index(line)
                continue
            components.append({
                "id": f"c{len(components) + 1}",
                "label": _module_label(line) or f"模块{len(components) + 1}",
                "layer_id": layers[current]["id"],
            })
    else:
        layers = [
            {"id": "l1", "label": "接入层", "level": 0},
            {"id": "l2", "label": "业务层", "level": 1},
            {"id": "l3", "label": "数据层", "level": 2},
        ]
        components = []
        for i, sentence in enumerate(sentences, start=1):
            layer = layers[(i - 1) % len(layers)]
            components.append({
                "id": f"c{i}",
                "label": _module_label(sentence) or f"模块{i}",
                "layer_id": layer["id"],
            })

    connections = []
    for i in range(len(components) - 1):
        connections.append({
            "from_id": components[i]["id"],
            "to_id": components[i + 1]["id"],
            "label": "",
        })
    return {"title": title or "架构图", "data": {"layers": layers, "components": components, "connections": connections}}


def _parse_swimlane(text: str) -> dict:
    title, body = _split_title(text)
    sentences = _sentences(body)
    if not sentences:
        raise ParseError("文本中没有可解析的泳道流程")

    role_candidates = ["用户", "前端", "服务端", "数据库", "运营", "管理员", "客户"]
    found = [r for r in role_candidates if any(r in s for s in sentences)]
    if len(found) >= 2:
        lanes = [{"id": f"lane{i}", "label": r} for i, r in enumerate(found, start=1)]
    else:
        lanes = [
            {"id": "lane1", "label": "用户"},
            {"id": "lane2", "label": "前端"},
            {"id": "lane3", "label": "服务端"},
        ]

    nodes = []
    for i, sentence in enumerate(sentences, start=1):
        lane = next((l for l in lanes if l["label"] in sentence), lanes[(i - 1) % len(lanes)])
        label = _label(sentence) or f"步骤{i}"
        nodes.append({
            "id": f"n{i}",
            "label": label,
            "lane_id": lane["id"],
            "shape": "diamond" if _is_condition(label) else "rectangle",
        })
    edges = [
        {"source": nodes[i]["id"], "target": nodes[i + 1]["id"], "label": ""}
        for i in range(len(nodes) - 1)
    ]
    return {"title": title or "泳道图", "data": {"lanes": lanes, "nodes": nodes, "edges": edges}}


BUILDERS = {
    "flowchart": _parse_flowchart,
    "sequence": _parse_sequence,
    "composition": _parse_composition,
    "component": _parse_component,
    "architecture": _parse_architecture,
    "swimlane": _parse_swimlane,
}


def count_stats(diagram_type: str, data: dict) -> dict:
    def labels(items, key="label"):
        return sum(1 for item in items if item.get(key))

    if diagram_type == "flowchart":
        nodes, edges = data.get("nodes", []), data.get("edges", [])
        return {"nodes": len(nodes), "edges": len(edges), "labels": labels(nodes) + labels(edges)}
    if diagram_type == "sequence":
        msgs = data.get("messages", [])
        return {"nodes": len(data.get("participants", [])), "edges": len(msgs), "labels": labels(msgs)}
    if diagram_type == "composition":
        nodes = data.get("nodes", [])
        return {"nodes": len(nodes), "edges": sum(1 for n in nodes if n.get("parent_id")), "labels": labels(nodes)}
    if diagram_type == "component":
        comps = data.get("components", [])
        return {
            "nodes": len(comps),
            "edges": len(data.get("dependencies", [])),
            "labels": labels(comps) + labels(data.get("interfaces", [])),
        }
    if diagram_type == "architecture":
        comps = data.get("components", [])
        return {
            "nodes": len(data.get("layers", [])) + len(comps),
            "edges": len(data.get("connections", [])),
            "labels": labels(comps),
        }
    if diagram_type == "swimlane":
        nodes, edges = data.get("nodes", []), data.get("edges", [])
        return {"nodes": len(nodes), "edges": len(edges), "labels": labels(nodes) + labels(edges)}
    raise ParseError(f"未知图表类型: {diagram_type}")


# ---------------------------------------------------------------- LLM 适配

def llm_config() -> dict | None:
    base = os.environ.get("OPENVS_LLM_BASE_URL", "").rstrip("/")
    key = os.environ.get("OPENVS_LLM_API_KEY", "")
    model = os.environ.get("OPENVS_LLM_MODEL", "")
    if base and key and model:
        return {"base": base, "key": key, "model": model}
    return None


def _chat(config: dict, messages: list[dict], timeout: int = 90) -> str:
    payload = json.dumps({"model": config["model"], "messages": messages, "temperature": 0.2}).encode()
    req = urllib.request.Request(
        f"{config['base']}/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {config['key']}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode())
    return body["choices"][0]["message"]["content"]


def llm_parse_text(diagram_type: str, text: str) -> dict:
    config = llm_config()
    prompt_file = PARSE_PROMPTS / f"{diagram_type}.txt"
    if not config or not prompt_file.exists():
        raise ParseError("LLM 未配置")
    content = _chat(config, [
        {"role": "system", "content": prompt_file.read_text(encoding="utf-8")},
        {"role": "user", "content": text},
    ])
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    return json.loads(content)


def parse_text(diagram_type: str, text: str, model: str | None = None) -> dict:
    text = _clean(text)
    if not text:
        raise ParseError("文本为空")
    if diagram_type not in BUILDERS:
        raise ParseError(f"未知图表类型: {diagram_type}")

    # c2vsdx-graph v1 固定走本地规则；v2 在配置 LLM 时优先走 LLM
    use_llm = bool(llm_config()) and model != "c2vsdx-graph-v1"
    if use_llm:
        try:
            data = llm_parse_text(diagram_type, text)
            title, body = _split_title(text)
            return {"title": title or "生成结果", "data": data, "stats": count_stats(diagram_type, data)}
        except Exception as exc:  # LLM 失败时回退规则解析
            print(f"[parser] LLM 解析失败，回退规则解析: {exc}")

    built = BUILDERS[diagram_type](text)
    return {**built, "stats": count_stats(diagram_type, built["data"])}


# ---------------------------------------------------------------- 图片解析

def _image_aspect(raw: bytes) -> float:
    try:
        if raw[:8] == b"\x89PNG\r\n\x1a\n":
            width, height = struct.unpack(">II", raw[16:24])
            return width / height if height else 1.78
        if raw[:2] == b"\xff\xd8":
            i = 2
            while i < len(raw) - 9:
                if raw[i] != 0xFF:
                    i += 1
                    continue
                marker = raw[i + 1]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3):
                    h, w = struct.unpack(">HH", raw[i + 5:i + 9])
                    return w / h if h else 1.78
                length = struct.unpack(">H", raw[i + 2:i + 4])[0]
                i += 2 + length
        if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
            return 1.78
    except Exception:
        pass
    return 1.78


def _demo_analysis(aspect: float) -> dict:
    """未配置视觉模型时的演示数据（明确标记 demo，不冒充真实识别）。"""
    def box(i, x, y, w, h, text, kind="rectangle"):
        return {"id": i, "type": kind, "x": x, "y": y, "width": w, "height": h, "text": text}

    shapes = [
        box(1, 0.08, 0.08, 0.18, 0.10, "开始", "rounded_rectangle"),
        box(2, 0.40, 0.08, 0.20, 0.10, "输入手机号"),
        box(3, 0.72, 0.08, 0.20, 0.10, "获取验证码"),
        box(4, 0.40, 0.38, 0.20, 0.14, "校验验证码", "diamond"),
        box(5, 0.08, 0.68, 0.18, 0.10, "提示错误"),
        box(6, 0.72, 0.68, 0.20, 0.10, "登录成功"),
    ]
    connections = [
        {"from_shape_id": 1, "to_shape_id": 2, "type": "straight", "label": "", "has_arrow": True,
         "start_x": 0.26, "start_y": 0.13, "end_x": 0.40, "end_y": 0.13},
        {"from_shape_id": 2, "to_shape_id": 3, "type": "straight", "label": "", "has_arrow": True,
         "start_x": 0.60, "start_y": 0.13, "end_x": 0.72, "end_y": 0.13},
        {"from_shape_id": 3, "to_shape_id": 4, "type": "elbow", "label": "", "has_arrow": True,
         "start_x": 0.82, "start_y": 0.18, "end_x": 0.50, "end_y": 0.38},
        {"from_shape_id": 4, "to_shape_id": 5, "type": "straight", "label": "失败", "has_arrow": True,
         "start_x": 0.40, "start_y": 0.45, "end_x": 0.26, "end_y": 0.68},
        {"from_shape_id": 4, "to_shape_id": 6, "type": "straight", "label": "成功", "has_arrow": True,
         "start_x": 0.60, "start_y": 0.45, "end_x": 0.72, "end_y": 0.68},
    ]
    return {
        "image_aspect": round(aspect, 2),
        "diagram_type": "flowchart",
        "title": "图片识别示例",
        "demo": True,
        "shapes": shapes,
        "connections": connections,
        "floating_texts": [],
    }


def image_stats(analysis: dict) -> dict:
    shapes = analysis.get("shapes", [])
    connections = analysis.get("connections", [])
    floating = analysis.get("floating_texts", [])
    return {
        "nodes": len(shapes) + len(floating),
        "edges": len(connections),
        "labels": (
            sum(1 for s in shapes if s.get("text"))
            + sum(1 for c in connections if c.get("label"))
            + sum(1 for t in floating if t.get("text"))
        ),
    }


def vision_config() -> dict | None:
    base = os.environ.get("OPENVS_VISION_BASE_URL", os.environ.get("OPENVS_LLM_BASE_URL", "")).rstrip("/")
    key = os.environ.get("OPENVS_VISION_API_KEY", os.environ.get("OPENVS_LLM_API_KEY", ""))
    model = os.environ.get("OPENVS_VISION_MODEL", "")
    if base and key and model:
        return {"base": base, "key": key, "model": model}
    return None


def parse_image(raw: bytes, filename: str, demo: bool = False) -> dict:
    if not raw:
        raise ParseError("图片为空")
    if len(raw) > 10 * 1024 * 1024:
        raise ParseError("图片超过 10MB")
    ext = Path(filename or "").suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".svg", ".webp"}:
        raise ParseError("仅支持 PNG/JPG/SVG/WebP")

    aspect = _image_aspect(raw)
    config = vision_config()
    if config:
        schema = (REF_DIR / "image-schema.md").read_text(encoding="utf-8")
        mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".webp": "image/webp", ".svg": "image/svg+xml"}.get(ext, "image/png")
        data_url = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
        content = _chat(config, [
            {"role": "system", "content": f"按以下 schema 分析图片，只输出 JSON：\n{schema}"},
            {"role": "user", "content": [
                {"type": "text", "text": "识别这张图并输出 image-schema JSON"},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]},
        ])
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
        analysis = json.loads(content)
        aspect = analysis.get("image_aspect")
        if not isinstance(aspect, (int, float)) or aspect <= 0:
            analysis["image_aspect"] = round(_image_aspect(raw), 2)
        for text in analysis.get("floating_texts", []):
            for field in ("text", "x", "y", "width", "height"):
                if field not in text:
                    raise ParseError(f"floating_texts 缺少必填字段 '{field}'")
        return {"title": analysis.get("title") or "图片识别结果", "analysis": analysis,
                "stats": image_stats(analysis)}

    if demo:
        analysis = _demo_analysis(aspect)
        return {"title": analysis["title"], "analysis": analysis, "stats": image_stats(analysis)}

    raise ParseError("未配置视觉模型：请设置 OPENVS_VISION_MODEL / OPENVS_VISION_API_KEY / OPENVS_VISION_BASE_URL")
