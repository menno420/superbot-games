# 2026-07-18 · games-broken-gear-consumed — fix(mining): consume gear on break (durability 0)

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus 4.x · high · runtime bugfix

⚑ Owner-authorized code slice (menno420, live 2026-07-18): resolve ONE queued
owner-input decision from `docs/NEXT-TASKS.md` as its own small, tested,
autonomous PR, applying the decision's stated default and FLAGGING it in the PR
body for the owner's asynchronous review. The change lives in
`services/mining_workflow.py`; it is reversible. Executed at branch base
`11e1451` (#172, main HEAD).

**What this slice ships.**

- **Decision #2 [design] — broken gear stays equipped and fully effective at
  durability 0.** The mining seam (`services/mining_workflow.py::_apply_wear`)
  ticks 1 durability per wearing action and reports items that hit 0 in
  `broke`, but it never clears them: a broken tool/light sat in `state.equipped`
  at durability 0 and kept feeding `equipment.compute_stats` — the full mine
  multiplier, depth access, and light radius — forever, so the durability sink
  was toothless. The equipment docstring says gear is "consumed on break," but
  no layer did it. **Owner-default applied: consume on break.** When
  `_apply_wear` ticks an equipped item to 0, it now consumes the item —
  unequips it from `state.equipped`, drops its `state.durability` entry, and
  removes one unit from `state.inventory` if a copy is held there — so it stops
  contributing stats on the very next action. Items above 0 durability are
  untouched; a subsequent `mine` with an emptied tool slot does not crash (the
  seam already reads `has_pickaxe` from inventory and tolerates an empty slot).
  Reversible; flagged for owner review.

**Tests.** `services/tests/test_mining_workflow.py` — the prior
`test_mine_reports_break_only_on_the_tick_it_breaks` (which pinned the OLD
"broken tool stays at durability 0 in the slot, never re-reported" behavior) is
updated to the corrected consumption behavior (the item is gone from
`equipped` / `durability` / `inventory` after the break tick, and a follow-up
`mine` neither re-reports it nor crashes). New cases pin: a tool at durability
1 used once breaks → is consumed → no longer contributes its mine multiplier
next action; an item above 0 is unaffected; the last tool breaking leaves an
empty slot without a crash. No economy / balance number changed.

## 💡 Session idea

⚑ Self-initiated. A durability sink only bites if the break has a consequence
in state: reporting `broke` to the UI is a *notification*, not an *effect*. The
reusable move is to make the break tick the single place that both reports AND
mutates — unequip + consume where the durability actually hits 0 — so no caller
can forget to clear a spent item, and "consumed on break" stops being a
docstring the code contradicts.

## ⟲ Previous-session review

The 2026-07-18 games-mining-qty-diagnostic slice (card
`2026-07-18-games-mining-qty-diagnostic`, PR #172) resolved queued decision #6
from `docs/NEXT-TASKS.md`, landing main at `11e1451`. This slice is the next
owner-authorized follow-through in the same queue: take one more queued
owner-input decision (#2), apply its stated default, flag it, and land on green.

## ✅ Landed

_Filled on the flip-to-complete commit._
