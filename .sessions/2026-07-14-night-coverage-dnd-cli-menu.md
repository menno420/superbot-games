# 2026-07-14 · night coverage — games/dnd cli + menu_sim (tests)

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T01:20:18Z · night-coverage-dnd-cli-menu

Coverage slice over the dnd area as ONE unit, re-confirmed this session
at main `73111d0` (the 659-test HEAD, #113's merge) before acting:

- `games/dnd/cli.py` at **77%** (142 stmts, 33 missed: 87, 124, 196,
  265, 303–336) — the existing `tests/dnd/test_cli.py` drives the
  scripted arc, the off-menu clamp, and the read-only verbs through
  `run_commands`, but leaves the capability suffix in the status and
  summary reward lines, the `help` verb dispatch in `step`,
  `run_commands`' fresh default state, and the whole interactive
  `main()` REPL dark;
- `games/dnd/sim/menu_sim.py` at **77%** (94 stmts, 22 missed: 138,
  193, 206–208, 215–244) — the existing `tests/dnd/test_menu_sim.py`
  pins the happy-path economy bounds but leaves the
  reward-not-seed-stable AssertionError, the over-cap
  `all_within_global_max` flag flip, `_fmt_reward`'s two branches, and
  the whole `format_report` renderer dark.

Plan: ≤16 focused tests across two new files
(`tests/dnd/test_cli_repl.py`, `tests/dnd/test_menu_report.py`;
tests/dnd floor bumped and `docs/balance.md` regenerated in the same
push — the #111 lesson), driving `main()` TTY-free via monkeypatched
`builtins.input` + capsys per the #111/#113 pattern, and tripping the
sim's two defensive branches via a monkeypatched
`_resolve_option_reward` stub (the guard is otherwise unreachable — the
real resolver IS seed-stable and under-cap). Tests only, EXISTING
constants; a genuine bug would be pinned + HEADLINED, not fixed here.
