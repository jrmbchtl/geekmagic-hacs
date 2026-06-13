"""Canvas widget — YAML-declarative free-form layout with absolute positioning.

The canvas widget accepts a tree of component definitions via
``options.children`` and renders them with full control over placement,
custom drawing, and HA Jinja2 templating.

Example config::

    layout: fullscreen
    widgets:
      - type: canvas
        slot: 0
        options:
          children:
            - type: rect
              x: 0; y: 0; width: 240; height: 240
              fill: "#1a1a2e"
            - type: circle
              x: 120; y: 100; width: 80; height: 80
              outline: text_primary; width: 3
            - type: text
              x: 10; y: 5
              text: "{{ states('sensor.temperature') }}°C"
              font: secondary; color: text_secondary
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

import yaml

from .base import Widget, WidgetConfig
from .colors import (
    THEME_ERROR,
    THEME_INFO,
    THEME_MUTED,
    THEME_PRIMARY,
    THEME_SECONDARY,
    THEME_SUCCESS,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    THEME_TEXT_TERTIARY,
    THEME_WARNING,
    Color,
)
from .components import (
    Arc,
    Bar,
    Center,
    Circle,
    Column,
    Component,
    Icon,
    Line,
    Panel,
    Polygon,
    Positioned,
    Rect,
    Ring,
    Row,
    Spacer,
    Sparkline,
    Stack,
    Text,
    VerticalBar,
)

if TYPE_CHECKING:
    from ..render_context import RenderContext
    from .state import WidgetState

import logging

_LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Colour name → sentinel mapping
# ---------------------------------------------------------------------------

_COLOR_MAP: dict[str, Color] = {
    "primary": THEME_PRIMARY,
    "secondary": THEME_SECONDARY,
    "success": THEME_SUCCESS,
    "warning": THEME_WARNING,
    "error": THEME_ERROR,
    "info": THEME_INFO,
    "muted": THEME_MUTED,
    "text_primary": THEME_TEXT_PRIMARY,
    "text_secondary": THEME_TEXT_SECONDARY,
    "text_tertiary": THEME_TEXT_TERTIARY,
}


def _parse_color(value: Any) -> Color | None:
    """Resolve a colour value to a sentinel or RGB tuple."""
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return (int(value[0]), int(value[1]), int(value[2]))
    if isinstance(value, str):
        if value.startswith("#"):
            h = value.lstrip("#")
            try:
                if len(h) == 6:
                    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))
                if len(h) == 3:
                    return tuple(int(c * 2, 16) for c in h)
            except ValueError:
                pass
            return None
        return _COLOR_MAP.get(value)
    return None


def _resolve_color(value: Any) -> Color | None:
    """Resolve colour value, preserving None passthrough."""
    if value is None:
        return None
    return _parse_color(value)


def _safe_int(value: Any, default: int = 0) -> int:
    """Convert to int safely, returning default on failure."""
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Convert to float safely, returning default on failure."""
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


# ---------------------------------------------------------------------------
# Type → Component handler mapping
# ---------------------------------------------------------------------------


