"""
Render one SVG card per project into cards/, styled like the info card. The
README wraps each in a link, because an SVG shown via <img> can't hold its own.

Stars and the latest tag come from data/repos.json; the blurbs are hand-written
below. STATIC=1 emits the frozen state for previews.
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IN_PATH = os.path.join(HERE, "..", "data", "repos.json")
OUT_DIR = os.path.join(HERE, "..", "cards")
STATIC = bool(os.environ.get("STATIC"))

W, H = 420, 104
PAD = 20

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
SECTION = "#58a6ff"
GOLD = "#f2cc60"
GREEN = "#3fb950"

LANG_COLORS = {
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Python": "#3572a5",
    "Kotlin": "#a97bff",
    "Rust": "#dea584",
    "Dart": "#00b4ab",
    "HTML": "#e34c26",
    "Shell": "#89e051",
}

# ===========================================================================
#  EDIT THIS  -- (repo name, blurb). Keep blurbs under ~50 chars to fit.
# ===========================================================================
PROJECTS = [
    ("Tag-Team", "Dashboard for juggling Claude accounts"),
    ("duck-share", "LocalSend fork with NFC tap-to-share"),
    ("ONION", "Night & day VS Code theme system"),
    ("Onion-Lens", "Color picker & screenshot extension"),
    ("DARKMARK", "Dark Markdown preview for VS Code"),
    ("Forge", "Interactive dev environment setup CLI"),
]


def rise(inner):
    """fade + slight upward slide; freezes visible."""
    if STATIC:
        return f"<g>{inner}</g>"
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="0.1s" dur="0.5s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="0.1s" dur="0.5s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


def render(name, blurb, repo):
    lang = repo["language"] or "Other"
    color = LANG_COLORS.get(lang, MUTED)
    tag = repo["latest_release"]["tag"] if repo["latest_release"] else "no release"
    foot_y = H - 19
    stars = (f'<text x="{PAD+116}" y="{foot_y}" fill="{GOLD}" font-size="12">&#9733; '
             f'<tspan fill="{MUTED}">{repo["stars"]}</tspan></text>') if repo["stars"] else ""
    inner = (
        f'<text x="{PAD}" y="33" fill="{SECTION}" font-size="15" font-weight="700">{html.escape(name)}</text>'
        f'<text x="{PAD}" y="56" fill="{INK}" font-size="12.5">{html.escape(blurb)}</text>'
        f'<circle cx="{PAD+5}" cy="{foot_y-4}" r="5" fill="{color}"/>'
        f'<text x="{PAD+16}" y="{foot_y}" fill="{MUTED}" font-size="12">{html.escape(lang)}</text>'
        f'{stars}'
        f'<text x="{W-PAD}" y="{foot_y}" fill="{GREEN}" font-size="12" text-anchor="end">{html.escape(tag)}</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>'
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>'
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>'
        f'{rise(inner)}</svg>'
    )


if __name__ == "__main__":
    with open(IN_PATH) as f:
        repos = {r["name"]: r for r in json.load(f)["repos"]}
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, blurb in PROJECTS:
        with open(os.path.join(OUT_DIR, f"{name}.svg"), "w") as f:
            f.write(render(name, blurb, repos[name]))
    print("wrote", len(PROJECTS), "cards to", OUT_DIR)
