# 2026-07-13 · ORDER 007 verdict fan-out — V043 fishing economy wiring + V044 mint-at-most-once (feature build)

> **Status:** in-progress
>
> 📊 Model: Fable · 2026-07-13T17:31:31Z · order-007 verdict fan-out

Consuming the four Q-0264 sim-lab verdicts relayed as ORDER 007
(`control/inbox.md` @ `d6a9526`, landed via PR #80):

- **V043 fishing APPROVE-WITH-CONSTANTS** — wire the sell curve
  (minnow 8 / bass 13 / pike 27 / legend_carp 80 coins) and the progression
  curve (`ProgressionDelta.game_xp = size_rank` per catch,
  `xp_to_next(L) = 50·L`, milestones at L10/L25, levels STAT-NEUTRAL)
  VERBATIM; wire the sell leg so one fish yields sell-OR-cook, never both.
- **V044 dnd-escort MINT-AT-MOST-ONCE** — one `bundle_minted: bool = False`
  field on `DnDState` + a small guard in `choose()`; flip the 2×
  characterization test in `services/tests/test_dnd_workflow.py` to 1×.
- **V042 mining APPROVE (ratify)** and **V045 exploration RATIFY-WITH-NULL**
  are control-side record steps (outbox closures) — no code change.
