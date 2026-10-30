"""Check the marker replacement, since it rewrites README.md unattended in CI."""
from update_readme_releases import END, START, releases_table, replace_block


def repo(name, date):
    rel = {"tag": "v1", "date": date, "url": "https://x/r"}
    return {"name": name, "url": "https://x", "latest_release": rel}


def test_replace_keeps_surrounding_text_and_is_idempotent():
    text = f"before\n{START}\nold\n{END}\nafter\n"
    once = replace_block(text, "new")
    assert once == f"before\n{START}\nnew\n{END}\nafter\n"
    assert replace_block(once, "new") == once


def test_missing_or_swapped_markers_raise():
    for bad in ("no markers", f"{END} {START}", f"{START} {START} {END}"):
        try:
            replace_block(bad, "new")
        except ValueError:
            continue
        raise AssertionError(f"accepted: {bad!r}")


def test_table_is_newest_first_and_skips_unreleased():
    repos = [repo("old", "2026-01-01"), repo("new", "2026-02-01"),
             {"name": "none", "url": "https://x", "latest_release": None}]
    table = releases_table(repos)
    assert table.index("[new]") < table.index("[old]")
    assert "none" not in table


if __name__ == "__main__":
    test_replace_keeps_surrounding_text_and_is_idempotent()
    test_missing_or_swapped_markers_raise()
    test_table_is_newest_first_and_skips_unreleased()
    print("ok")
