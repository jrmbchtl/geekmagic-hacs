# Canvas Widget — YAML Component Tree

The **Canvas** widget gives you pixel-level control over the 240×240 display.
Instead of choosing from pre-built layouts, you write a YAML list of
positioned nodes — text, shapes, icons, gauges, nested layouts — anywhere on
the screen.

It uses HA's Jinja2 template engine, so you can inject live sensor values,
entity states, and attributes into any string field with `{{ ... }}`.

## Configuration

Add a **Canvas** widget in the widget slot editor (the textarea labelled
*"Component Tree (YAML list of nodes)"*). Type or paste the YAML list
directly — no outer `layout:`, `widgets:`, or `options:` wrappers:

```yaml
- type: text
  x: 10
  y: 8
  text: "{{ states('sensor.temperature') }}°"
  font: primary
  bold: true
  color: text_primary

- type: text
  x: 10
  y: 210
  text: "{{ states('sensor.weather_condition') }}"
  font: tertiary
  color: text_secondary
```

> **Tip:** If you paste a YAML dict that starts with `children:`, the widget
> automatically extracts the list underneath `children`. Both formats work.

## Positioning

Every top-level node with an `x` or `y` key is wrapped in a `Positioned`
container and placed absolutely on the 240×240 canvas.

| Field | Type | Default | Description |
|---|---|---|---|
| `x` | int | — | Horizontal position from left (0–240) |
| `y` | int | — | Vertical position from top (0–240) |
| `width` | int | auto | Explicit width constraint (for gauges, containers) |
| `height` | int | auto | Explicit height constraint |

Nodes **without** `x`/`y` are overlaid via `Stack` and centred in the slot
by default.

```yaml
# Fixed position
- type: text
  x: 120
  y: 100
  text: "Hello"
  align: center

# No x/y — centred by Stack
- type: text
  text: "Overlay"
  align: center
```

## Colour System

Colours can be specified in three ways:

| Format | Example | Notes |
|---|---|---|
| **Theme role** | `text_primary` | Resolves to the active theme's palette (see table below) |
| **Hex string** | `"#ff5500"` or `"#f50"` | Short form `#RGB` is expanded to `#RRGGBB` |
| **RGB list** | `[255, 85, 0]` | Tuple of three ints 0–255 |

When no colour is specified, each type picks a sensible default (usually
`text_primary` or `primary`).

### Theme Role Sentinels

| Sentinel | Use case |
|---|---|
| `text_primary` | Hero values, main text (white-ish) |
| `text_secondary` | Supporting info, dates, units |
| `text_tertiary` | Captions, low-priority text |
| `primary` | Brand accent, chart fill, progress |
| `secondary` | Less prominent accents |
| `success` | ON, connected |
| `warning` | Sunny, hot, caution |
| `error` | OFF, disconnected, extreme |
| `info` | Cool, cold, humidity |
| `muted` | Disabled, idle, off |

## Templating (HA Jinja2)

Any string field containing `{{ ... }}` is pre-resolved by HA's template
engine before rendering. You have full access to `states()`, `is_state()`,
`state_attr()`, and all Jinja2 filters.

```yaml
- type: text
  x: 10
  y: 8
  text: "{{ states('sensor.temperature') | round(1) }}°C"
  font: primary
  bold: true

- type: text
  x: 10
  y: 45
  text: "{{ states('sensor.humidity') }}% humidity"
  font: tertiary

- type: text
  x: 10
  y: 210
  text: "Last: {{ as_timestamp(states('binary_sensor.door').last_changed) | timestamp_custom('%H:%M') }}"
  font: tertiary
```

Templates are resolved in the coordinator's async context, so `hass.states`
is safe. If template rendering fails, the raw string is kept as-is.

## Node Types

### `text` — Text label

```yaml
- type: text
  x: 10
  y: 10
  text: "Hello"           # Text content (supports templates)
  font: primary           # primary | secondary | tertiary | tiny | small | regular | medium | large | xlarge | huge
  bold: true              # false by default
  color: text_primary     # Colour (hex, role, or RGB)
  align: center           # start | center | end
  truncate: false         # Truncate with ellipsis if too wide
  auto_fit: false         # Auto-scale font to fill available space
  rotation: 0             # Rotation in degrees (0, 90, 180, 270)
```

> **Font sizing:** `primary` (~35% of container height), `secondary` (~20%),
> `tertiary` (~12%). See AGENTS.md for the full font system.

### `icon` — Material Design icon

