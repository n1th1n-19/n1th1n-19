#!/usr/bin/env python3
"""
Fetch public, non-fork repos plus their latest release over GraphQL and write
data/repos.json, consumed by render_project_cards.py, render_stats.py and
update_readme_releases.py. Run daily by .github/workflows/update-profile-art.yml.

Needs GITHUB_TOKEN. A bad response exits non-zero, so a failed fetch never
overwrites good data.
"""
import datetime
import json
import os
import sys

import requests

USERNAME = os.environ.get("GH_PROFILE_USER", "YOUR_GITHUB_USERNAME")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "repos.json")

# ponytail: first page only, add pageInfo pagination past 100 repos
QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 100, privacy: PUBLIC, ownerAffiliations: OWNER, isFork: false,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name
        description
        url
        stargazerCount
        pushedAt
        primaryLanguage { name }
        releases(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
          totalCount
          nodes { tagName publishedAt url }
        }
      }
    }
  }
}
"""


def fetch_repos():
    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY, "variables": {"login": USERNAME}},
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"},
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()
    if body.get("errors") or not body.get("data", {}).get("user"):
        print(f"graphql error: {body.get('errors')}", file=sys.stderr)
        sys.exit(1)
    return body["data"]["user"]["repositories"]["nodes"]


def clean(node):
    latest = node["releases"]["nodes"][0] if node["releases"]["nodes"] else None
    return {
        "name": node["name"],
        "description": node["description"],
        "url": node["url"],
        "stars": node["stargazerCount"],
        "language": (node["primaryLanguage"] or {}).get("name"),
        "pushed_at": node["pushedAt"],
        "releases_total": node["releases"]["totalCount"],
        "latest_release": latest and {
            "tag": latest["tagName"],
            "date": latest["publishedAt"][:10],
            "url": latest["url"],
        },
    }


if __name__ == "__main__":
    nodes = fetch_repos()
    if not nodes:
        print("no repos returned", file=sys.stderr)
        sys.exit(1)
    repos = [clean(n) for n in nodes]
    data = {
        "username": USERNAME,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repos": repos,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {OUT_PATH}: {len(repos)} repos")
