"""
Rewrite the block between the releases markers in README.md with the newest
releases across all repos, from data/repos.json. A real markdown table, so the
links work and CI can refresh it daily.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IN_PATH = os.path.join(HERE, "..", "data", "repos.json")
README = os.path.join(HERE, "..", "README.md")

START = "<!-- releases:start -->"
END = "<!-- releases:end -->"
COUNT = 5


def replace_block(text, block):
    """Swap the text between the markers; refuse to guess if they're missing."""
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        raise ValueError("README needs exactly one releases start/end marker pair, in order")
    head = text[:text.index(START) + len(START)]
    tail = text[text.index(END):]
    return f"{head}\n{block}\n{tail}"


def releases_table(repos):
    released = [r for r in repos if r["latest_release"]]
    released.sort(key=lambda r: r["latest_release"]["date"], reverse=True)
    rows = ["", "| Project | Release | Date |", "| :--- | :--- | :--- |"]
    for r in released[:COUNT]:
        rel = r["latest_release"]
        rows.append(f"| [{r['name']}]({r['url']}) | [{rel['tag']}]({rel['url']}) | {rel['date']} |")
    rows.append("")
    return "\n".join(rows)


if __name__ == "__main__":
    with open(IN_PATH) as f:
        repos = json.load(f)["repos"]
    with open(README) as f:
        text = f.read()
    try:
        updated = replace_block(text, releases_table(repos))
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    with open(README, "w") as f:
        f.write(updated)
    print("updated releases in", README)
