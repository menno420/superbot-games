# 2026-07-11 · D&D story game — scene-chaining (data-driven bounded transitions)

> **Status:** `complete`
>
> 📊 Model: Opus 4.8 · 2026-07-11T15:18:58Z · D&D scene-chaining (data-driven bounded transitions)

## Goal

Extend the merged D&D walking skeleton (PR #48) from a **single scene** to a small
**data-driven scene chain**, without loosening the bounded-menu law (Q-0040 / D-0007,
design §4.4). The AI Dungeon Master's authority stays exactly what it was: pick one id
from a hard-capped menu. Scene TRANSITIONS become PRE-DEFINED DATA on each menu option
(`next_scene_id`) — never computed or chosen by the DM. The model can only select an
option; that option's destination is immutable data, so it can never steer to an
arbitrary scene. All new scene nouns/flavour/emoji stay in the theme catalog (Q-0267),
and the new scenes reuse only the existing sim-pinned effects — no new balance numbers.

## What shipped

- **`games/dnd/core/models.py`** — `MenuOption` gains an OPTIONAL, frozen
  `next_scene_id: str | None = None` (data; `None` = stay/end). It is the option's
  pre-defined destination — the DM never supplies it. `models.py` stays catalog-free
  (no import cycle); the referenced-scene invariant is enforced at the catalog layer.
- **`games/dnd/core/resolver.py`** — `Resolution` gains `next_scene_id`, lifted verbatim
  from the CHOSEN option's DATA. On the clamp path `chosen` is the default option, so the
  destination is the DEFAULT's own fixed edge (deterministic) — an off-menu/hallucinated
  choice can never navigate anywhere but the default's pre-defined edge (here: stay).
- **`games/dnd/data/scenes.py`** — two MORE scenes chained off `waystation_road`:
  `waystation_gate` (press on) and `treeline_watch` (scout), each a ≤4 bounded menu with
  its own narrate-only no-op default. All copy/nouns/emoji are catalog rows.
  `_assert_transitions_resolve()` runs at import and fails LOUDLY on any dangling
  `next_scene_id` — no dangling edge ships. Rewards reuse the existing sim-pinned
  effects (`escort_step` = `TIER_CAPS[I]`; `scout_narrate`/`rest_noop` mint nothing).
- **`tests/dnd/test_scene_chain.py`** — 8 new tests. Headline: **deterministic traversal**
  — the fixed choice sequence `advance_escort → circle_to_treeline → hold_position` walks
  the pinned path `["waystation_road", "waystation_gate", "treeline_watch"]`. Plus:
  transitions are data-driven (destination = option DATA, never a DM field); clamp chains
  safely (hallucinated/malformed → default option → default's own edge, state consistent);
  every referenced `next_scene_id` resolves to a real scene. Floor bumped 15 → 23.

## Verification

- `python3 -m pytest tests/dnd/ -q` → 23 passed.
- `python3 tests/check_suite_floors.py` → exit 0 (tests/dnd 23 ≥ floor 23).
- `python3 -m pytest tests/ games/exploration/tests/ -q` → 295 passed.
- `python3 bootstrap.py check --strict` → exit 0.
- Bound guarantee (absent the not-yet-merged #49 menu_sim): `Scene.__post_init__`
  enforces the ≤4 menu cap on every new scene, and the new scenes reuse ONLY the three
  existing effects, so no new balance number is introduced — the #49 sim will enumerate
  all 3 scenes automatically once it lands, still ≤ GLOBAL_MAX (no pay-to-win).

## 💡 Session idea

**A scene-graph reachability check for the D&D catalog.** This slice added a load-time
`_assert_transitions_resolve()` that rejects dangling `next_scene_id` edges. The natural
next guard is a *reachability* sweep — assert every catalog scene is reachable from the
start scene (or explicitly marked terminal), so a scene added but never wired into any
option's `next_scene_id` fails LOUDLY instead of shipping as dead content. Cheap to add
now (the SCENES dict is the whole graph) and it turns the menu_sim's per-scene enumeration
into a proof that the sim actually covers the reachable game.

## ⟲ Previous-session review

The previous session (D&D walking skeleton, PR #48) did the load-bearing thing right: it
made the bounded-menu law *executable* rather than merely documented — `Scene.__post_init__`
enforcing the ≤4 cap + registered-effect invariant, and the resolver's validate→clamp→apply
choke point, are exactly the seams this slice extended without touching. The schema was
already shaped for growth (frozen dataclasses, neutral text keys, an effect registry), so
adding a `next_scene_id` field was purely additive with zero churn to the determinism core.
What it left implicit: there was no navigation at all, so "the DM can't steer the story" was
untested for transitions specifically — this session closed that by making the *destination*
data on the option and pinning the clamp-takes-only-the-default-edge property. **System
improvement:** the skeleton floor file (15) and the in-flight menu_sim PR (#49, bumps to 19)
both edit `tests/dnd/EXPECTED_MIN_TESTS.txt`; the per-suite floor design already isolates
suites from each other, but two open PRs against the SAME suite's floor still collide — a
tiny convention (floor bumps land in their own trailing commit) would make the rebase a
one-line no-brainer instead of a content conflict.
