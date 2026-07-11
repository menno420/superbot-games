# 2026-07-11 · Theme remediation — mining R2 (capacity/world data-isolation)

> **Status:** 🔴 `born-red`
>
> 📊 Model: Claude Opus · 2026-07-11T01:45:39Z · Q-0267 mining R2 data-isolation (capacity/world)

## Goal

Second sweep of the Q-0267 theme-readiness audit for the mining domain: relocate the
remaining welded player-visible strings in the pure mining core out of code and into
module-level data tables, exactly mirroring the shipped pattern (`grid._STRIKE_NOTE`
and the merged encounters `_NARRATION`, PR #31 / R1). Scope this slice to the two
genuine code-leak surfaces the audit flagged — `capacity.py`'s pack/vault warnings and
`world.py`'s position line + descend hints. **Pure byte-identical refactor:** every
rendered player string identical before/after, proven by capture-before/assert-after
snapshot tests; deterministic logic and all numbers untouched — only string literals
move. `skills.py`'s `BRANCH_LABELS` is already a module-level data dict (emoji live in
the label VALUES, swappable as a unit) so it is left as-is. One READY-on-green PR.

## What shipped

- **`games/mining/core/capacity.py`** — a module-level `_CAP_WARNING` table (keyed on
  neutral `"pack"`/`"vault"` slots) now holds the two capacity-nudge strings;
  `pack_warning` / `vault_warning` look up the row and fill `{used}`/`{cap}` from the
  `CapStatus`. The at-cap/over-cap thresholds and all numbers are untouched.
- **`games/mining/core/world.py`** — a `_POSITION_TEMPLATE` and a `_DESCEND_HINT` table
  hold the `"<emoji> <Label> (depth N/MAX)"` position line and the two descend hints;
  `describe_position` / `descend_hint` fill the numbers + biome label at the call site.
  `BIOME_LABELS` / `BIOME_EMOJI` were already clean data and are left in place.
- **`tests/mining/test_capacity_warnings.py`** (+4) — snapshots the exact pre-extraction
  pack/vault strings, the under-threshold `None` paths, and proves the copy flows through
  the `_CAP_WARNING` table (row swap re-skins only the string).
- **`tests/mining/test_world_hints.py`** (+4) — snapshots every band's position line and
  every descend hint byte-identical, the max-depth branch, and the `_POSITION_TEMPLATE`
  data-swap.
- **Not touched:** `skills.py` (`BRANCH_LABELS` already data-isolated), `encounters.py`
  (R1, merged #31), the count-floor file / `tests.yml` (adding tests only raises the
  mining count above the floor; no floor edit needed — avoids conflict with pending #34).
- **Verification:** `pytest tests/mining/` → 87 passed; `pytest tests/ games/exploration/tests/`
  → 256 passed; `bootstrap.py check --strict` → exit 0. The 8 new snapshot tests passed
  green against the UNMODIFIED code first (baseline lock), then again post-refactor
  (byte-identical proof).

## 💡 Session idea

The cleanest byte-identity proof for a relocation is a snapshot test that hardcodes the
EXACT expected string and is run green **against the unmodified code first** — then the
same assertion passing post-refactor is a literal before/after equality, not a claim.
Splicing the multi-line f-string concatenations back into a single `.format` template
(`"... item " + "types) — ..."` → `"... item types) — ..."`) is the one place a stray
space could sneak in, so the snapshot pins that seam specifically.

## ⟲ Previous-session review

Builds directly on the merged mining narration→data slice (PR #31, R1), which moved the
encounter resolver's player strings into `encounters._NARRATION`; this is R2, the same
audit's remaining mining code-leaks. Same capture-before/assert-after discipline the
mining narration slice used, and the same `grid._STRIKE_NOTE` template shape. No overlap
with the shared-inventory seam or the fishing spot-biomes slice (#35); the only mining
core files this touches (`capacity.py`, `world.py`) were untouched by #31.

## Guard recipe

Behaviour-preservation anchor: the snapshot tests in `tests/mining/test_capacity_warnings.py`
and `tests/mining/test_world_hints.py` hardcode the exact pre-extraction strings for
fixed inputs. If a `_CAP_WARNING` / `_POSITION_TEMPLATE` / `_DESCEND_HINT` row is edited
intentionally (a real re-skin), those snapshots are the deliberate update point; an
unintended drift fails them immediately.
