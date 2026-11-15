import os

from common.visio_utils import start_visio, open_stencils, close_visio, rgb_to_visio
from common import style
from sequence.layout_engine import MARGIN_LEFT, MARGIN_TOP, PARTICIPANT_BOX_HEIGHT, PARTICIPANT_BOX_WIDTH, PARTICIPANT_SPACING, MESSAGE_SPACING
from sequence.models import FragmentType, MessageType, SequenceData

ACTIVATION_WIDTH = 0.15  # Narrow activation bar width (inches)


def render_to_visio(data: SequenceData, output_path: str, visible: bool = False):
    """Render SequenceData to a Visio document following UML sequence diagram conventions."""
    visio = start_visio(visible)
    basic_stencil, connector_stencil, stencil_masters, conn_master = open_stencils(visio)

    try:
        rect_master = stencil_masters.get("Rectangle")
        doc = visio.Documents.Add("")
        page = doc.Pages(1)

        # Compute page dimensions first (need page_height for Y flip)
        n_participants = len(data.participants) or 1
        n_messages = len(data.messages)
        page_width = min(MARGIN_LEFT * 2 + (n_participants - 1) * PARTICIPANT_SPACING + PARTICIPANT_BOX_WIDTH, 50)
        page_height = min(MARGIN_TOP + PARTICIPANT_BOX_HEIGHT + n_messages * MESSAGE_SPACING + 2.0, 50)
        page.PageSheet.Cells("PageWidth").FormulaU = f"{page_width:.2f} in"
        page.PageSheet.Cells("PageHeight").FormulaU = f"{page_height:.2f} in"

        # Y-flip function: convert layout Y (top-down) to Visio Y (bottom-up)
        def vy(layout_y: float) -> float:
            return page_height - layout_y

        # Compute activation bars
        activations = _compute_activations(data, page_height)

        # Draw lifelines (dashed vertical lines, behind everything)
        lifeline_bottom_layout = (max(m.y for m in data.messages if m.y is not None) + 1.5) if data.messages else MARGIN_TOP
        lifeline_bottom_vy = vy(lifeline_bottom_layout)
        for p in data.participants:
            _draw_lifeline(page, p.x, vy(MARGIN_TOP + PARTICIPANT_BOX_HEIGHT / 2), lifeline_bottom_vy)

        # Draw activation bars
        for act in activations:
            _draw_activation_bar(page, act, rect_master)

        # Draw participant boxes at the very top
        for p in data.participants:
            _draw_participant_box(page, p, rect_master, vy(MARGIN_TOP))

        # Draw fragments
        for frag in data.fragments:
            _draw_fragment(page, frag, data, rect_master, vy)

        # Draw messages
        for msg in data.messages:
            from_p = data.get_participant(msg.from_id)
            to_p = data.get_participant(msg.to_id)
            if not from_p or not to_p or msg.y is None:
                continue
            msg_vy = vy(msg.y)
            if msg.msg_type == MessageType.SELF:
                _draw_self_message(page, from_p.x, msg_vy, msg.label)
            else:
                _draw_message(page, from_p.x, to_p.x, msg_vy, msg.label, msg.msg_type)

        abs_path = os.path.abspath(output_path)
        doc.SaveAs(abs_path)
    finally:
        close_visio(visio, doc, [basic_stencil, connector_stencil], visible)


def _compute_activations(data: SequenceData, page_height: float) -> list[dict]:
    """Compute activation bar positions with Y-flipped coordinates."""
    activations = []
    for p in data.participants:
        involved_msgs = []
        for msg in data.messages:
            if msg.y is None:
                continue
            if msg.from_id == p.id or msg.to_id == p.id:
                involved_msgs.append(msg)

        if not involved_msgs:
            continue

        first_y = min(m.y for m in involved_msgs)
        last_y = max(m.y for m in involved_msgs)

        # Flip Y: in layout, top_y < bottom_y; in Visio, after flip, top_vy > bottom_vy
        activations.append({
            "x": p.x,
            "top_vy": page_height - (first_y - 0.15),
            "bottom_vy": page_height - (last_y + 0.15),
        })

    return activations


