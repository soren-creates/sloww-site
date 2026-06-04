# Releases — one source, three destinations

The goal: **write each release's "what's changed" once.** Everything else derives
from it, so the in-app screen, the App Store listing, and the website never drift.

## Source of truth

[`releases.json`](releases.json) holds the curated, user-facing highlights for each
version (version, date, theme, tagline, features). It mirrors `VersionUpdate.history`
in the app (`ios/Sloww/Sloww/Utilities/VersionUpdate.swift`).

> This is the *curated* list, not the exhaustive engineering changelog. The full
> per-commit log still lives in the app repo's `docs/release-notes.md`; only the
> highlights worth showing a human belong here.

### A feature's shape — two voices, one entry

The App Store and the in-app "What's Changed" moment genuinely want different
registers (the store sells with specifics; the in-app moment is warm and complete).
So each feature can carry **both**, written once:

```json
{
  "title": "StandBy Widgets",
  "description": "Three bedside clocks for iPhone's StandBy mode: a minimal dial, a countdown to the next light transition, and tonight's moon phase.",
  "blurb": "Three new widgets for your nightstand. The clock keeps watch while you sleep.",
  "store": true
}
```

- **`description`** — the specific, App-Store-quality line. Required.
- **`blurb`** — the warm, in-app line. Optional; falls back to `description`.
- **`store`** — set `false` for in-app-only changes (minor tweaks rolled into the
  closing `note`). Defaults to `true`.

Who reads what:

| Surface | Features shown | Voice |
|---|---|---|
| App Store (`whats_new.py`) | `store !== false` | `description` |
| In-app "What's Changed" | all | `blurb` ?? `description` |
| Website Almanac | `store !== false` | `blurb` ?? `description` |

(The Almanac uses the warm `blurb` to match the site's voice; to make it read like
the store instead, change `f.get("blurb") or f["description"]` to `f["description"]`
in `scripts/build_almanac.py`.)

## The flow

```
releases.json
   ├─→ in-app "What's Changed"   VersionUpdate decodes it (see note below)
   ├─→ App Store "What's New"     python3 scripts/whats_new.py     → paste / fastlane
   └─→ website Almanac + footer    python3 scripts/build_almanac.py → static HTML
```

### Per release, you do one thing
Add a new entry to the top of `releases.json`. Then:

1. **App Store** — run `python3 scripts/whats_new.py` and paste the output into
   App Store Connect → "What's New in This Version" (or drop it into
   `fastlane/metadata/en-US/release_notes.txt`).
2. **Website** — run `python3 scripts/build_almanac.py` to regenerate the Almanac
   page and the footer version line as static HTML, then commit.
3. **In-app** — nothing to write; see below.

## Making the app read the same file (recommended)

Today `VersionUpdate.history` is a hard-coded Swift array — a *fourth* place the copy
lives. To collapse it into the single source, have `VersionUpdate` **decode
`releases.json`** instead of hard-coding the array:

- Bundle `releases.json` into the app target (or fetch `https://sloww.app/releases.json`
  with the bundled copy as offline fallback).
- Map `features[].title/description` onto `VersionUpdate.Feature`. SF Symbols aren't in
  the JSON (the web can't use them), so keep a small `title → symbol` lookup in Swift,
  or add an optional `"symbol"` field to each feature in `releases.json`.

Until that refactor lands, keep `releases.json` and `VersionUpdate.history` in sync by
hand — but the website and App Store are already single-sourced from `releases.json`.

## Why not auto-pull from the App Store instead?

The iTunes Lookup API (`itunes.apple.com/lookup?id=6759274049`) returns only the
*current* version's notes — no history — so it can't power a full Almanac. Driving
everything *from* `releases.json` gives full history and keeps the app, the store,
and the site reading the same words.
