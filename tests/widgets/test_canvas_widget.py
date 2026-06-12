"""Tests for the canvas widget and its component tree renderer."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.geekmagic.widgets.base import WidgetConfig
from custom_components.geekmagic.widgets.canvas import (
    CanvasWidget,
    _dict_to_component,
    _parse_color,
)
from custom_components.geekmagic.widgets.colors import (
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
)
from custom_components.geekmagic.widgets.components import (
    Arc,
    Bar,
    Center,
    Circle,
    Column,
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
from custom_components.geekmagic.widgets.state import WidgetState


def test_parse_color_hex():
    """Test parsing #RRGGBB hex strings."""
    assert _parse_color("#ff0000") == (255, 0, 0)
    assert _parse_color("#00ff00") == (0, 255, 0)
    assert _parse_color("#0000ff") == (0, 0, 255)
    assert _parse_color("#fff") == (255, 255, 255)


def test_parse_color_rgb_tuple():
    """Test parsing RGB tuple/list."""
    assert _parse_color((255, 0, 0)) == (255, 0, 0)
    assert _parse_color([0, 255, 0]) == (0, 255, 0)


def test_parse_color_theme_names():
    """Test parsing theme color names to sentinels."""
    assert _parse_color("primary") is THEME_PRIMARY
    assert _parse_color("secondary") is THEME_SECONDARY
    assert _parse_color("success") is THEME_SUCCESS
    assert _parse_color("warning") is THEME_WARNING
    assert _parse_color("error") is THEME_ERROR
    assert _parse_color("info") is THEME_INFO
    assert _parse_color("muted") is THEME_MUTED
    assert _parse_color("text_primary") is THEME_TEXT_PRIMARY
    assert _parse_color("text_secondary") is THEME_TEXT_SECONDARY
    assert _parse_color("text_tertiary") is THEME_TEXT_TERTIARY


def test_parse_color_none():
    """Test None returns None."""
    assert _parse_color(None) is None


def test_parse_color_invalid():
    """Test invalid color returns None."""
    assert _parse_color("notacolor") is None
    assert _parse_color("#gggggg") is None  # Invalid hex
    assert _parse_color(12345) is None  # Invalid type


# Sentinel mocks for _dict_to_component's RenderContext and WidgetState params.
# These functions only use the params for recursive passthrough; none of these
# unit tests exercise actual drawing.
_MOCK_CTX = MagicMock()
_MOCK_STATE = MagicMock()