def _draw_lifeline(page, x: float, top_vy: float, bottom_vy: float):
    """Draw a dashed vertical lifeline. All coordinates already in Visio space."""
    line = page.DrawLine(x, top_vy, x, bottom_vy)
    line.Cells("LinePattern").FormulaU = "2"  # Dashed
    line.Cells("LineColor").FormulaU = rgb_to_visio(style.LINE_MUTED)
    line.Cells("LineWeight").FormulaU = style.WEIGHT_THIN
    line.Cells("EndArrow").FormulaU = "0"


def _draw_activation_bar(page, act: dict, master):
    """Draw a narrow activation bar on a lifeline. Coordinates already in Visio space."""
    x = act["x"]
    top = act["top_vy"]
    bottom = act["bottom_vy"]
    half_w = ACTIVATION_WIDTH / 2

    shape = page.DrawRectangle(x - half_w, bottom, x + half_w, top)
    shape.Cells("FillForegnd").FormulaU = rgb_to_visio(style.FILL_SOFT)
    shape.Cells("LineColor").FormulaU = rgb_to_visio(style.LINE_MUTED)
    shape.Cells("LineWeight").FormulaU = style.WEIGHT_THIN


def _draw_participant_box(page, participant, master, visio_y: float):
    """Draw a participant box. visio_y is the Y-flipped position."""
    x = participant.x
    shape = page.Drop(master, x, visio_y)

    shape.Cells("Width").FormulaU = f"{PARTICIPANT_BOX_WIDTH:.4f} in"
    shape.Cells("Height").FormulaU = f"{PARTICIPANT_BOX_HEIGHT:.4f} in"
    shape.Text = participant.label
    style.apply_font(shape, style.SIZE_HEADER, style.TEXT_LIGHT, bold=True)
    shape.Cells("Para.HorzAlign").FormulaU = "1"
    style.apply_fill(shape, style.FILL_HEADER, style.BORDER_HEADER)
    style.apply_shadow(shape)


def _draw_message(page, from_x: float, to_x: float, y: float, label: str, msg_type: MessageType):
    """Draw a message arrow between two lifelines."""
    # Offset arrow start/end to edge of activation bar
    if from_x < to_x:
        start_x = from_x + ACTIVATION_WIDTH / 2
        end_x = to_x - ACTIVATION_WIDTH / 2
    elif from_x > to_x:
        start_x = from_x - ACTIVATION_WIDTH / 2
        end_x = to_x + ACTIVATION_WIDTH / 2
    else:
        start_x = from_x
        end_x = to_x

    line = page.DrawLine(start_x, y, end_x, y)

    if msg_type == MessageType.SYNC:
        line.Cells("EndArrow").FormulaU = style.ARROW_SOLID  # Filled arrow
        line.Cells("LinePattern").FormulaU = "1"  # Solid
    elif msg_type == MessageType.ASYNC:
        line.Cells("EndArrow").FormulaU = style.ARROW_OPEN  # Open arrow
        line.Cells("LinePattern").FormulaU = "1"  # Solid
    elif msg_type == MessageType.RETURN:
        line.Cells("EndArrow").FormulaU = style.ARROW_OPEN  # Open arrow
        line.Cells("LinePattern").FormulaU = "2"  # Dashed

    line.Cells("LineColor").FormulaU = rgb_to_visio(style.LINE_DARK)
    line.Cells("LineWeight").FormulaU = style.WEIGHT_MAIN

    # Message label above the line (in Visio space, "above" = larger Y)
    if label:
        mid_x = (start_x + end_x) / 2
        label_offset = 0.12
        text_shape = page.DrawRectangle(
            mid_x - 1.0, y + label_offset,
            mid_x + 1.0, y + label_offset + 0.35
        )
        text_shape.Text = label
        text_shape.Cells("Char.Font").FormulaU = f'"{style.FONT}"'
        text_shape.Cells("Char.Size").FormulaU = f"{style.SIZE_EDGE} pt"
        text_shape.Cells("Char.Color").FormulaU = rgb_to_visio(style.TEXT_MUTED)
        text_shape.Cells("LinePattern").FormulaU = "0"  # No border
        text_shape.Cells("FillPattern").FormulaU = "0"  # Transparent background
        text_shape.Cells("Para.HorzAlign").FormulaU = "1"


