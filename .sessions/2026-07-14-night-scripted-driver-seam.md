# 2026-07-14 · night build — refactor: scripted-driver twin seam — one feed loop for run_commands and run_hub

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T03:59:32Z · night-scripted-driver-seam

Build slice from #127's card idea, verified fresh at branch base `e2cc40f`:
the five scripted entrypoints — `run_commands` in
`games/{mining,fishing,dnd,exploration}/cli.py` and `run_hub` in
`games/__main__.py` — each still hand-rolled the command feed loop that
`games/shared/cli/repl.py` (#127, squash `94a396c`) owns for interactive
mode: banner lines, feed each command through `step()`, break silently on a
quit step, collect the other steps' lines, append the closing summary.

Shipped `run_scripted(step_fn, commands, *, banner_lines, closing_lines)`
beside `repl()` in the SAME module and adopted it in **all five** drivers —
no entrypoint had to be left behind. Per-game bookkeeping (mining's
`ok_actions`, fishing's `casts_made`/`ok_casts`, dnd's
`scenes_visited`/`story_over`, exploration's `actions_taken`/
`quests_completed`, the hub's `launched` order) moved into `step_fn`
closures — the exact shape their `main()`s already use — so the seam still
only reads `.quit`/`.lines`. The one structural wrinkle was the hub's
"Launching …" banner (appended to the transcript BEFORE the opener runs):
solved with a per-step prefix buffer inside the hub's `step_fn`, transcript
order preserved. Mining's write-only `quit_seen` local died in the diff.

**Byte-identity discipline** (the #125/#127 pattern): 10 fixed-seed/now
scripted transcripts (2 per entrypoint — one quit-terminated, one
end-of-list, both closing paths) captured at base `e2cc40f`, re-captured
after, all 10 SHA-256-identical plus the hub's launched-order; table on PR
#130. Capture script double-run to prove determinism before trusting it.

**11 seam tests** in `services/tests/test_shared_scripted_seam.py`
(registered suite, beside #127's `test_shared_repl_seam.py`): the feed
contract (banner→steps→closing order, quit ends the feed silently and later
commands never dispatch, end-of-list closes through the SAME closing path,
`closing_lines` invoked after the loop sees final state, degenerate empty
inputs, fresh-list return) + a 5-way adoption pin (each driver's imported
`run_scripted` monkeypatched with a recorder — a driver that re-grows its
own loop stops calling the seam and fails). Floor `services/tests`
193 → **204** (floor==collected); `docs/balance.md` regenerated BEFORE
flip; suite **773 → 784 passed** locally; preflight green + strict exit 0
post-flip. Claim `control/claims/night-scripted-driver-seam.md`
self-released here.

## 💡 Session idea

Adopting `run_scripted` exposed that every game now writes its per-step
BOOKKEEPING CLOSURE twice: `main()` and `run_commands` each define a
near-identical `step_fn` (mining counts `ok_actions` in both; dnd tracks
`scenes_visited`/`story_over` in both — 4 lines of stateful logic
duplicated per game, five games). The loops are unified; the closures are
not. A drift between the twins (interactive counting differently than
scripted — e.g. one counts a blocked action, the other doesn't) would be
invisible to both suites, because each driver is only ever tested against
itself. Single-source it: a `make_step_fn(state, sink, ...)` factory per
game beside `step()`, used by BOTH drivers, plus a **driver-parity test**
per game — feed the same fixed command list through `main()` (monkeypatched
input) and `run_commands` and assert the shared transcript region and the
summary lines are equal. Dedupe check against all 2026-07-14 cards' ideas:
the shared-REPL idea (#111 wave) and the scripted-twin idea (#127, this
slice) unified the LOOPS, not the per-game closures; verb-table (#125),
display-table, and README-parity ideas are surface-sync registries; no card
proposes converging the duplicated step_fn bookkeeping or an
interactive-vs-scripted parity pin.

## ⟲ Previous-session review

The previous slice is #129 (`test: dnd effects liveness`, squash `e2cc40f`,
this branch's base, committed 2026-07-14T05:50:25+02:00). Same-night-run
review, so discount accordingly; its claims re-verified here mechanically
rather than taken from the card: `tests/dnd/test_effects_liveness.py`
exists with exactly **7 test functions** (card: "7 tests"), floor
`tests/dnd/EXPECTED_MIN_TESTS.txt` reads **75** and `pytest tests/dnd
--collect-only` collects exactly 75 (floor==collected holds), the 7 run
green in 0.04s, and this slice's own base preflight reproduced the card's
canonical 773. The card's honesty is above average — it flags its own
weakest spot (no headline bug; value is the tripwire) instead of inflating.
One nit that survives scrutiny: its idea text says a completability sweep
should assert "the banked bundle equals the tier cap", but
`catalog.TIER_CAPS` is engine-clamped per tier — an assert against the cap
is right only if no template under-grants; the sweep (this run's slice 3)
should read the granted bundle off the seam's audit rows rather than assume
cap-equality a priori. Also mildly under-specified: "≤8 as specced" cites a
spec the card never links; the number matches the coordinator brief, so
harmless, but a PR-body citation would have made it checkable.
