# 2026-07-14 · night build — refactor: scripted-driver twin seam — one feed loop for run_commands and run_hub

> **Status:** in-progress
>
> 📊 Model: Fable · 2026-07-14T03:59:32Z · night-scripted-driver-seam

Build slice from #127's card idea: the five scripted entrypoints
(`run_commands` in `games/{mining,fishing,dnd,exploration}/cli.py` and
`run_hub` in `games/__main__.py`) still hand-roll the command feed loop
that `games/shared/cli/repl.py` (#127, squash `94a396c`) owns for
interactive mode. Extract the shared feed-loop mechanics into the same
module (`run_scripted(step_fn, commands, ...)` beside `repl()`), adopt in
all five, with byte-identity discipline: fixed-seed/now scripted
transcripts captured BEFORE, asserted byte-identical AFTER, SHA-256 table
on the PR. Focused seam tests in a registered suite.

## 💡 Session idea

(pending — filled at flip)

## ⟲ Previous-session review

(pending — filled at flip)
