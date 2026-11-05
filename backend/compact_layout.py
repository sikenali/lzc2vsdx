"""Web 展示层的紧凑流程图布局。

原项目 flowchart 布局依赖 Graphviz dot，输出的是窄而高的竖向链。结果页设计稿
要求紧凑的多行流程图，因此 Web 层在不修改原脚本的前提下，增加一个展示布局：
主链按蛇形排成多行，分支节点单独成行。Visio 渲染复用同一份布局数据。
"""
from __future__ import annotations

import math

CHAR_WIDTH = 0.19
LINE_HEIGHT = 0.30
PAD_X = 0.5
PAD_Y = 0.22


def _estimate(label: str, shape: str) -> tuple[float, float]:
    text_w = max(len(label), 1) * CHAR_WIDTH
    w = text_w + PAD_X
    h = LINE_HEIGHT + PAD_Y
    if shape == "diamond":
        return max(w * 1.45 + 0.4, 1.8), max(h + 0.45, 1.0)
    if shape in ("stadium", "rounded"):
        return max(w, 1.1), max(h, 0.55)
    return max(w, 1.1), max(h, 0.55)


def _main_chain(data) -> list:
    ids = {n.id for n in data.nodes}
    outgoing: dict[str, list] = {n.id: [] for n in data.nodes}
    incoming_count = {n.id: 0 for n in data.nodes}
    for edge in data.edges:
        if edge.source in ids and edge.target in ids:
            outgoing[edge.source].append(edge)
            incoming_count[edge.target] += 1

    start = next((n for n in data.nodes if incoming_count[n.id] == 0), data.nodes[0])
    chain = [start]
    seen = {start.id}
    current = start
    while True:
        options = [e for e in outgoing[current.id] if e.target not in seen]
        if not options:
            break
        preferred = next((e for e in options if e.label not in ("失败", "否", "错误", "异常")), options[0])
        target = data.get_node(preferred.target)
        if not target:
            break
        chain.append(target)
        seen.add(target.id)
        current = target
    return chain


def compute(data):
    for node in data.nodes:
        node.width, node.height = _estimate(node.label, node.shape.value)

    chain = _main_chain(data)
    cols = max(2, min(4, math.ceil(math.sqrt(len(chain)))))
    rows = math.ceil(len(chain) / cols)

    # 每列宽度、每行高度按该行/列最大节点计算，避免重叠
    col_w = [0.0] * cols
    row_h = [0.0] * rows
    slots = []
    for i, node in enumerate(chain):
        row = i // cols
        col = i % cols
        if row % 2 == 1:
            col = cols - 1 - col
        slots.append((node, row, col))
        col_w[col] = max(col_w[col], node.width)
        row_h[row] = max(row_h[row], node.height)

    gap_x, gap_y = 1.0, 0.95
    xs, acc = [], 0.0
    for c in range(cols):
        xs.append(acc + col_w[c] / 2)
        acc += col_w[c] + gap_x
    ys, acc = [], 0.0
    for r in range(rows):
        ys.append(acc + row_h[r] / 2)
        acc += row_h[r] + gap_y

    for node, row, col in slots:
        node.x = xs[col]
        node.y = ys[row]

    # 分支节点：插在父节点下一行，父行以下的链节点整体下移，避免重叠
    chain_ids = {n.id for n in chain}
    row_of = {node.id: row for node, row, _ in slots}
    branches = [n for n in data.nodes if n.id not in chain_ids]
    if branches:
        shifts = [0.0] * rows
        per_parent_offset = {}
        for node in branches:
            parent_edge = next(
                (e for e in data.edges if e.target == node.id and e.source in chain_ids), None
            )
            parent = data.get_node(parent_edge.source) if parent_edge else chain[0]
            parent_row = row_of.get(parent.id, 0)
            shift = node.height + gap_y
            for r in range(parent_row + 1, rows):
                shifts[r] += shift
            offset = per_parent_offset.get(parent.id, 0.0)
            node.x = parent.x
            node.y = ys[parent_row] + row_h[parent_row] / 2 + gap_y + offset + node.height / 2
            per_parent_offset[parent.id] = offset + shift

        for node, row, _ in slots:
            node.y = ys[row] + shifts[row]
    return data
