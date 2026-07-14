# 2026-07-14 · night build — refactor: shared REPL seam — one loop implementation for all five CLIs

> **Status:** in-progress
>
> 📊 Model: Fable · 2026-07-14T03:23:37Z · night-shared-repl-seam

Build slice from `.sessions/2026-07-14-night-coverage-games-hub.md`'s card
idea (verified unimplemented: no `games/shared/cli/` exists). Five
hand-rolled interactive `main()` loops — `games/{mining,fishing,dnd,
exploration}/cli.py` + `games/__main__.py` — re-implement the same
prompt/EOF/^C/quit/step-print mechanics. Plan: one generic
`games/shared/cli/repl.py` `repl(step_fn, *, prompt, source=input,
sink=print, banner_lines=…, closing_lines=…)` owning the loop, adopted by
all five mains under byte-identity discipline (scripted-stdin transcripts
captured before/after with fixed rng/now, SHA-256s recorded in the PR
body), plus focused seam tests (EOF, interrupt, quit, banner, exit code)
in a registered suite dir.
