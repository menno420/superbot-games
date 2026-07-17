# Claim · claude-mining-cli-case

- **Branch:** `claude/mining-cli-case`
- **Scope:** Fix the standalone mining CLI's case-sensitive item/branch handling
  (`games/mining/cli.py`) — a capitalised token (`sell Iron`, `buy Torch`,
  `skill Mining`) currently misfires (falsely "0 held", mismatched inventory key,
  "not a skill branch") because the CLI never lower-cases the name the way the
  fishing CLI already does. Normalise at the CLI boundary + regression tests.
- **Date:** 2026-07-17 (`date -u` = Fri Jul 17 23:23:25 UTC 2026)
- **Self-initiated:** ⚑ small game-improvement slice (owner order 2026-07-17).
