"""
Build tagline.svg (and tagline-light.svg for light-mode GitHub): a transparent
banner that types each line in turn, holds it, wipes it, and loops. Uses the same
SMIL clip wipe as make_ascii_svg.py, since JS doesn't run in an <img> SVG.

Static content; rerun by hand after editing LINES. STATIC=1 emits the first line
frozen for previews.
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = bool(os.environ.get("STATIC"))

W, H = 860, 40
FONT_SIZE = 15
CHAR_W = 9           # forced with textLength, so widths are font-independent
BASELINE = 26

LINE_DUR = 3.6       # seconds per line, including type and wipe
TYPE_END = 0.35      # fraction of a line's slot spent typing
HOLD_END = 0.92      # fraction at which the wipe starts

THEMES = {"tagline.svg": "#c9d1d9", "tagline-light.svg": "#1f2328"}

# ===========================================================================
#  EDIT THIS
# ===========================================================================
LINES = [
    "May the almighty source code be with you.",
    "Now building: Forge · Tag-Team · duck-share",
    "Shipping ONION, Onion-Lens and DARKMARK",
    "TypeScript · Kotlin · Python · Rust",
]


def timeline(i, n, closed, opened):
    """values/keyTimes for line i of n: closed -> opened -> hold -> closed."""
    start = i / n
    points = [(0, closed), (start, closed), (start + TYPE_END / n, opened),
              (start + HOLD_END / n, opened), ((i + 1) / n, closed), (1, closed)]
    # first/last lines already sit on 0 and 1, so drop the duplicate key time
    points = [p for j, p in enumerate(points) if j == 0 or p[0] > points[j - 1][0]]
    return (";".join(f"{v:g}" for _, v in points),
            ";".join(f"{t:.4f}" for t, _ in points))


def render(ink):
    period = LINE_DUR * len(LINES)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">']
    for i, line in enumerate(LINES):
        width = len(line) * CHAR_W
        x = (W - width) / 2
        text = (f'<text xml:space="preserve" x="{x}" y="{BASELINE}" fill="{ink}" font-size="{FONT_SIZE}" '
                f'textLength="{width}" lengthAdjust="spacing">{html.escape(line)}</text>')
        if STATIC:
            if i == 0:
                parts.append(text)
            continue
        vals, keys = timeline(i, len(LINES), 0, width)
        anim = f'keyTimes="{keys}" dur="{period}s" repeatCount="indefinite"'
        parts.append(f'<clipPath id="l{i}"><rect x="{x}" y="0" height="{H}" width="0">'
                     f'<animate attributeName="width" values="{vals}" {anim}/></rect></clipPath>')
        parts.append(f'<g clip-path="url(#l{i})">{text}</g>')
        cursor_vals = ";".join(f"{x + float(v):g}" for v in vals.split(";"))
        cursor_opacity = ";".join("0" if float(v) == 0 else "1" for v in vals.split(";"))
        parts.append(f'<rect y="{BASELINE-13}" width="8" height="16" fill="{ink}" opacity="0">'
                     f'<animate attributeName="x" values="{cursor_vals}" {anim}/>'
                     f'<animate attributeName="opacity" values="{cursor_opacity}" {anim}/></rect>')
    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    for name, ink in THEMES.items():
        with open(os.path.join(HERE, "..", name), "w") as f:
            f.write(render(ink))
    print("wrote", ", ".join(THEMES))