def _handle_text(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    return Text(
        text=str(node.get("text", "")),
        font=str(node.get("font", "regular")),
        bold=bool(node.get("bold", False)),
        color=_resolve_color(node.get("color", "text_primary")) or THEME_TEXT_PRIMARY,
        align=str(node.get("align", "center")),  # type: ignore[arg-type]
        truncate=bool(node.get("truncate", False)),
        auto_fit=bool(node.get("auto_fit", False)),
        rotation=_safe_int(node.get("rotation")),
    )


def _handle_icon(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    return Icon(
        name=str(node.get("icon", "")),
        size=node.get("size"),
        color=_resolve_color(node.get("color", "text_primary")) or THEME_TEXT_PRIMARY,
    )


def _handle_bar(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    return Bar(
        percent=_safe_float(node.get("percent")),
        color=_resolve_color(node.get("color", "primary")) or THEME_PRIMARY,
        background=_resolve_color(node.get("background")),
        height=node.get("height"),
    )


def _handle_ring(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    return Ring(
        percent=_safe_float(node.get("percent")),
        color=_resolve_color(node.get("color", "primary")) or THEME_PRIMARY,
        background=_resolve_color(node.get("background")),
        thickness=node.get("thickness"),
    )


def _handle_arc(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    return Arc(
        percent=_safe_float(node.get("percent")),
        color=_resolve_color(node.get("color", "primary")) or THEME_PRIMARY,
        background=_resolve_color(node.get("background")),
        width=node.get("width"),
    )


def _handle_sparkline(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    raw = node.get("data", [])
    data = [_safe_float(v) for v in raw] if isinstance(raw, (list, tuple)) else []
    return Sparkline(
        data=data,
        color=_resolve_color(node.get("color", "primary")) or THEME_PRIMARY,
        fill=bool(node.get("fill", True)),
        smooth=bool(node.get("smooth", True)),
    )


def _handle_vertical_bar(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    return VerticalBar(
        percent=_safe_float(node.get("percent")),
        color=_resolve_color(node.get("color", "primary")) or THEME_PRIMARY,
        background=_resolve_color(node.get("background")),
        width=node.get("width"),
    )


def _handle_panel(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    child_node = node.get("child")
    child = _dict_to_component(child_node, ctx, state) if child_node else None
    return Panel(
        child=child,
        color=_resolve_color(node.get("color")),
        radius=node.get("radius"),
        border_color=_resolve_color(node.get("border_color")),
    )


def _handle_spacer(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    return Spacer(min_size=_safe_int(node.get("min_size")))


def _handle_rect(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    return Rect(
        fill=_resolve_color(node.get("fill")),
        outline=_resolve_color(node.get("outline")),
        width=_safe_int(node.get("width"), 1),
        radius=node.get("radius"),
    )


def _handle_circle(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    return Circle(
        fill=_resolve_color(node.get("fill")),
        outline=_resolve_color(node.get("outline")),
        width=_safe_int(node.get("width"), 1),
    )


def _handle_line(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    raw_points = node.get("points", [])
    points: list[tuple[int, int]] = []
    for p in raw_points:
        if not isinstance(p, (list, tuple)) or len(p) < 2:
            continue
        try:
            x = int(p[0])
            y = int(p[1])
            points.append((x, y))
        except (ValueError, TypeError):
            continue
    return Line(
        points=points,
        color=_resolve_color(node.get("color", "text_primary")) or THEME_TEXT_PRIMARY,
        width=_safe_int(node.get("width"), 1),
    )


def _handle_polygon(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
    raw_points = node.get("points", [])
    points: list[tuple[int, int]] = []
    for p in raw_points:
        if not isinstance(p, (list, tuple)) or len(p) < 2:
            continue
        try:
            x = int(p[0])
            y = int(p[1])
            points.append((x, y))
        except (ValueError, TypeError):
            continue
    return Polygon(
        points=points,
        fill=_resolve_color(node.get("fill")),
        outline=_resolve_color(node.get("outline")),
        width=_safe_int(node.get("width"), 1),
    )


def _handle_layout(
    component_cls: type[Row | Column | Stack | Center],
) -> Any:
    """Factory for layout component handlers."""

    def handler(node: dict, ctx: RenderContext, state: WidgetState) -> Component:
        raw_children = node.get("children", [])
        children = [_dict_to_component(c, ctx, state) for c in raw_children if isinstance(c, dict)]
        if issubclass(component_cls, (Row, Column)):
            kwargs: dict[str, Any] = {
                "gap": _safe_int(node.get("gap")),
                "padding": _safe_int(node.get("padding")),
            }
            if "align" in node:
                kwargs["align"] = node["align"]
            if "justify" in node:
                kwargs["justify"] = node["justify"]
            return component_cls(children=children, **kwargs)
        if issubclass(component_cls, Stack):
            kwargs = {}
            if "align" in node:
                kwargs["align"] = node["align"]
            return component_cls(children=children, **kwargs)
        if issubclass(component_cls, Center):
            child = children[0] if children else Spacer()
            return Center(child=child)
        return component_cls(children=children)

    return handler


_TYPE_HANDLERS: dict[str, Any] = {
    "text": _handle_text,
    "icon": _handle_icon,
    "bar": _handle_bar,
    "ring": _handle_ring,
    "arc": _handle_arc,
    "sparkline": _handle_sparkline,
    "vertical_bar": _handle_vertical_bar,
    "panel": _handle_panel,
    "spacer": _handle_spacer,
    "rect": _handle_rect,
    "circle": _handle_circle,
    "line": _handle_line,
    "polygon": _handle_polygon,
    "row": _handle_layout(Row),
    "column": _handle_layout(Column),
    "stack": _handle_layout(Stack),
    "center": _handle_layout(Center),
}


def _dict_to_component(node: Any, ctx: RenderContext, state: WidgetState) -> Component:
    """Convert a YAML/JSON node dict into a Component instance."""
    if not isinstance(node, dict):
        return Spacer()
    node_type = node.get("type", "")
    handler = _TYPE_HANDLERS.get(node_type)
    if handler is None:
        return Spacer()
    return handler(node, ctx, state)


# ---------------------------------------------------------------------------
# CanvasWidget
# ---------------------------------------------------------------------------


class CanvasWidget(Widget):
    """Widget that renders a YAML-defined component tree with absolute positioning.

    The tree is specified via ``config.options["children"]`` — a list of
    node dicts. Each node has a ``type`` field and type-specific attributes.

    Top-level nodes with ``x``/``y`` keys are automatically wrapped in a
    ``Positioned`` component for absolute placement on the 240x240 canvas.
    Nodes without ``x``/``y`` are overlaid via ``Stack`` (centred by default).
    """

    WIDGET_TYPE: ClassVar[str] = "canvas"
    SCHEMA: ClassVar[dict[str, Any]] = {
        "name": "Canvas",
        "needs_entity": False,
        "options": [
            {
                "key": "children",
                "type": "longtext",
                "label": "Component Tree (YAML list of nodes)",
                "placeholder": "- type: text\n  x: 10\n  y: 8\n  text: Hello\n  font: primary",
            },
        ],
    }

    def __init__(self, config: WidgetConfig) -> None:
        """Initialize the canvas widget."""
        super().__init__(config)
        raw = config.options.get("children", [])
        self._raw_yaml: str | None = raw if isinstance(raw, str) else None
        if isinstance(raw, str):
            try:
                parsed = yaml.safe_load(raw)
            except yaml.YAMLError:
                parsed = None
            if isinstance(parsed, list):
                self._raw_children: list[dict] = parsed
            elif isinstance(parsed, dict) and "children" in parsed:
                extracted = parsed["children"]
                self._raw_children = extracted if isinstance(extracted, list) else []
            else:
                self._raw_children = []
        else:
            self._raw_children = raw

    def render(self, ctx: RenderContext, state: WidgetState) -> Component:
        """Render the canvas widget."""
        tree = state.canvas_tree if state.canvas_tree is not None else self._raw_children
        if state.canvas_tree is not None:
            _LOGGER.debug("CanvasWidget.render using resolved state tree")
        else:
            _LOGGER.debug("CanvasWidget.render using raw_children (no state tree)")

        components: list[Component] = []
        for node in tree:
            if not isinstance(node, dict):
                continue
            comp = _dict_to_component(node, ctx, state)
            if "x" in node or "y" in node:
                comp = Positioned(
                    comp,
                    x=int(node.get("x", 0)),
                    y=int(node.get("y", 0)),
                    width=node.get("width"),
                    height=node.get("height"),
                )
            components.append(comp)

        return Stack(children=components)
