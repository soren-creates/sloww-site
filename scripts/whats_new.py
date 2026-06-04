#!/usr/bin/env python3
"""
Generate App Store "What's New" text from releases.json — the single source of truth.

Usage:
    python3 scripts/whats_new.py            # latest version
    python3 scripts/whats_new.py 1.1        # a specific version

Paste the output into App Store Connect's "What's New in This Version",
or wire it into fastlane (metadata/<lang>/release_notes.txt). The website
Almanac and the in-app What's Changed read the same releases.json, so the
copy is written exactly once.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "releases.json").read_text())
releases = data["releases"]

version = sys.argv[1] if len(sys.argv) > 1 else releases[0]["version"]
rel = next((r for r in releases if r["version"] == version), None)
if rel is None:
    sys.exit(f"Version {version} not found in releases.json")

# App Store "What's New" format: uppercase feature heading, its description,
# a blank line between each, then the closing "Plus ..." note.
# Features flagged "store": false are in-app only (rolled into the note), so skip them.
for f in rel["features"]:
    if not f.get("store", True):
        continue
    print(f["title"].upper())
    print(f["description"])
    print()
note = rel.get("note")
if note:
    print(note)
