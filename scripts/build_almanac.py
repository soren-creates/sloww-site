#!/usr/bin/env python3
"""
Pre-render the Almanac page and the footer version line from releases.json.

Run whenever releases.json changes (alongside scripts/whats_new.py):

    python3 scripts/build_almanac.py

Writes static HTML between the <!-- RELEASES:START/END --> markers in
almanac/index.html and the <!-- VERSION:START/END --> markers in index.html, so
the content is fully crawlable — no client-side fetch, no "Loading…" for bots.
Idempotent: safe to run repeatedly.
"""
import json
import pathlib
import re
from datetime import date as Date

ROOT = pathlib.Path(__file__).resolve().parent.parent
releases = json.loads((ROOT / "releases.json").read_text())["releases"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def fmt_full(iso):
    d = Date.fromisoformat(iso)
    return f"{d:%B} {d.day}, {d.year}"


def fmt_month(iso):
    d = Date.fromisoformat(iso)
    return f"{d:%B} {d.year}"


def render_release(rel):
    feats = [f for f in rel["features"] if f.get("store", True)]
    items = "\n".join(
        f'            <li><span class="f-title">{esc(f["title"])}.</span> '
        f'{esc(f.get("blurb") or f["description"])}</li>'
        for f in feats
    )
    note = (
        f'\n          <p class="release-note">{esc(rel["note"])}</p>'
        if rel.get("note")
        else ""
    )
    return f"""        <section class="release">
          <div class="release-head">
            <h2>Version {esc(rel["version"])}</h2>
            <span class="release-date">{fmt_full(rel["date"])}</span>
          </div>
          <p class="release-tagline">{esc(rel["tagline"])}</p>
          <ul class="release-features">
{items}
          </ul>{note}
        </section>"""


def replace_between(text, start_re, end_marker, inner, *, block):
    """Replace text between a start-marker regex and a literal end marker.
    Uses a function replacement so HTML in `inner` is treated literally."""
    pattern = re.compile(rf"({start_re}).*?({re.escape(end_marker)})", re.DOTALL)
    if not pattern.search(text):
        raise SystemExit(f"Markers not found (…{end_marker})")
    if block:
        return pattern.sub(lambda m: f"{m.group(1)}\n{inner}\n    {m.group(2)}", text, count=1)
    return pattern.sub(lambda m: f"{m.group(1)}{inner}{m.group(2)}", text, count=1)


# 1) Almanac page — pre-render all release entries
almanac_path = ROOT / "almanac" / "index.html"
releases_html = "\n".join(render_release(r) for r in releases)
almanac_path.write_text(
    replace_between(
        almanac_path.read_text(),
        r"<!-- RELEASES:START.*?-->", "<!-- RELEASES:END -->",
        releases_html, block=True,
    )
)

# 2) Home-page footer version line — from the latest release
latest = releases[0]
version_html = (
    f'Currently v{esc(latest["version"])} · {fmt_month(latest["date"])} '
    f'· <a href="almanac/">what’s changed</a>'
)
index_path = ROOT / "index.html"
index_path.write_text(
    replace_between(
        index_path.read_text(),
        r"<!-- VERSION:START.*?-->", "<!-- VERSION:END -->",
        version_html, block=False,
    )
)

print(f"Built Almanac ({len(releases)} releases) and footer version line (v{latest['version']}).")
