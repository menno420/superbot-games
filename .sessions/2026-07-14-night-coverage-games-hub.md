# 2026-07-14 · night coverage — games/__main__.py hub loop (tests)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T00:19:20Z · night-coverage-games-hub

Coverage slice, re-confirmed this session at main `a51c5d5` (the 618-test
HEAD) before acting: `games/__main__.py` sat at **72%** (110 stmts,
31 missed: 38–39, 48, 57, 85, 114, 123, 127, 129–133, 185, 208–228, 232).
The existing hub tests (`services/tests/test_world_registry.py`, the
`run_hub` block) prove list/play/quit dispatch through the scripted
driver with a fake launcher, but left `_default_launch`, the
empty-registry menu, `help`, the bare-number/bare-id shortcuts, the
invalid-input branches, the entire interactive `main()` REPL, and the
`python -m games` guard dark.

Shipped **14 focused tests** in `services/tests/test_games_hub_loop.py`
(same suite as the existing hub tests; floor bumped 164 → 178 in the
same commit): `_default_launch`'s return normalisation (`None` → 0, int
passthrough) and `run_hub`'s fallback to it when no launcher is
injected; the empty menu line; the help reference; out-of-range number,
blank line, bare `play`, and unknown-command paths; both bare shortcuts;
`main()` driven TTY-free via monkeypatched `builtins.input` + capsys
(banner, loop output, quit, EOF sign-off, exit code 0); and the module
guard via `runpy` (SystemExit code 0). Module coverage 72% → **100%**
(110/110 stmts); suite 618 → **632 passed**. Tests-only: zero
gameplay-constant changes, every asserted string an existing constant.
**No latent bug found** — `hub_step` really never raises on the bad
inputs tried, and both EOF and end-of-list close with the sign-off as
documented. This flip commit also deletes its own claim file
(`control/claims/night-coverage-games-hub.md`), following the
#106/#107/#109/#110 precedent that strict accepts the same-branch claim
delete.

## 💡 Session idea

Pinning `main()` exposed a structural duplication: the interactive REPL
(lines 208–228) re-implements what `run_hub` already does — banner/menu,
per-step output printing, quit, close-with-sign-off — differing only in
where lines come from (an `input()` loop vs a list) and where they go
(`print` vs a collected transcript). Both game CLIs carry the same
interactive/scripted split. Extract a shared REPL seam:
`games/shared/cli/repl.py` with one generic
`repl(step, *, prompt, source=input, sink=print)` that owns the
prompt/EOF/^C/quit/step-print loop, adopted by hub `main()` (as
`repl(hub_step, ...)`) and by the per-game CLI mains — so the
interactive-loop mechanics (the exact seams this slice had to
monkeypatch-drive) are written and covered ONCE instead of re-tested per
CLI. Dedupe check against used card ideas (telemetry outcome backfill;
CI coverage ratchet; detector-trip registry; display-table completeness
registry; sim-harness smoke registry; pinned-bug marker ledger;
registry-derived CI pytest paths; truth-stamp scaffold generator; the
guarded-rate seam + division grep-pin from #110's card): those target
telemetry, CI plumbing, registries, and renderer math — none touches
input-loop unification; no card idea to date does.

## ⟲ Previous-session review

The previous slice is the catch-sim coverage card, verified MERGED via
the PR API this session: **#110** (head `bf62ee7`) flipped green — its
flip-commit substrate-gate run 29295326166 and tests run 29295326135
both success — and was merged by github-actions[bot] at
2026-07-14T00:13:43Z (squash `a51c5d5`, today's baseline HEAD). Its
earlier commits held the designed born-red HOLD (e.g. substrate-gate
29294826285 / 29294929975 failures on `0b80723` / `0453442` heads of the
same wave). Re-checked its two headline numbers against this session's
own runs rather than trusting the card: the suite at `a51c5d5` collects
**618 passed** (my baseline run pre-slice) matching its "606 → 618", and
`games/fishing/sim/catch_sim.py` measures **100%** (97/97 stmts) under
`tests/fishing/` today, matching its "69% → 100%". Its claim-file
self-delete also held up — `control/claims/` contained only README.md at
this session's start. One honest note: the card says "12 focused tests"
while its PR body says "≤14" — accurate but the floor-file diff
(104 → 116 in tests/fishing) is the only committed artifact that pins
the exact count; the card number matches it.
