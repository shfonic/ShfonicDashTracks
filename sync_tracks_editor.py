#!/usr/bin/env python3
"""
Vendor the browser track tools into the Shfonic Dash companion app.

The canonical tools live in this repo:

  * ``track_viewer.html``   — the track-map editor.
  * ``session_viewer.html`` — the session line viewer (overlays a driven
    session's laps on the racing line, with tap-to-zoom).

The Pythonista companion embeds each in a WebView, but Pythonista has no pip and
syncs only via iCloud, so it carries *vendored copies* — the same pattern the
dashboard repo uses for the shared ``sessionlog`` package.

This script owns those copies:

    python3 sync_tracks_editor.py            # copy the HTML over
    python3 sync_tracks_editor.py --check    # report drift, copy nothing (exit 1)

What is synced (each file -> <companion>/<same name>, with a sha256 recorded in
<companion>/track_tools.manifest.json).

Never edit the companion's copies by hand — change them here, re-sync, and
commit both repos.
"""

import argparse
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# The tools vendored into the companion, by filename (source == destination).
TOOLS = ('track_viewer.html', 'session_viewer.html')
DEST_MANIFEST = 'track_tools.manifest.json'

COMPANION = os.environ.get(
    'SHFONIC_COMPANION_DIR',
    os.path.expanduser(
        '~/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/'
        'Documents/ShfonicDashCompanion'))


def _sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def _drift():
    """Return ``{name: reason}`` for every vendored copy that differs from the
    canonical source, or an empty dict when all are in sync."""
    out = {}
    for name in TOOLS:
        dst = os.path.join(COMPANION, name)
        if not os.path.exists(dst):
            out[name] = 'missing'
        elif _sha256(dst) != _sha256(os.path.join(HERE, name)):
            out[name] = 'differs'
    return out


def sync():
    manifest = {}
    for name in TOOLS:
        src = os.path.join(HERE, name)
        shutil.copyfile(src, os.path.join(COMPANION, name))
        manifest[name] = _sha256(src)
        print(f'  {name}')
    with open(os.path.join(COMPANION, DEST_MANIFEST), 'w',
              encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write('\n')
    print(f'  {DEST_MANIFEST}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument('--check', action='store_true',
                    help='report drift between canonical and vendored copies '
                         'without writing anything (exit 1 on drift)')
    args = ap.parse_args()

    missing = [n for n in TOOLS if not os.path.isfile(os.path.join(HERE, n))]
    if missing:
        sys.exit('canonical tool(s) not found: ' + ', '.join(missing))
    if not os.path.isdir(COMPANION):
        sys.exit(f'companion app folder not found: {COMPANION}\n'
                 '(set SHFONIC_COMPANION_DIR to override)')

    if args.check:
        drift = _drift()
        if not drift:
            print('vendored track tools are in sync')
            return
        for name, reason in drift.items():
            print(f'  {name}: {reason}')
        sys.exit(1)

    print(f'syncing into {COMPANION}')
    sync()
    print('done — commit both repos')


if __name__ == '__main__':
    main()
