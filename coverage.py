#!/usr/bin/env python3
"""Print the coverage table for tracks/ as GitHub-flavoured Markdown.

    python3 coverage.py            # print the table
    python3 coverage.py --write    # splice it into README.md between the markers

Shows, per track, which car-class lines exist and whether pit lane, sections
and gears are filled — so contributors can see the gaps at a glance.
"""
import glob
import json
import os
import sys

START = "<!-- COVERAGE:START -->"
END = "<!-- COVERAGE:END -->"


def _yn(v):
    return "✅" if v else "—"


def rows():
    out = []
    for path in sorted(glob.glob("tracks/**/*.json", recursive=True)):
        try:
            d = json.load(open(path))
        except (OSError, ValueError):
            continue
        lines = d.get("lines")
        if not isinstance(lines, dict):                 # v1 fallback
            lines = ({d.get("car_class") or "default": {"racing_line": d.get("racing_line") or [],
                                                        "gears": None}}
                     if d.get("racing_line") else {})
        classes = sorted(lines)
        # sections is shared/car-agnostic (see track-format.md), so every class
        # sees the same count; gears is per class, so it's looked up per class.
        sections = len(d.get("sections") or [])
        out.append({
            "game": d.get("game", "?"),
            "track": d.get("track", os.path.basename(path)),
            "classes": classes,
            "pit": bool(d.get("pit_lane")),
            "sections": sections,
            "gears_by_class": {c: bool(lines[c].get("gears")) for c in classes},
            "notes": (d.get("notes") or "").strip(),
        })
    out.sort(key=lambda r: (r["game"], r["track"].lower()))
    return out


def table():
    lines = ["| Game | Track | Class lines | Pit | Sections | Gears | Notes |",
             "|---|---|---|:--:|:--:|:--:|---|"]
    for r in rows():
        classes = r["classes"]
        classes_cell = ", ".join(classes) or "—"
        if classes:
            sections_cell = str(r['sections'] or "—")   # shared across classes — show once
            gears_cell = "<br>".join(f"{c}: {_yn(r['gears_by_class'][c])}" for c in classes)
        else:
            sections_cell = "—"
            gears_cell = "—"
        lines.append(f"| {r['game']} | {r['track']} | {classes_cell} | "
                     f"{_yn(r['pit'])} | {sections_cell} | {gears_cell} | "
                     f"{r['notes'] or ''} |")
    return "\n".join(lines)


def main(argv):
    md = table()
    if "--write" in argv and os.path.exists("README.md"):
        text = open("README.md").read()
        if START in text and END in text:
            pre, rest = text.split(START, 1)
            _, post = rest.split(END, 1)
            open("README.md", "w").write(f"{pre}{START}\n{md}\n{END}{post}")
            print("README.md coverage table updated.")
            return 0
        print("README.md is missing the COVERAGE markers.", file=sys.stderr)
        return 1
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
