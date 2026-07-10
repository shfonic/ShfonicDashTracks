#!/usr/bin/env python3
"""
Vendor the track-map editor into the Shfonic Dash companion app.

The canonical editor is `track_viewer.html` in this repo. The Pythonista
companion embeds it in a WebView (its offline track editor), but Pythonista
has no pip and syncs only via iCloud, so it carries a *vendored copy* — the
same pattern the dashboard repo uses for the shared `sessionlog` package.

This script owns that copy:

    python3 sync_tracks_editor.py            # copy the HTML over
    python3 sync_tracks_editor.py --check    # report drift, copy nothing (exit 1)

What is synced:
  track_viewer.html  -> <companion>/track_viewer.html
  a sha256 is recorded in <companion>/track_viewer.manifest.json

Never edit the companion's track_viewer.html by hand — change it here,
re-sync, and commit both repos.
"""

import argparse
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, 'track_viewer.html')

COMPANION = os.environ.get(
    'SHFONIC_COMPANION_DIR',
    os.path.expanduser(
        '~/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/'
        'Documents/ShfonicDashCompanion'))

DEST_HTML     = 'track_viewer.html'
DEST_MANIFEST = 'track_viewer.manifest.json'


def _sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def _drift():
    """Return a reason string if the vendored copy differs, else None."""
    dst = os.path.join(COMPANION, DEST_HTML)
    if not os.path.exists(dst):
        return 'missing'
    if _sha256(dst) != _sha256(SOURCE):
        return 'differs'
    return None


def sync():
    dst = os.path.join(COMPANION, DEST_HTML)
    shutil.copyfile(SOURCE, dst)
    print(f'  {DEST_HTML}')
    manifest = {'track_viewer.html': _sha256(SOURCE)}
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

    if not os.path.isfile(SOURCE):
        sys.exit(f'canonical editor not found: {SOURCE}')
    if not os.path.isdir(COMPANION):
        sys.exit(f'companion app folder not found: {COMPANION}\n'
                 '(set SHFONIC_COMPANION_DIR to override)')

    if args.check:
        reason = _drift()
        if not reason:
            print('vendored track_viewer.html is in sync')
            return
        print(f'  track_viewer.html: {reason}')
        sys.exit(1)

    print(f'syncing into {COMPANION}')
    sync()
    print('done — commit both repos')


if __name__ == '__main__':
    main()
