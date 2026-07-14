# Shfonic Dash — Track Maps

Community circuit maps for [Shfonic Dash](https://shfonic.com/dash/index.html), the
sim-racing telemetry dashboard. Each file describes one track — its edges, racing
line(s), pit lane, sector boundaries and labelled corners — as plain JSON in world
metres, recorded by driving the circuit in-game.

They're **free to use in your own projects too** (see [License](#license)). The format is
documented in **[track-format.md](track-format.md)** so it can stand on its own as a small
open data set, independent of any one app.

## Coverage

Which tracks exist and what's filled in. `—` = not done yet — **contributions welcome**
(see [CONTRIBUTING.md](CONTRIBUTING.md)). Regenerate this table with `python3 coverage.py --write`.

<!-- COVERAGE:START -->
| Game | Track | Class lines | Pit | Sections | Gears | Notes |
|---|---|---|:--:|:--:|:--:|---|
| f1_25 | Abu Dhabi | f2, formula1, formula1_2026 | ✅ | 17 | f2: —<br>formula1: —<br>formula1_2026: — |  |
| f1_25 | Hungaroring | f2, formula1, formula1_2026 | ✅ | 15 | f2: —<br>formula1: —<br>formula1_2026: — |  |
| f1_25 | Imola | f2, formula1, formula1_2026 | ✅ | 19 | f2: —<br>formula1: —<br>formula1_2026: — |  |
| f1_25 | Madrid | f2, formula1, formula1_2026 | ✅ | 26 | f2: —<br>formula1: —<br>formula1_2026: — |  |
| f1_25 | Melbourne | f2, formula1, formula1_2026 | ✅ | 17 | f2: —<br>formula1: —<br>formula1_2026: — |  |
| f1_25 | Red Bull Ring | f2, formula1, formula1_2026 | ✅ | 13 | f2: —<br>formula1: —<br>formula1_2026: — |  |
| f1_25 | Shanghai | f2, formula1, formula1_2026 | ✅ | 18 | f2: —<br>formula1: —<br>formula1_2026: — |  |
| f1_25 | Silverstone | f2, formula1, formula1_2026 | ✅ | 23 | f2: —<br>formula1: —<br>formula1_2026: — |  |
| f1_25 | Spa | f2, formula1, formula1_2026 | ✅ | 22 | f2: —<br>formula1: —<br>formula1_2026: — |  |
<!-- COVERAGE:END -->

Circuit geometry (edges, pit, sectors, corner labels) is **shared across car classes**;
the racing line **and its gears** are held per class in a `lines` map. In the **F1 titles
the lines are near-identical** — F1 and F2 differ by under a metre (recording noise) — but
the **gears differ** (the 2026 cars super-clip to a lower gear at some corners to recharge
the battery), so each class (`formula1`, `formula1_2026`, `f2`) is its **own profile**:
the line copied across, the gears filled in per class. Games with genuine class variety
(e.g. GT3 vs a road car) get a genuinely distinct line per class too. A track just needs
*one* class profile to be useful — the rest can follow.

> **Position feed:** recording needs world-position telemetry, which today only
> **F1 25 / F1 26** broadcast, so tracks are F1 for now. Other games slot in as their
> position support lands.

## Accuracy & provenance

These maps are recorded and labelled **by hand, on best visual judgement** — driving to
stay close to the track edges, following the on-screen racing line, and placing the
sections (corners, straights, complexes) by eye, **not to any official specification or
data source**. So expect some errors and inconsistencies: an edge that drifts, a corner
span that's a little off, a turn number someone would argue with.

That's fine — they're a starting point. **Corrections are very welcome, and you're free to
change them or record your own.** If you spot something wrong, open a PR or a note in the
file's `notes`.

## Using these in Shfonic Dash

Drop the JSON files into the app's `tracks/` directory (or sync them over the app's LAN
`/tracks` API). Filenames are `<game>_<track>.json` (slugged), e.g.
`f1-25_silverstone.json` — the app matches a map to the track you're on by game + name.

## Using these in your own product

Everything you need is in **[track-format.md](track-format.md)**: coordinates are world
metres (X/Z horizontal, Y up), lines are `[[x, z], …]`, and the file is one self-contained
JSON object. No app-specific dependencies. Validate any file with:

```bash
python3 validate.py tracks/f1-25_silverstone.json
```

## Map utility

**`track_viewer.html`** is a standalone, offline browser tool (no build, no server — just
open it) for viewing a track, switching between each car class's racing line, labelling
corners / straights / complexes, and editing notes and gears. Open a track file, edit,
then **Download** to get a ready-to-commit `<game>_<track>.json`.

The same file doubles as the **embedded editor in the Shfonic Dash companion app**: it
exposes a small `window.SHFONIC` bridge (`load` / `export` / `filename` / `isDirty`) that a
native WebView drives instead of the file picker and download button. This has no effect
when you just open the file in a browser — it still loads and downloads as normal.

**`session_viewer.html`** is the read-only companion tool: it overlays a driven session's
laps on the racing line so you can see where you ran wide, toggle individual laps on and
off, and **tap the map to zoom into a corner** (double-tap to fit). It reuses the editor's
projection, pan/zoom and theme. The companion bakes a session's data in via the same
`window.SHFONIC` bridge (`SHFONIC.load(data)`, where `data` is
`sessionlog.lines.session_line_export(...)`); opened directly in a browser it instead takes
a track JSON + a session CSV via the two file buttons, so you can inspect a session pulled
off the Pi. Both HTML tools are vendored into the companion by `sync_tracks_editor.py`.

## Contributing

Record a track in Shfonic Dash, then open a PR adding the `.json`. CI runs `validate.py`
on every file, so anything malformed is caught automatically. Full workflow in
**[CONTRIBUTING.md](CONTRIBUTING.md)**.

## License

Released under **[CC BY 4.0](LICENSE)** — free to use, share and adapt, including in
commercial products, **as long as you give credit**. These are original coordinate
recordings, not game assets.

If you use these maps, please attribute them — for example:

> Track maps from **Shfonic Dash Track Maps**
> (https://github.com/shfonic/ShfonicDashTracks) © Richard Hawes and contributors,
> licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

A link back in your docs, credits screen, or about page is enough.