class TestDictToComponent:
    """Tests for _dict_to_component function."""

    def test_text(self):
        """Test text node conversion."""
        node = {"type": "text", "text": "Hello", "font": "primary", "color": "warning"}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Text)
        assert result.text == "Hello"
        assert result.font == "primary"
        assert result.color is THEME_WARNING

    def test_text_defaults(self):
        """Test text node uses defaults."""
        node = {"type": "text", "text": "Hi"}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Text)
        assert result.text == "Hi"
        assert result.font == "regular"
        assert result.color is THEME_TEXT_PRIMARY
        assert result.align == "center"

    def test_icon(self):
        """Test icon node conversion."""
        node = {"type": "icon", "icon": "mdi:thermometer", "size": 24, "color": "success"}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Icon)
        assert result.name == "mdi:thermometer"
        assert result.size == 24
        assert result.color is THEME_SUCCESS

    def test_bar(self):
        """Test bar node conversion."""
        node = {"type": "bar", "percent": 75, "color": "warning"}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Bar)
        assert result.percent == 75.0
        assert result.color is THEME_WARNING

    def test_ring(self):
        """Test ring node conversion."""
        node = {"type": "ring", "percent": 60, "color": "success"}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Ring)
        assert result.percent == 60.0
        assert result.color is THEME_SUCCESS

    def test_arc(self):
        """Test arc node conversion."""
        node = {"type": "arc", "percent": 30, "color": "error"}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Arc)
        assert result.percent == 30.0
        assert result.color is THEME_ERROR

    def test_sparkline(self):
        """Test sparkline node conversion."""
        node = {"type": "sparkline", "data": [1, 2, 3, 4], "color": "info"}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Sparkline)
        assert result.data == [1, 2, 3, 4]
        assert result.color is THEME_INFO

    def test_vertical_bar(self):
        """Test vertical_bar node conversion."""
        node = {"type": "vertical_bar", "percent": 50}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, VerticalBar)
        assert result.percent == 50.0

    def test_rect(self):
        """Test rect node conversion."""
        node = {"type": "rect", "fill": "#ff0000", "radius": 4}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Rect)
        assert result.radius == 4

    def test_circle(self):
        """Test circle node conversion."""
        node = {"type": "circle", "fill": "primary", "outline": "secondary", "width": 2}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Circle)
        assert result.fill is THEME_PRIMARY
        assert result.outline is THEME_SECONDARY
        assert result.width == 2

    def test_line(self):
        """Test line node conversion."""
        node = {"type": "line", "points": [[10, 20], [30, 40]], "color": "error", "width": 2}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Line)
        assert result.points == [(10, 20), (30, 40)]
        assert result.color is THEME_ERROR
        assert result.width == 2

    def test_polygon(self):
        """Test polygon node conversion."""
        node = {
            "type": "polygon",
            "points": [[0, 0], [50, 0], [25, 50]],
            "fill": "success",
            "outline": "muted",
        }
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Polygon)
        assert result.points == [(0, 0), (50, 0), (25, 50)]

    def test_panel_with_child(self):
        """Test panel node with child."""
        node = {
            "type": "panel",
            "child": {"type": "text", "text": "inside"},
            "color": "muted",
            "radius": 8,
        }
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Panel)
        assert result.radius == 8
        assert isinstance(result.child, Text)
        assert result.child.text == "inside"

    def test_row(self):
        """Test row node with children."""
        node = {
            "type": "row",
            "children": [
                {"type": "text", "text": "A"},
                {"type": "text", "text": "B"},
            ],
            "gap": 4,
        }
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Row)
        assert len(result.children) == 2
        assert result.gap == 4

    def test_column(self):
        """Test column node."""
        node = {
            "type": "column",
            "children": [{"type": "text", "text": "X"}],
            "padding": 8,
        }
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Column)
        assert len(result.children) == 1
        assert result.padding == 8

    def test_stack(self):
        """Test stack node."""
        node = {
            "type": "stack",
            "children": [
                {"type": "rect", "fill": "#000"},
                {"type": "text", "text": "overlay"},
            ],
        }
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Stack)
        assert len(result.children) == 2

    def test_center(self):
        """Test center node conversion."""
        node = {"type": "center", "children": [{"type": "text", "text": "centered"}]}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Center)
        assert isinstance(result.child, Text)
        assert result.child.text == "centered"

    def test_spacer(self):
        """Test spacer node conversion."""
        node = {"type": "spacer", "min_size": 10}
        result = _dict_to_component(node, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Spacer)
        assert result.min_size == 10

    def test_invalid_type_returns_spacer(self):
        """Test unknown type returns Spacer."""
        result = _dict_to_component({"type": "nonexistent"}, _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Spacer)

    def test_non_dict_returns_spacer(self):
        """Test non-dict input returns Spacer."""
        result = _dict_to_component("hello", _MOCK_CTX, _MOCK_STATE)
        assert isinstance(result, Spacer)


