# Claim · claude-cli-case-sweep

- **Branch:** `claude/cli-case-sweep`
- **Scope:** Pin a cross-CLI case-normalisation invariant that guards the #158
  drift class — a shared/parametric sweep that drives every game CLI's real
  entry point with a CAPITALISED name/id token and asserts it behaves identically
  to the lowercase form (same committed state delta + audit rows). Covers mining
  (`sell`), fishing (`sell`), exploration (`offer`); fixes exploration's
  `offer`/`act` token boundaries (they silently failed on capitals — the same
  latent #158 bug) with a boundary `.lower()`, seam untouched, no balance change;
  xfails the dnd gap (off-menu-safe-clamp is product semantics, deferred as a
  follow-up). New suite `tests/cross_cli`; regenerate `docs/balance.md`.
- **Date:** 2026-07-17 (`date -u` = Fri Jul 17 23:54:00 UTC 2026)
- **Self-initiated:** ⚑ small game-improvement slice (owner order 2026-07-17).
