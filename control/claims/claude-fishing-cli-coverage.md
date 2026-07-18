# Claim · claude-fishing-cli-coverage

- **Branch:** `claude/fishing-cli-coverage`
- **Scope:** Pin the fishing CLI's `sell <species> [qty]` argument handling that
  was unpinned: (a) NON-INTEGER quantities — a float (`sell bass 1.5`) and a
  negative (`sell bass -2`, the seam's "must be positive" no-op path) — and
  (b) MULTI-WORD species DISPLAY names (`sell Legendary Carp 3`). Investigation
  found NO real bug: the CLI addresses species by their neutral single-token id
  (`legend_carp`), never the multi-word display name ("Legendary Carp"), so the
  multi-word input honestly no-ops ("Quantity must be a number, got 'Carp'.")
  with zero state change — and `sell legend_carp 2` sells that same species
  correctly. Whether the CLI *should* resolve display names is a product call,
  deferred as a follow-up. Pure test additions to `tests/fishing/test_cli.py`;
  bump the `tests/fishing` floor 121 → 125 and regenerate `docs/balance.md`.
  No CLI/seam/economy/balance change.
- **Date:** 2026-07-18 (`date -u` = Sat Jul 18 00:12:09 UTC 2026)
- **Self-initiated:** ⚑ small game-improvement slice (owner night order 2026-07-18).
