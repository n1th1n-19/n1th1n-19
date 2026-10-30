"""
Render stats.svg from data/repos.json: stars, repos, releases, and a top-languages
bar. Sits above the heatmap, which already covers streaks and contribution totals,
so none of those repeat here. STATIC=1 emits the frozen state for previews.
"""
import html
import json
import os
from collections import Counter

from render_project_cards import BG, BG2, FRAME, INK, LANG_COLORS, MUTED, SECTION

HERE = os.path.dirname(os.path.abspath(__file__))
IN_PATH = os.path.join(HERE, "..", "data", "repos.json")
OUT_PATH = os.path.join(HERE, "..", "stats.svg")
STATIC = bool(os.environ.get("STATIC"))

W, H = 869, 134      # same width as the heatmap
PAD = 22
BAR_Y = 76
BAR_H = 10
TOP_LANGS = 6
OTHER = "#484f58"
CHAR_W = 7.3         # approx mono advance at font-size 12


def tile(x, label, value):
    return (f'<text x="{x}" y="34" fill="{MUTED}" font-size="12">{html.escape(label)}</text>'
            f'<text x="{x}" y="58" fill="{INK}" font-size="18" font-weight="700">{html.escape(str(value))}</text>')


def lang_bar(repos):
    counts = Counter(r["language"] for r in repos if r["language"])
    top = counts.most_common(TOP_LANGS)
    rest = sum(counts.values()) - sum(n for _, n in top)
    if rest:
        top.append(("Other", rest))
    total = sum(n for _, n in top)

    parts = [f'<clipPath id="bar"><rect x="{PAD}" y="{BAR_Y}" height="{BAR_H}" rx="5" width="{W - PAD*2 if STATIC else 0}">']
    if not STATIC:
        parts.append(f'<animate attributeName="width" from="0" to="{W - PAD*2}" begin="0.2s" dur="1s" '
                     f'fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>')
    parts.append('</rect></clipPath><g clip-path="url(#bar)">')

    x = PAD
    legend = []
    for lang, n in top:
        width = (W - PAD * 2) * n / total
        color = LANG_COLORS.get(lang, OTHER)
        parts.append(f'<rect x="{x:.1f}" y="{BAR_Y}" width="{width + 0.5:.1f}" height="{BAR_H}" fill="{color}"/>')
        x += width
        legend.append((lang, color, round(100 * n / total)))
    parts.append("</g>")

    labels = [f"{lang} {pct}%" for lang, _, pct in legend]
    widths = [16 + len(label) * CHAR_W for label in labels]
    gap = (W - PAD * 2 - sum(widths)) / max(len(legend) - 1, 1)
    lx = PAD
    for (_, color, _), label, width in zip(legend, labels, widths):
        parts.append(f'<circle cx="{lx + 5:.1f}" cy="{BAR_Y + 30}" r="5" fill="{color}"/>'
                     f'<text x="{lx + 16:.1f}" y="{BAR_Y + 34}" fill="{MUTED}" font-size="12">'
                     f'{html.escape(label)}</text>')
        lx += width + gap
    return "".join(parts)


def render(repos):
    released = [r for r in repos if r["latest_release"]]
    newest = max(released, key=lambda r: r["latest_release"]["date"])
    tiles = [
        ("Stars", sum(r["stars"] for r in repos)),
        ("Public repos", len(repos)),
        ("Releases shipped", sum(r["releases_total"] for r in repos)),
        ("Last release", f'{newest["name"]} {newest["latest_release"]["tag"]}'),
    ]
    xs = [PAD, PAD + 130, PAD + 300, PAD + 490]
    body = "".join(tile(x, label, value) for x, (label, value) in zip(xs, tiles))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>'
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>'
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>'
        f'{body}{lang_bar(repos)}</svg>'
    )


if __name__ == "__main__":
    with open(IN_PATH) as f:
        data = json.load(f)
    with open(OUT_PATH, "w") as f:
        f.write(render(data["repos"]))
    print("wrote", OUT_PATH)
