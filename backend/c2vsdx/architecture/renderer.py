import os

from common.visio_utils import start_visio, open_stencils, close_visio
from common import style
from architecture.models import ArchData
from architecture.layout_engine import LAYER_LABEL_WIDTH, MARGIN_LEFT


def render_to_visio(data: ArchData, output_path: str, visible: bool = False):
    """Render ArchData to a Visio document as a layered architecture diagram."""
    visio = start_visio(visible)
    basic_stencil, connector_stencil, stencil_masters, conn_master = open_stencils(visio)

    try:
        rect_master = stencil_masters.get("Rectangle")

        doc = visio.Documents.Add("")
        page = doc.Pages(1)

        # Compute page dimensions
        if data.layers:
            last_layer = data.layers[-1]
            page_height = last_layer.y + last_layer.height + 1.0
            from architecture.layout_engine import _compute_page_width
            page_width = _compute_page_width(data)
        else:
            page_width = 11.0
            page_height = 8.5

        page.PageSheet.Cells("PageWidth").FormulaU = f"{page_width:.2f} in"
        page.PageSheet.Cells("PageHeight").FormulaU = f"{page_height:.2f} in"

        def vy(layout_y: float) -> float:
            return page_height - layout_y

        # Draw layer bands (soft fill, muted dashed border)
        for i, layer in enumerate(data.layers):
            layer_shape = page.DrawRectangle(
                MARGIN_LEFT, vy(layer.y + layer.height),
                page_width - 0.3, vy(layer.y)
            )
            layer_shape.Cells("FillPattern").FormulaU = "1"
            layer_shape.Cells("FillForegnd").FormulaU = style.rgb_to_visio(style.FILL_SOFT)
            layer_shape.Cells("LineColor").FormulaU = style.rgb_to_visio(style.LINE_MUTED)
            layer_shape.Cells("LinePattern").FormulaU = "2"  # Dashed
            layer_shape.Cells("LineWeight").FormulaU = style.WEIGHT_THIN

            # Layer label — centered vertically, no background
            label_y = vy(layer.y + layer.height / 2)

            label_shape = page.DrawRectangle(
                MARGIN_LEFT + 0.1, label_y + 0.22,
                MARGIN_LEFT + LAYER_LABEL_WIDTH - 0.1, label_y - 0.22
            )
            label_shape.Text = layer.label
            style.apply_font(label_shape, style.SIZE_HEADER, style.TEXT_MUTED, bold=True)
            label_shape.Cells("FillPattern").FormulaU = "0"  # No fill
            label_shape.Cells("LinePattern").FormulaU = "0"  # No border
            label_shape.Cells("Para.HorzAlign").FormulaU = "1"

        # Draw components
        for comp in data.components:
            if comp.x is None or comp.y is None:
                continue

            shape = page.Drop(rect_master, comp.x, vy(comp.y))
            shape.Cells("Width").FormulaU = f"{comp.width:.4f} in"
            shape.Cells("Height").FormulaU = f"{comp.height:.4f} in"

            shape.Text = comp.label
            style.apply_font(shape, style.SIZE_NODE_SMALL, style.TEXT)
            style.apply_fill(shape, style.FILL_PROCESS, style.BORDER_NODE)
            style.apply_shadow(shape)
            shape.Cells("Para.HorzAlign").FormulaU = "1"

        abs_path = os.path.abspath(output_path)
        doc.SaveAs(abs_path)
    finally:
        close_visio(visio, doc, [basic_stencil, connector_stencil], visible)
