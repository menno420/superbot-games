# 2026-07-13 · ORDER 007 verdict fan-out — V043 fishing economy wiring + V044 mint-at-most-once (feature build)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-13T17:31:31Z · order-007 verdict fan-out

Consumed the four Q-0264 sim-lab verdicts relayed as ORDER 007
(`control/inbox.md` @ `d6a9526`, landed via PR #80):

- **V043 fishing APPROVE-WITH-CONSTANTS** — WIRED VERBATIM: the sell curve
  (minnow 8 / bass 13 / pike 27 / legend_carp 80 coins) and the progression
  curve (`ProgressionDelta.game_xp = size_rank` per catch,
  `xp_to_next(L) = 50·L`, milestones surface at L10/L25, levels STAT-NEUTRAL)
  land in `games/fishing/core/economy.py` (new, pure) +
  `games/fishing/inventory/adapter.py` + `services/fishing_workflow.py`
  (new audited `sell` action; a sold fish is CONSUMED from the haul — the
  sell-OR-cook-never-both exclusivity mechanism). Suite 516 → 546; floors
  ratcheted (`services/tests` 149→164, `tests/fishing` 79→94).
- **V044 dnd-escort MINT-AT-MOST-ONCE** — `DnDState.bundle_minted: bool =
  False` + a small guard in `choose()`; a repeat `escort_step` still resolves
  and records (D2) but as a narrate-only transition. The 2× characterization
  test in `services/tests/test_dnd_workflow.py` FLIPPED to 1×, plus stay-loop
  coverage (10 repeats → one mint).
- **V042 mining APPROVE (ratify)** and **V045 exploration RATIFY-WITH-NULL** —
  control-side record steps: the four SIM-REQUEST closures + dispositions and
  the `acked=007 done=007` status ack landed via control PR #84 (fast lane);
  the work claim landed via PR #82 and is released at session close.

## 💡 Session idea

`docs/balance.md` promises "every sim-pinned number … collected onto ONE
page", but `tools/gen_balance.py` does not read the NEW
`games/fishing/core/economy.py` — the V043 sell curve (8/13/27/80), the
`xp_to_next(L) = 50·L` progression curve, and the L10/L25 milestones are now
sim-pinned constants that are invisible on the owner's one-page economy view.
Follow-up session: add a "Fishing economy (V043)" section to the generator
(reads-only, deterministic, same `_table` helpers), regenerate the page, and —
since per-game economy modules will now multiply (mining has `market.py`,
fishing has `economy.py`) — consider a small convention so the generator
enumerates per-game economy modules instead of hand-adding each. Dedupe
check: `.sessions/2026-07-11-auto-balance-page.md` built the generator itself
and `docs/retro/` only cites it; no existing card covers folding the V043
economy module (which postdates them all) into the page. A natural second
slice in the same session: surface `sell` / coins / level / milestones in
`games/fishing/cli.py` so the wired economy is player-visible.

## ⟲ Previous-session review

The prior card (`.sessions/2026-07-13-games-current-state-groom.md`, PR #81)
groomed `docs/current-state.md` honestly — its every-claim-cited discipline
(each PR with squash SHA, API-verified) made this session's Phase-1
re-verification fast, and its "Awaiting implementation: V042–V045 …
ORDER 007" line pointed exactly at this session's work; its seeded
`ledger-behind` advisory idea is still worth a kit session (the ledger will
drift again after this wave: #82–#84 and this PR postdate the groom).
