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
| `created` | str | ISO-8601 UTC, stamped once at first save; kept across edits *(optional)* |
| `updated` | str | ISO-8601 UTC, refreshed on every save *(optional)* |
| `author` | str | who recorded it; carried through the editor unchanged (not editable there) *(optional)* |
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
  "formula1": {
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
  "turn": "1",           // turn number (string; may be "1-2"); corner only
  "name": "Abbey",       // common name; optional on a corner, required otherwise
  "type": "corner",      // corner | straight | chicane | complex | other
  "start_m": 351,
  "end_m": 531,
  "apex_m": 429,         // optional apex (corner only), within the span
  "severity": "high",    // optional: low | medium | high (corner only)
  "overtake": "yes"      // optional: yes | no (corner / straight)
}
```

Fields are type-specific (this is what the editor shows and validates):

| Field | corner | chicane | complex | straight | other |
|---|:--:|:--:|:--:|:--:|:--:|
| `turn` | ✓ | – | – | – | – |
| `name` | optional | required | required | required | required |
| `apex_m` · `severity` | ✓ | – | – | – | – |
| `overtake` | ✓ | – | – | ✓ | – |
| `members` | – | optional | required | – | – |

**`chicane`** and **`complex`** are *grouping* types: they name a corner sequence and list
its corners by turn number in `members`; those member corners exist in their own right — the
group overlays them. A `complex` must list its members; a `chicane` may or may be a bare
named span like "Bus Stop".

> **Gear is not a section field.** Recommended gear is car-specific (an F1 car, F2 and a GT3
> take the same corner in different gears), whereas `sections` is shared car-agnostic
> geometry — so gear lives per class in `lines[car_class].gears`, not on a section. (Severity
> and overtake are roughly car-agnostic, so they stay on the shared section.)

```jsonc
{ "name": "Maggots and Becketts and Chapel", "type": "complex",
  "start_m": 3528, "end_m": 4296, "members": ["10", "11", "12", "13", "14"] }
```

> **DRS / override zones are not a section type.** DRS is regulation-specific (F1 25 / F2;
> the 2026 cars replace it with active aero + a manual override), whereas `sections` is
> shared, car-agnostic geometry. DRS/override zones therefore belong in a (planned) per-car-class
> profile layer, not here — see the SimRacingTelemetry roadmap's "Track profiles".
