# -*- coding: utf-8 -*-
"""C2VSDX 统一 Visio 样式主题（Nebula 呼应 · 文档级配色）。

所有图表 renderer 共用：字体层级、节点浅色填充、连线箭头/线宽、节点阴影。
颜色为 RGB 整数（r + g<<8 + b<<16），供 rgb_to_visio() 转 Visio 公式。
"""
from common.visio_utils import rgb_to_visio

# ---------- 字体 ----------
FONT = "Microsoft YaHei"

SIZE_TITLE = 14        # 图表/泳道标题
SIZE_HEADER = 12       # 分组/泳道/层标签
SIZE_NODE = 10         # 节点正文
SIZE_NODE_SMALL = 9    # 子节点/接口/成员
SIZE_EDGE = 8          # 连线标签

# ---------- 文字色（RGB int） ----------
TEXT = 0x333333          # 深灰（正文）
TEXT_MUTED = 0x808080    # 中灰（次要）
TEXT_LIGHT = 0xFFFFFF    # 白（深底上）

# ---------- 线条 ----------
LINE_DARK = 0x404040     # 主流程线（深灰）
LINE_MUTED = 0x999999    # 次要线（lifeline/泳道分隔）
LINE_ACCENT = 0x00A0C6   # 强调线（青，Nebula 主色）

WEIGHT_MAIN = "1 pt"
WEIGHT_THIN = "0.75 pt"
WEIGHT_BOLD = "1.5 pt"

# ---------- 节点填充（浅色系，按角色区分） ----------
FILL_NODE = 0xFFFFFF     # 普通节点（白）
FILL_PROCESS = 0xEAF3FB  # 流程（浅蓝）
FILL_DECISION = 0xFFF4E0 # 决策（浅琥珀）
FILL_STARTEND = 0xE8F7EC # 起止（浅绿）
FILL_HEADER = 0x2D5A8C   # 泳道/层 header（深蓝）
FILL_SOFT = 0xF5F8FC     # 极浅蓝（次要底）

# ---------- 节点边框 ----------
BORDER_NODE = 0x4A9EFF   # 节点边（蓝）
BORDER_DECISION = 0xFFB347
BORDER_STARTEND = 0x00A878
BORDER_HEADER = 0x1B4E7E

# ---------- 箭头 ----------
ARROW_SOLID = "4"   # 实心三角
ARROW_OPEN = "2"    # 开放箭头
ARROW_NONE = "0"

# ---------- 阴影 ----------
SHADOW_ON = "1"
SHADOW_COLOR = 0xC0C0C0


def apply_font(shape, size=SIZE_NODE, color=TEXT, bold=False, font=FONT):
    """设置形状文字：字体/字号/颜色/粗细。"""
    shape.Cells("Char.Font").FormulaU = f'"{font}"'
    shape.Cells("Char.Size").FormulaU = f"{size} pt"
    shape.Cells("Char.Color").FormulaU = rgb_to_visio(color)
    shape.Cells("Char.Style").FormulaU = "1" if bold else "0"


def apply_fill(shape, fill=FILL_NODE, border=BORDER_NODE, weight=WEIGHT_MAIN):
    """设置节点填充 + 边框色/线宽。"""
    shape.Cells("FillForegnd").FormulaU = rgb_to_visio(fill)
    shape.Cells("LineColor").FormulaU = rgb_to_visio(border)
    shape.Cells("LineWeight").FormulaU = weight


def apply_shadow(shape):
    """给形状加柔和外阴影。"""
    shape.Cells("ShadowPattern").FormulaU = SHADOW_ON
    shape.Cells("ShadowOffsetX").FormulaU = "0.02 in"
    shape.Cells("ShadowOffsetY").FormulaU = "0.02 in"
    shape.Cells("ShadowColor").FormulaU = rgb_to_visio(SHADOW_COLOR)


def style_edge(conn, arrow=ARROW_SOLID, color=LINE_DARK, weight=WEIGHT_MAIN,
               label="", size=SIZE_EDGE):
    """设置连线：箭头/颜色/线宽/标签。"""
    conn.Cells("EndArrow").FormulaU = arrow
    conn.Cells("LineColor").FormulaU = rgb_to_visio(color)
    conn.Cells("LineWeight").FormulaU = weight
    if label:
        conn.Text = label
        conn.Cells("Char.Font").FormulaU = f'"{FONT}"'
        conn.Cells("Char.Size").FormulaU = f"{size} pt"
        conn.Cells("Char.Color").FormulaU = rgb_to_visio(TEXT_MUTED)
        conn.Cells("Para.HorzAlign").FormulaU = "1"
