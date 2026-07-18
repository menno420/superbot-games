# Claim · claude-mining-negqty-coverage

- **Branch:** `claude/mining-negqty-coverage`
- **Scope:** Pin the mining CLI's negative / non-integer quantity handling for
  the qty-taking verbs (`sell` / `build` / `skill`), which was unpinned. The
  boundary split `args[-1].lstrip("-").isdigit()` (`_split_item_qty`) branches
  two ways: (a) a leading-minus token (`sell iron -3`, `build forge -1`,
  `skill mining -2`) PASSES the isdigit test, parses as a NEGATIVE int, and is
  forwarded to the audited seam whose non-positive / invalid-level guard rejects
  it one layer deeper (an honest "must be positive" / "cannot be upgraded from
  level -1" no-op); (b) a non-numeric token (`sell iron abc`, `build forge xyz`,
  `skill mining foo`) FAILS the isdigit test, folds into the multi-word name, and
  the unknown name is rejected ("cannot be sold" / "not buildable" / "not a skill
  branch"). Investigation found NO bug: every path is an honest no-op today — no
  crash, no state change, no audit row. Mirrors what slice 4 (PR #161) did for
  the fishing CLI. Pure test additions to `tests/mining/test_cli.py` (6 tests);
  bump the `tests/mining` floor 196 → 202 and regenerate `docs/balance.md`. No
  CLI / seam / economy / balance change.
- **Date:** 2026-07-18 (`date -u` = Sat Jul 18 00:21:21 UTC 2026)
- **Self-initiated:** ⚑ small game-improvement slice (owner night order 2026-07-18).