```yaml
- type: icon
  x: 10
  y: 10
  icon: "mdi:weather-sunny"   # MDI icon name
  size: 24                    # Pixel size (optional, theme default otherwise)
  color: warning              # Colour (hex, role, or RGB)
```

### `rect` — Rectangle

```yaml
- type: rect
  x: 0
  y: 0
  width: 240
  height: 240
  fill: "#1a1a2e"            # Fill colour (optional)
  outline: text_primary      # Outline colour (optional)
  width: 2                   # Outline thickness (default 1)
  radius: 8                  # Corner radius (optional)
```

### `circle` — Circle

```yaml
- type: circle
  x: 120
  y: 100
  width: 80
  height: 80
  fill: primary              # Fill colour (optional)
  outline: text_primary      # Outline colour (optional)
  width: 3                   # Outline thickness (default 1)
```

The ellipse fills its `width` × `height` bounding box. For a perfect circle,
width and height should match.

### `line` — Polyline

```yaml
- type: line
  x: 10
  y: 50
  points:
    - [10, 0]
    - [50, 20]
    - [90, 10]
    - [130, 40]
  color: text_primary        # Line colour
  width: 2                   # Stroke thickness (default 1)
```

`points` is a list of `[x, y]` coordinates expressed **relative** to the
node's `x`/`y` position.

### `polygon` — Filled polygon

```yaml
- type: polygon
  x: 120
  y: 120
  points:
    - [0, -20]
    - [20, 20]
    - [-20, 20]
  fill: success              # Fill colour (optional)
  outline: text_primary      # Outline colour (optional)
  width: 1                   # Outline thickness (default 1)
```

`points` is a list of `[x, y]` coordinates relative to `x`/`y`. The shape is
automatically closed.

### `bar` — Horizontal progress bar

```yaml
- type: bar
  x: 10
  y: 100
  width: 220
  height: 12
  percent: 73               # Value 0–100
  color: primary             # Fill colour
  background: muted          # Track colour (optional)
```

### `vertical_bar` — Vertical progress bar

```yaml
- type: vertical_bar
  x: 50
  y: 20
  width: 16
  height: 150
  percent: 65               # Value 0–100
  color: info                # Fill colour
  background: muted          # Track colour (optional)
```

### `ring` — Circular ring gauge

```yaml
- type: ring
  x: 80
  y: 40
  width: 80
  height: 80
  percent: 60               # Value 0–100
  color: success             # Arc fill colour
  background: muted          # Track colour (optional)
  thickness: 10              # Ring thickness in px (optional)
```

### `arc` — Arc gauge (partial ring)

```yaml
- type: arc
  x: 40
  y: 30
  width: 160
  height: 80
  percent: 45               # Value 0–100
  color: warning             # Arc fill colour
  background: muted          # Track colour (optional)
```

### `sparkline` — Mini chart line

```yaml
- type: sparkline
  x: 10
  y: 80
  width: 220
  height: 40
  data: [23, 25, 22, 28, 26, 30, 29, 31, 33, 35, 32, 30, 28, 27]
  color: primary             # Line colour
  fill: true                 # Fill area under the line
  smooth: true               # Smooth curve vs straight lines
```

### `panel` — Background card/panel

```yaml
- type: panel
  x: 5
  y: 5
  width: 230
  height: 230
  color: muted               # Background fill (optional)
  radius: 12                 # Corner radius (optional)
  border_color: text_tertiary  # Border colour (optional)
  child:
    type: text
    text: "Inside the panel"
    align: center
```

`panel` wraps a single `child` node inside a rounded background rectangle.

### `spacer` — Empty flexible space

```yaml
- type: spacer
  min_size: 10               # Minimum space in px
```

Useful inside `row`/`column` layouts to push items apart.

## Layout Node Types

### `row` — Horizontal flex container

```yaml
- type: row
  x: 10
  y: 10
  width: 220
  height: 30
  gap: 4
  padding: 4
  align: center              # start | center | end | stretch
  justify: space-between     # start | center | end | space-between | space-evenly | space-around
  children:
    - type: text
      text: "Left"
      color: text_primary
    - type: text
      text: "Right"
      color: text_secondary
```

### `column` — Vertical flex container

Same fields as `row`, but stacks children vertically.

### `stack` — Overlay container

```yaml
- type: stack
  x: 10
  y: 10
  width: 220
  height: 220
  align: center              # start | center | end | stretch
  children:
    - type: rect
      fill: "#1a1a2e"
    - type: text
      text: "Overlay"
      align: center
```

Children are drawn on top of each other in order.

