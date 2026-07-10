# Contributing a track

Thanks for helping fill the map! Two kinds of contribution are equally welcome:

1. **A new track** — record a circuit that isn't here yet.
2. **Filling a gap** on an existing track — add a car class's racing line, label the
   corners, add a pit lane, or fill in the suggested gears.

## Recording a new track

You'll need [Shfonic Dash](https://shfonic.com/dash/index.html) and a game that
broadcasts world position (F1 25 / F1 26 today).

1. In the game menu, arm **RECORD**, pick the track's game, and enter record mode.
2. Drive the guided passes: **left edge → right edge → racing line** (a few laps, it
   median-averages them), then optionally the **pit lane** (out on track → ADD PIT LANE →
   drive in through and out the far end in one pass).
3. **SAVE.** The app writes `tracks/<game>_<track>.json`.
4. Copy that file out (the DATA tab's `/tracks` API, or straight off the device) and drop
   it into this repo's `tracks/` folder.

Drive *cleanly*, not fast — staying on the line matters more than lap time. (That's also
why gears aren't recorded live; see below.)

## Filling a gap

- **Another car class's line:** at an already-mapped track, enter record mode in that car
  and it keeps the shared geometry — you just re-drive the racing line. Save, and the new
  line lands under its class alongside the others.
- **Corner labels / complexes / notes / gears:** open the file in the **map utility**
  (`track_viewer.html` in this repo — just open it in a browser) and edit them there. Gears
  are filled here, by hand — **never recorded live**.

## Submitting

1. Add or update the `.json` under `tracks/`. Keep the `<game>_<track>.json` naming.
2. Run the validator locally:

   ```bash
   python3 validate.py
   ```

3. Regenerate the coverage table:

   ```bash
   python3 coverage.py --write
   ```

4. Open a pull request. CI re-runs `validate.py`, so a malformed file is caught before
   review — no one has to eyeball the geometry.

## Quality bar

- Racing line hugs the line you'd actually drive; edges follow the track boundary.
- Pit lane joins the circuit cleanly at both ends (the recorder does this for you).
- Corner turn numbers match the official ones where they exist.
- If something's rough or partial, say so in `notes` — an honest "S2 still rough" is far
  better than a silent gap.

See **[track-format.md](track-format.md)** for the full schema.

## Licensing

By submitting a track you agree to license your contribution under
**[CC BY 4.0](LICENSE)**, the same terms as the rest of the collection — so anyone can use
the maps as long as they credit the project.
