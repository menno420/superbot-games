# 2026-07-14 · night coverage — games/mining/cli.py (tests)

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T01:07:58Z · night-coverage-mining-cli

Coverage slice, re-confirmed this session at main `6de5666` (the
646-test HEAD, #112's merge) before acting: `games/mining/cli.py` sits
at **75%** (179 stmts, 44 missed: 82–85, 88–90, 189, 193, 199, 207,
212, 215–220, 224, 226, 276, 321, 355–380). The existing
`tests/mining/test_cli.py` drives scripted sessions through
`run_commands` (mine/sell/buy/skill economy legs, blocked actions, help
and quit ergonomics) but leaves these seams dark:

- lines 82–85 + 88–90 — the status gear-line fallback branches
  (durability without a max cap, no durability entry at all) and the
  equipped-light suffix,
- lines 189 / 193 — the `harvest` and `ascend` dispatch legs,
- lines 199, 207, 212, 215–216, 224, 276 — the malformed-command
  usage paths (`sell`/`buy`/`repair`/`build`/`skill` with no args),
- lines 217–220 — the `build` leg (explicit level and the
  default-level-from-structures read),
- line 226 — `_dispatch_action`'s unreachable-via-`step` None tail,
- line 321 — `run_commands`' fresh default state,
- lines 355–380 — the whole interactive `main()` REPL (banner, input
  loop, quit, EOF, summary, exit code).

Plan: ≤14 focused tests in a new `tests/mining/test_cli_repl.py`
(tests/mining floor bumped in the same commit, `docs/balance.md`
regenerated in the same push — the #111 lesson), driving `main()`
TTY-free via monkeypatched `builtins.input` + capsys per the #111 hub
pattern. Tests only, EXISTING seam/core constants; a genuine bug would
be pinned + HEADLINED, not fixed here.
