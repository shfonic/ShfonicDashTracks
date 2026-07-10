# Track map format

One JSON object per track, one file: `<game>_<track>.json` (slugged, lower-case), e.g.
`f1-25_silverstone.json`. Self-contained and dependency-free — you can consume these in
any project. Validate with `python3 validate.py <file>`.

Coordinates are **world metres** in a game-agnostic convention: **X / Z horizontal, Y up**
(elevation). Polylines are `[[x, z], …]`. Distances along the lap (`start_m`, `end_m`, …)
are metres from the start/finish line.

## Shape

Circuit geometry is **shared across car classes**; only the racing line is per class, so
it lives in a `lines` map keyed by car class.

| Key | Type | Notes |
|---|---|---|
| `format_version` | int | `1` |
| `game` | str | source game id, e.g. `f1_25` |
| `track` | str | track name, e.g. `Silverstone` |
| `game_track_length_m` | float | lap length reported by the game (sanity check) |
| `notes` | str | free-text notes for the whole track (e.g. "missing F2 line") |
| `left_edge` / `right_edge` | list | track edges, `[[x, z], …]` on a common distance grid *(shared)* |
| `pit_lane` | list | open polyline, pit entry → exit; empty if not recorded *(shared)* |
| `sf_line` | dict | `{"pos": [x, z], "heading": <radians>}` — the start/finish line *(shared)* |
| `sectors` | list | `[{"index", "pos": [x, z], "lap_dist_m"}]` — sector-boundary positions *(shared)* |
| `sections` | list | labelled corners / straights / complexes, see [below](#sections) *(shared)* |
| `lines` | dict | **per car class**, see [below](#lines) |

### `lines`

Each car class driven at the track gets one entry; classes nobody's driven simply aren't
present. A track is useful with just one.

```jsonc
"lines": {
  "formula1_2026": {
    "racing_line": [[x, z], …],   // the driven line, ~400 points, averaged over several laps
    "racing_attempts": 3,          // how many laps it was averaged from
    "gears": null,                 // suggested gear per line point — hand-filled, NOT recorded; null until set
    "notes": ""                    // free-text notes for this class's line
  }
}
```

**Gears are never captured live.** You drive slowly when recording to hold the line, so
the live gear would be wrong — the slot stays `null` until filled in by hand.

### `sections`

Labels for stretches of track, as distance spans in metres from S/F. A span **wraps across
S/F** when `start_m > end_m` (the main straight), and spans may overlap.

```jsonc
{
  "turn": "1",           // turn number (string; may be "1-2"); optional
  "name": "Abbey",       // common name; optional
  "type": "corner",      // corner | straight | chicane | complex | drs | other
  "start_m": 351,
  "end_m": 531,
  "apex_m": 429,         // optional apex (corner/chicane), within the span
  "gear": 3,             // optional
  "severity": "high",    // optional: low | medium | high
  "overtake": "yes"      // optional: yes | no
}
```

A **`complex`** groups a named corner sequence (e.g. *Maggots / Becketts / Chapel*). Its
span covers the whole group and it lists the corners it groups by turn number; the member
corners still exist as their own sections — the complex overlays them.

```jsonc
{ "name": "Maggots and Becketts and Chapel", "type": "complex",
  "start_m": 3528, "end_m": 4296, "members": ["10", "11", "12", "13", "14"] }
```
