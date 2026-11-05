from parser import ParseError, count_stats, parse_text

SAMPLE = """用户登录流程
用户打开 App 后进入登录页，页面展示手机号输入框、验证码输入框以及「登录」按钮。
用户输入手机号后点击「获取验证码」，前端校验手机号格式。
用户在 60 秒内填写验证码并点击「登录」，前端完成非空校验后调用登录接口。
登录接口依次校验：若验证码错误，返回剩余重试次数。
Token 写入本地安全缓存后，系统并行请求用户信息接口与权限接口。
"""


def test_parse_flowchart_has_start_end_and_edges():
    result = parse_text("flowchart", SAMPLE)
    nodes = result["data"]["nodes"]
    edges = result["data"]["edges"]
    assert nodes[0]["shape"] == "stadium"
    assert nodes[-1]["shape"] == "stadium"
    assert any(n["shape"] == "diamond" for n in nodes)
    assert len(edges) >= len(nodes) - 1
    assert all(e["source"] in {n["id"] for n in nodes} for e in edges)
    assert all(e["target"] in {n["id"] for n in nodes} for e in edges)


def test_parse_flowchart_title_from_first_line():
    assert parse_text("flowchart", SAMPLE)["title"] == "用户登录流程"


def test_empty_text_raises():
    try:
        parse_text("flowchart", "   ")
    except ParseError as exc:
        assert "空" in str(exc)
    else:
        raise AssertionError("expected ParseError")


def test_long_text_is_capped_at_twenty_nodes():
    text = "用户流程\n" + "\n".join(f"步骤{i}执行操作。" for i in range(500))
    result = parse_text("flowchart", text)
    assert len(result["data"]["nodes"]) <= 20


def test_all_six_types_are_valid():
    for diagram_type in ("flowchart", "sequence", "composition", "component", "architecture", "swimlane"):
        result = parse_text(diagram_type, SAMPLE)
        stats = count_stats(diagram_type, result["data"])
        assert stats["nodes"] > 0
        assert stats["edges"] >= 0