### `center` — Centering wrapper

```yaml
- type: center
  x: 0
  y: 0
  width: 240
  height: 240
  child:
    type: text
    text: "Centred"
    font: primary
    align: center
```

Wraps a single `child` and centres it within the bounding box.

## Examples

### Temperature & weather condition

```yaml
- type: text
  x: 15
  y: 15
  text: "{{ states('sensor.outdoor_temperature') }}°"
  font: primary
  bold: true
  color: text_primary

- type: icon
  x: 190
  y: 15
  icon: "mdi:weather-partly-cloudy"
  size: 32
  color: text_primary

- type: text
  x: 15
  y: 210
  text: "{{ states('sensor.weather_condition') }}"
  font: tertiary
  color: text_secondary
```

### Smiley face (dynamic mouth via template)

```yaml
- type: rect
  fill: "#1a1a2e"

- type: circle
  x: 120
  y: 105
  width: 110
  height: 110
  outline: text_primary
  width: 3

- type: circle
  x: 90
  y: 85
  width: 14
  height: 14
  fill: text_primary

- type: circle
  x: 136
  y: 85
  width: 14
  height: 14
  fill: text_primary

# Mouth: sad → happy based on slider value
- type: line
  points:
    - [80, "{{ 115 + (1 - states('input_number.happiness')|int / 100) * 25 }}"]
    - [120, "{{ 122 + (1 - states('input_number.happiness')|int / 100) * 25 }}"]
    - [160, "{{ 115 + (1 - states('input_number.happiness')|int / 100) * 25 }}"]
  color: text_primary
  width: 3
```

### Clock with date

```yaml
- type: text
  x: 120
  y: 50
  text: "{{ now().strftime('%H:%M') }}"
  font: primary
  bold: true
  color: text_primary
  align: center

- type: text
  x: 120
  y: 120
  text: "{{ now().strftime('%A') }}"
  font: tertiary
  color: text_secondary
  align: center

- type: text
  x: 120
  y: 145
  text: "{{ now().strftime('%-d %B %Y') }}"
  font: tertiary
  color: text_tertiary
  align: center
```

### Battery gauge card

```yaml
- type: panel
  x: 10
  y: 10
  width: 220
  height: 100
  color: muted
  radius: 12
  child:
    type: row
    gap: 8
    padding: 12
    align: center
    children:
      - type: icon
        icon: "mdi:battery"
        size: 28
        color: success
      - type: column
        gap: 2
        children:
          - type: text
            text: "Battery"
            font: small
            color: text_secondary
          - type: text
            text: "{{ states('sensor.battery_level') }}%"
            font: primary
            bold: true
            color: text_primary
```

### System monitor row

```yaml
- type: row
  x: 0
  y: 200
  width: 240
  height: 40
  gap: 0
  justify: space-evenly
  align: center
  children:
    - type: column
      gap: 0
      align: center
      children:
        - type: text
          text: "{{ states('sensor.cpu_temp') }}°"
          font: small
          bold: true
          color: text_primary
        - type: text
          text: "CPU"
          font: tiny
          color: text_tertiary
    - type: column
      gap: 0
      align: center
      children:
        - type: text
          text: "{{ states('sensor.memory_used') }}%"
          font: small
          bold: true
          color: text_primary
        - type: text
          text: "RAM"
          font: tiny
          color: text_tertiary
    - type: column
      gap: 0
      align: center
      children:
        - type: text
          text: "{{ states('sensor.disk_used') }}%"
          font: small
          bold: true
          color: text_primary
        - type: text
          text: "DISK"
          font: tiny
          color: text_tertiary
```

## Best Practices

- **Use `fullscreen` layout** with the Canvas widget for maximum space.
  The canvas fills the entire 240×240 display.
- **Prefer nested `row`/`column` layouts** over manually positioning every
  element — they handle spacing, alignment, and overflow more gracefully.
- **Wrap sets of related elements in `panel`** to create visual cards or
  sections.
- **Use semantic font sizes** (`primary`, `secondary`, `tertiary`) instead
  of names like `large` — they scale with the container automatically.
- **Use `x: 120` with `align: center`** to centre text horizontally.
- **Use `justify: space-evenly`** in rows/columns for evenly spaced content
  with equal gaps (reads better than `space-between` in most cells).
- **Minimum font size is 10–12px** for readability on the small display.
- **High-contrast colours** work best — light text on dark backgrounds.
- Prefer single-letter names for temporary templates where it makes the
  YAML more compact, but err on the side of clarity.