class TestCanvasWidget:
    """Tests for CanvasWidget."""

    def test_init(self):
        """Test basic initialization."""
        config = WidgetConfig(
            widget_type="canvas",
            slot=0,
            options={
                "children": [
                    {"type": "text", "text": "Hello"},
                    {"type": "rect", "fill": "#ff0000"},
                ]
            },
        )
        widget = CanvasWidget(config)
        assert widget.WIDGET_TYPE == "canvas"
        assert len(widget._raw_children) == 2

    def test_init_with_yaml_string(self):
        """Test initialization with a YAML string."""
        config = WidgetConfig(
            widget_type="canvas",
            slot=0,
            options={"children": '- type: text\n  text: Hello\n- type: rect\n  fill: "#ff0000"\n'},
        )
        widget = CanvasWidget(config)
        assert len(widget._raw_children) == 2
        assert widget._raw_children[0]["type"] == "text"
        assert widget._raw_children[0]["text"] == "Hello"
        assert widget._raw_children[1]["type"] == "rect"
        assert widget._raw_children[1]["fill"] == "#ff0000"

    def test_init_with_empty_yaml_string(self):
        """Test initialization with an empty YAML string."""
        config = WidgetConfig(
            widget_type="canvas",
            slot=0,
            options={"children": ""},
        )
        widget = CanvasWidget(config)
        assert widget._raw_children == []

    def test_init_with_invalid_yaml(self):
        """Test initialization with invalid YAML returns empty list."""
        config = WidgetConfig(
            widget_type="canvas",
            slot=0,
            options={"children": "{{ broken yaml: ["},
        )
        widget = CanvasWidget(config)
        assert widget._raw_children == []

    def test_render_returns_stack(self):
        """Test render returns a Stack component."""
        config = WidgetConfig(
            widget_type="canvas",
            slot=0,
            options={"children": [{"type": "text", "text": "A"}]},
        )
        widget = CanvasWidget(config)
        state = WidgetState()
        result = widget.render(_MOCK_CTX, state)
        assert isinstance(result, Stack)
        assert len(result.children) == 1
        assert isinstance(result.children[0], Text)

    def test_positioned_wrapping(self):
        """Test nodes with x/y get Positioned wrapper."""
        config = WidgetConfig(
            widget_type="canvas",
            slot=0,
            options={
                "children": [
                    {"type": "text", "text": "A", "x": 10, "y": 20},
                    {"type": "text", "text": "B"},  # No x/y, no wrapper
                ]
            },
        )
        widget = CanvasWidget(config)
        state = WidgetState()
        result = widget.render(_MOCK_CTX, state)
        assert len(result.children) == 2

        # First child should be Positioned
        assert isinstance(result.children[0], Positioned)
        assert result.children[0].x == 10
        assert result.children[0].y == 20
        assert isinstance(result.children[0].child, Text)
        assert result.children[0].child.text == "A"

        # Second child should be plain Text
        assert isinstance(result.children[1], Text)
        assert result.children[1].text == "B"

    def test_positioned_with_width_height(self):
        """Test Positioned with explicit width/height."""
        config = WidgetConfig(
            widget_type="canvas",
            slot=0,
            options={
                "children": [
                    {
                        "type": "rect",
                        "x": 5,
                        "y": 5,
                        "width": 100,
                        "height": 50,
                        "fill": "#ff0000",
                    }
                ]
            },
        )
        widget = CanvasWidget(config)
        state = WidgetState()
        result = widget.render(_MOCK_CTX, state)
        assert isinstance(result.children[0], Positioned)
        assert result.children[0].width == 100
        assert result.children[0].height == 50

    def test_canvas_tree_override(self):
        """Test state.canvas_tree overrides the config tree."""
        config = WidgetConfig(
            widget_type="canvas",
            slot=0,
            options={"children": [{"type": "text", "text": "original"}]},
        )
        widget = CanvasWidget(config)
        state = WidgetState(canvas_tree=[{"type": "text", "text": "overridden"}])
        result = widget.render(_MOCK_CTX, state)
        assert isinstance(result.children[0], Text)
        assert result.children[0].text == "overridden"

    def test_empty_children(self):
        """Test with no children returns empty Stack."""
        config = WidgetConfig(widget_type="canvas", slot=0, options={})
        widget = CanvasWidget(config)
        state = WidgetState()
        result = widget.render(_MOCK_CTX, state)
        assert isinstance(result, Stack)
        assert len(result.children) == 0

    def test_color_resolution_in_text(self):
        """Test that color strings are properly resolved in rendered tree."""
        config = WidgetConfig(
            widget_type="canvas",
            slot=0,
            options={
                "children": [
                    {"type": "text", "text": "test", "color": "success"},
                    {"type": "text", "text": "hex", "color": "#ff8800"},
                ]
            },
        )
        widget = CanvasWidget(config)
        state = WidgetState()
        result = widget.render(_MOCK_CTX, state)
        assert result.children[0].color is THEME_SUCCESS
        assert result.children[0].text == "test"
        assert result.children[1].color == (255, 136, 0)

    def test_line_with_points(self):
        """Test line with points in rendered tree."""
        config = WidgetConfig(
            widget_type="canvas",
            slot=0,
            options={
                "children": [
                    {
                        "type": "line",
                        "points": [[10, 20], [30, 40], [50, 60]],
                        "color": "warning",
                        "width": 2,
                    }
                ]
            },
        )
        widget = CanvasWidget(config)
        state = WidgetState()
        result = widget.render(_MOCK_CTX, state)
        assert isinstance(result.children[0], Line)
        assert result.children[0].points == [(10, 20), (30, 40), (50, 60)]
        assert result.children[0].color is THEME_WARNING
        assert result.children[0].width == 2

    def test_nested_layout(self):
        """Test nested layout components."""
        config = WidgetConfig(
            widget_type="canvas",
            slot=0,
            options={
                "children": [
                    {
                        "type": "row",
                        "gap": 8,
                        "children": [
                            {"type": "text", "text": "left"},
                            {"type": "text", "text": "right"},
                        ],
                    }
                ]
            },
        )
        widget = CanvasWidget(config)
        state = WidgetState()
        result = widget.render(_MOCK_CTX, state)
        assert isinstance(result.children[0], Row)
        assert result.children[0].gap == 8
        assert len(result.children[0].children) == 2
        assert result.children[0].children[0].text == "left"
        assert result.children[0].children[1].text == "right"

    def test_mixed_positioned_and_unpositioned(self):
        """Test mixing positioned and unpositioned children."""
        config = WidgetConfig(
            widget_type="canvas",
            slot=0,
            options={
                "children": [
                    {"type": "rect", "fill": "#000"},
                    {"type": "text", "text": "floating", "x": 50, "y": 50},
                    {"type": "circle", "x": 120, "y": 120, "width": 40, "height": 40},
                ]
            },
        )
        widget = CanvasWidget(config)
        state = WidgetState()
        result = widget.render(_MOCK_CTX, state)
        assert len(result.children) == 3
        assert isinstance(result.children[0], Rect)
        assert isinstance(result.children[1], Positioned)
        assert isinstance(result.children[2], Positioned)
