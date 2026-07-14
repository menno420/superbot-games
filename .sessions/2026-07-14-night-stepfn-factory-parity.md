# 2026-07-14 · night build — refactor: one step-closure per game — main() and run_commands share construction

> **Status:** in-progress
>
> 📊 Model: Fable · 2026-07-14T04:51:53Z · night-stepfn-factory-parity

Build slice from #130's final-verdict follow-up: the loops are unified
(`repl` / `run_scripted`, #127/#130) but each game still writes its
per-step BOOKKEEPING CLOSURE twice — `main()` and `run_commands` each
define a near-identical `step_fn` (mining counts `ok_actions` in both;
dnd tracks `choices_made`/`scenes_visited`/`story_over` in both), and the
hub pair duplicates the announcing-launch wrapper. Extract one
`make_step_fn(...)` factory per game (returning the closure plus its
tally) used by BOTH drivers, byte-identity discipline (fixed-seed/now
transcripts for all entrypoints before/after, SHA-256 table on the PR),
and driver-parity tests pinning the actual main()-vs-run_commands
relation per game.

## 💡 Session idea

(pending — filled at flip)

## ⟲ Previous-session review

(pending — filled at flip)