def _draw_self_message(page, x: float, y: float, label: str):
    """Draw a self-call message (small loop to the right of activation bar)."""
    offset_x = 0.5
    offset_y = 0.3
    start_x = x + ACTIVATION_WIDTH / 2

    # Draw loop: right from activation bar, down (smaller Y in Visio), left back
    page.DrawLine(start_x, y, start_x + offset_x, y)
    page.DrawLine(start_x + offset_x, y, start_x + offset_x, y - offset_y)
    line3 = page.DrawLine(start_x + offset_x, y - offset_y, start_x, y - offset_y)
    line3.Cells("EndArrow").FormulaU = style.ARROW_SOLID
    line3.Cells("LineColor").FormulaU = rgb_to_visio(style.LINE_DARK)
    line3.Cells("LineWeight").FormulaU = style.WEIGHT_MAIN

    if label:
        text_shape = page.DrawRectangle(
            start_x + offset_x, y - offset_y - 0.25,
            start_x + offset_x + 1.0, y - offset_y - 0.05
        )
        text_shape.Text = label
        text_shape.Cells("Char.Font").FormulaU = f'"{style.FONT}"'
        text_shape.Cells("Char.Size").FormulaU = f"{style.SIZE_EDGE} pt"
        text_shape.Cells("Char.Color").FormulaU = rgb_to_visio(style.TEXT_MUTED)
        text_shape.Cells("LinePattern").FormulaU = "0"
        text_shape.Cells("FillPattern").FormulaU = "0"  # Transparent background
        text_shape.Cells("Para.HorzAlign").FormulaU = "0"


def _draw_fragment(page, fragment, data: SequenceData, master, vy):
    """Draw a fragment box. Uses vy function to flip Y coordinates."""
    if fragment.start_y is None or fragment.end_y is None:
        return

    pids = fragment.participant_ids
    if pids:
        xs = []
        for pid in pids:
            p = data.get_participant(pid)
            if p and p.x is not None:
                xs.append(p.x)
        if xs:
            left = min(xs) - 0.8
            right = max(xs) + 0.8
        else:
            left = MARGIN_LEFT - 0.8
            right = MARGIN_LEFT + (len(data.participants) - 1) * PARTICIPANT_SPACING + 0.8
    else:
        left = MARGIN_LEFT - 0.8
        right = MARGIN_LEFT + (len(data.participants) - 1) * PARTICIPANT_SPACING + 0.8

    # Flip Y: start_y is earlier in time (higher visio Y), end_y is later (lower visio Y)
    top_vy = vy(fragment.start_y)
    bottom_vy = vy(fragment.end_y)

    # Draw fragment box (dashed muted border, transparent fill)
    frag_shape = page.DrawRectangle(left, bottom_vy, right, top_vy)
    frag_shape.Cells("LinePattern").FormulaU = "2"  # Dashed
    frag_shape.Cells("LineColor").FormulaU = rgb_to_visio(style.LINE_MUTED)
    frag_shape.Cells("LineWeight").FormulaU = style.WEIGHT_THIN
    frag_shape.Cells("FillForegnd").FormulaU = rgb_to_visio(style.FILL_SOFT)
    frag_shape.Cells("FillPattern").FormulaU = "0"  # No fill (transparent)

    # Draw label tab in top-left corner (top_vy is the upper edge)
    tab_width = 0.8
    tab_height = 0.25
    tab_shape = page.DrawRectangle(left, top_vy - tab_height, left + tab_width, top_vy)
    tab_shape.Text = fragment.frag_type.value.upper()
    style.apply_font(tab_shape, style.SIZE_NODE_SMALL, style.TEXT_MUTED, bold=True)
    style.apply_fill(tab_shape, style.FILL_SOFT, style.LINE_MUTED, style.WEIGHT_THIN)
    tab_shape.Cells("Para.HorzAlign").FormulaU = "1"

    # Fragment label
    if fragment.label and fragment.label != fragment.id:
        label_shape = page.DrawRectangle(
            left + tab_width, top_vy - tab_height,
            left + tab_width + 1.2, top_vy
        )
        label_shape.Text = fragment.label
        style.apply_font(label_shape, style.SIZE_NODE_SMALL, style.TEXT_MUTED)
        label_shape.Cells("LinePattern").FormulaU = "0"
        label_shape.Cells("FillPattern").FormulaU = "0"  # Transparent background
        label_shape.Cells("Para.HorzAlign").FormulaU = "0"
