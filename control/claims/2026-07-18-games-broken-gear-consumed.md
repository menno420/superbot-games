# Claim · games-broken-gear-consumed

- **Branch:** `claude/games-broken-gear-consumed`
- **Scope:** Resolve queued owner-input decision **#2 [design]** from
  `docs/NEXT-TASKS.md` — a mining tool/light at durability 0 (broken) stays
  equipped and keeps contributing its full `EffectiveStats` (mine multiplier,
  depth access, light radius) forever: the equipment docstring
  (`games/mining/core/equipment.py`) says gear is "consumed on break," but no
  layer does it — the durability sink is toothless. Apply the stated
  owner-default: **consume on break.** When `services/mining_workflow.py::
  _apply_wear` ticks an equipped item to durability 0, consume it — unequip it
  from `state.equipped`, drop its `state.durability` entry, and remove one unit
  from `state.inventory` if held — so it stops contributing stats on the next
  action. Items above 0 durability are unaffected; the last tool breaking does
  not crash a subsequent `mine` (the seam already tolerates an empty tool slot).
  One narrow change in `services/mining_workflow.py::_apply_wear` + tests in
  `services/tests/test_mining_workflow.py` (the prior
  `test_mine_reports_break_only_on_the_tick_it_breaks`, which pinned the OLD
  "broken tool stays at 0 in the slot" behavior, is updated to the corrected
  consumption behavior + new cases added). Reversible; flagged for owner review.
  No economy / balance number changed.
- **Date:** 2026-07-18 (owner-authorized code slice)
- **Self-initiated:** ⚑ owner-authorized game-improvement slice (menno420, live
  2026-07-18) — one queued owner-input decision resolved as its own flagged PR.
