# 2026-07-11 · Mining encounter narration → theme data (Q-0267 leak #1)

> **Status:** `complete`
>
> 📊 Model: Claude Opus · 2026-07-11T01:02:54Z · extract mining encounter narration to theme data (Q-0267 leak #1)

## Goal

Clear the **#1 ❌ finding** of the Q-0267 theme-slot audit
(`docs/audit/theme-slot-readiness-2026-07-11.md` §3): mining encounter narration
and the "creature" noun are hardcoded f-string literals *inside* the `_resolve_*`
branches of `games/mining/core/encounters.py` (cited lines `160,253,269,309,321,335,342`).
Move **all** player-visible nouns/narration into a module-level DATA table keyed on
neutral ids — mirroring `grid.py`'s `_STRIKE_NOTE` and `fishing/species.py`. This is
**behaviour-preserving**: deterministic outcomes (kind, resolution, rewards, damage,
energy_cost) stay byte-identical; the narration relocates from code to data and stays
byte-identical too (pure relocation, not a rewrite). Deliver ONE merged-on-green PR
(roadmap item **R1**).

## What shipped

- **`games/mining/core/encounters.py`** — a `# --- narration data (theme-swappable, Q-0267) ---`
  block: a `_Narration` neutral-slot enum, a `_NARRATION` template table keyed on it, a
  `_CREATURE_NOUN` row, and a single pure `_narrate(slot, **fields)` helper. Every
  `_resolve_*` branch and `_NONE_OUTCOME` now assembles its string via `_narrate` and
  contains **zero** player-visible string literals. Outcome logic untouched.
- **`tests/mining/test_encounter_narration.py`** — the golden/characterization guard:
  a fixture (`_encounter_golden.json`) captured from the *pre-change* resolver pins the
  FULL `EncounterOutcome` (kind, resolution, rewards, damage, energy_cost, **and**
  narration) byte-identical across a fixed sweep; plus a data-drivenness test (swap a
  `_NARRATION` row → narration changes, outcome fields identical) and a no-inline-strings
  guard on the `_resolve_*` source.
- **Audit doc** `docs/audit/theme-slot-readiness-2026-07-11.md` — row verdict ❌→✅, §5
  R1 marked shipped (cites this PR).

## 💡 Session idea

The golden fixture is captured from the pre-change resolver and encodes the OLD narration
strings; the post-change sweep must reproduce it byte-for-byte. That makes "pure
relocation" a *provable* property, not a claim — the same discipline generalises to R2
(grid barren line) and R3 (fishing status scaffold): capture-before, assert-after.

## ⟲ Previous-session review

Builds directly on the theme-slot audit (PR #28) which *is* this session's spec, and on
the fishing skeleton (PR #25) whose `species.py` + `catch.py` are the reference shape the
audit names. No conflict with the shared-inventory seam (PR #29 / R5) — that's a separate,
later leak (#2, noun-as-key); this slice touches only encounter narration.

## Guard recipe

Behaviour-preservation anchor: `encounters.resolve` / `_resolve_hazard` / `_resolve_loot_cache`
/ `_resolve_rich_vein` in `games/mining/core/encounters.py`; the guard target is
`tests/mining/test_encounter_narration.py::test_encounter_outcomes_match_golden` (fixture
`tests/mining/_encounter_golden.json`, sweep in `tests/mining/_encounter_golden.py`). If a
future narration edit is intentional, regenerate the fixture from that module's `sweep_records()`.
