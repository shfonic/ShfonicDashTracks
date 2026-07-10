#!/usr/bin/env python3
"""Validate every track map in tracks/ against the Shfonic Dash track format.

Pure standard library, no dependencies — run locally or in CI:

    python3 validate.py            # validate tracks/
    python3 validate.py path/…     # validate specific files/dirs

Exits non-zero if any file fails. See track-format.md for the schema.
"""
import glob
import json
import math
import os
import re
import sys

_FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*\.json$")
# DRS/override zones are regulation-specific (F1 25/F2 have DRS; 2026 uses
# active-aero + override), so they belong in a future per-class profile, not the
# shared, car-agnostic sections list.
_SECTION_TYPES = {"corner", "straight", "chicane", "complex", "other"}
# Grouping types describe a sequence of corners via a `members` turn list rather
# than carrying their own turn/gear/apex.
_GROUPING_TYPES = {"chicane", "complex"}


def _is_xy(p):
    return (isinstance(p, (list, tuple)) and len(p) == 2
            and all(isinstance(v, (int, float)) and math.isfinite(v) for v in p))


def _check_line(errs, where, pts):
    if not isinstance(pts, list):
        errs.append(f"{where}: must be a list of [x, z] points")
        return
    for i, p in enumerate(pts):
        if not _is_xy(p):
            errs.append(f"{where}[{i}]: not a finite [x, z] pair: {p!r}")
            break


def _check_sections(errs, sections):
    if not isinstance(sections, list):
        errs.append("sections: must be a list")
        return
    turns = {str(s.get("turn")) for s in sections
             if isinstance(s, dict) and s.get("turn") is not None}
    for i, s in enumerate(sections):
        at = f"sections[{i}]"
        if not isinstance(s, dict):
            errs.append(f"{at}: must be an object")
            continue
        typ = s.get("type", "other")
        if typ not in _SECTION_TYPES:
            errs.append(f"{at}: unknown type {typ!r} (allowed: {sorted(_SECTION_TYPES)})")
        for k in ("start_m", "end_m"):
            if not isinstance(s.get(k), (int, float)):
                errs.append(f"{at}: {k} must be a number")
        if s.get("apex_m") is not None and not isinstance(s["apex_m"], (int, float)):
            errs.append(f"{at}: apex_m must be a number or absent")
        if typ in _GROUPING_TYPES:
            members = s.get("members")
            # A complex is defined by the corners it groups, so it must list
            # them. A chicane may list its member corners (to carry their gear)
            # but a bare named chicane (e.g. "Bus Stop") is fine too.
            if typ == "complex" and (not isinstance(members, list) or not members):
                errs.append(f"{at}: a complex needs a non-empty members list")
            if isinstance(members, list):
                for m in members:
                    if str(m) not in turns:
                        errs.append(f"{at}: member {m!r} has no matching corner turn")


def _check_lines(errs, lines):
    if not isinstance(lines, dict):
        errs.append("lines: must be an object keyed by car_class")
        return
    if not lines:
        errs.append("lines: empty — a v2 track needs at least one class line")
    for cls, ln in lines.items():
        at = f"lines[{cls!r}]"
        if not isinstance(ln, dict):
            errs.append(f"{at}: must be an object")
            continue
        _check_line(errs, f"{at}.racing_line", ln.get("racing_line", []))
        if not isinstance(ln.get("racing_attempts", 0), int):
            errs.append(f"{at}: racing_attempts must be an int")
        g = ln.get("gears")
        if g is not None and not isinstance(g, list):
            errs.append(f"{at}: gears must be null or a list")
        if not isinstance(ln.get("notes", ""), str):
            errs.append(f"{at}: notes must be a string")


def validate_file(path):
    """Return a list of error strings ([] if the file is a valid track map)."""
    errs = []
    name = os.path.basename(path)
    if not _FILENAME_RE.match(name):
        errs.append(f"filename {name!r} must be <game>_<track>.json (lower-case, [a-z0-9_-])")
    try:
        with open(path, "rb") as f:
            obj = json.loads(f.read())
    except (OSError, ValueError) as e:
        return [f"not valid JSON: {e}"]
    if not isinstance(obj, dict):
        return ["top level must be a JSON object"]

    if obj.get("format_version") != 1:
        errs.append(f"format_version must be 1 (got {obj.get('format_version')!r})")
    for k in ("game", "track"):
        if not isinstance(obj.get(k), str) or not obj.get(k):
            errs.append(f"{k}: required non-empty string")

    for k in ("left_edge", "right_edge", "pit_lane"):
        if k in obj:
            _check_line(errs, k, obj[k])

    if "lines" in obj:
        _check_lines(errs, obj["lines"])
    elif not (obj.get("left_edge") or obj.get("right_edge") or obj.get("sections")):
        errs.append("no geometry: need lines, edges, or sections")

    if "sections" in obj:
        _check_sections(errs, obj["sections"])

    if "notes" in obj and not isinstance(obj["notes"], str):
        errs.append("notes: must be a string")

    # Optional provenance metadata (absent on pre-metadata maps).
    for k in ("created", "updated", "author"):
        if k in obj and not isinstance(obj[k], str):
            errs.append(f"{k}: must be a string")
    return errs


def main(argv):
    targets = argv[1:] or ["tracks"]
    files = []
    for t in targets:
        if os.path.isdir(t):
            files += sorted(glob.glob(os.path.join(t, "**", "*.json"), recursive=True))
        else:
            files.append(t)
    if not files:
        print("No track files found.")
        return 0

    failed = 0
    for path in files:
        errs = validate_file(path)
        if errs:
            failed += 1
            print(f"FAIL  {path}")
            for e in errs:
                print(f"        - {e}")
        else:
            print(f"ok    {path}")
    print(f"\n{len(files)} file(s), {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
