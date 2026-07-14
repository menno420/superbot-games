# 2026-07-14 · night coverage — games/__main__.py hub loop (tests)

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T00:19:20Z · night-coverage-games-hub

Coverage slice, re-confirmed this session at main `a51c5d5` (the 618-test
HEAD) before acting: `games/__main__.py` sits at **72%** (110 stmts,
31 missed: 38–39, 48, 57, 85, 114, 123, 127, 129–133, 185, 208–228, 232).
The existing hub tests (`services/tests/test_world_registry.py`, the
`run_hub` block) prove list/play/quit dispatch through the scripted
driver with a fake launcher, but leave these seams dark:

- lines 38–39 — `_default_launch` (opener return normalised: `None` → 0,
  int passed through),
- line 48 — the empty-registry menu ("No games are registered."),
- lines 57 + 123 — `help_lines()` and the `help` verb,
- line 85 — an out-of-range list number resolving to None,
- line 114 — a blank input line as a no-op,
- line 127 — bare `play` with no argument (usage message),
- lines 129–133 — the bare-number / bare-id shortcuts and the
  unknown-command branch,
- line 185 — `run_hub` falling back to `_default_launch` when no
  launcher is injected,
- lines 208–228 — the entire interactive `main()` REPL (banner, input
  loop, EOF/^C handling, step-output printing, sign-off, exit code),
- line 232 — the `python -m games` entry guard.

Plan: ≤14 focused tests in a new `services/tests/test_games_hub_loop.py`
(same suite as the existing hub tests; floor bumped in the same commit),
driving `main()` via monkeypatched `builtins.input` + capsys and the
module guard via `runpy`, everything else through the public helpers at
EXISTING strings. Tests only; a genuine bug would be pinned + HEADLINED,
not fixed here.
