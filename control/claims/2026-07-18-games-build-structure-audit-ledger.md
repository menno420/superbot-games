# Claim · 2026-07-18-games-build-structure-audit-ledger

- **Branch:** `claude/games-build-structure-audit-ledger`
- **Scope:** Ship ONE owner-authorized PR resolving two queued owner-input
  decisions from `docs/NEXT-TASKS.md` (both reversible; stated defaults applied
  and flagged for owner review). Both live in `services/mining_workflow.py`.
  **Decision #3 [contract]** — `build_structure` must derive the authoritative
  current level from `state.structures.get(key, 0)` (matching
  `vault_upgrade` / `allocate_skill`) rather than trusting the caller's `level`
  argument. Verified ALREADY LANDED on main by #167 (`ba78870`,
  `level = state.structures.get(key, 0)`), with the regression test
  `test_build_structure_uses_state_level_not_caller_claim` present; this PR marks
  the decision resolved and flags the prior fix. **Decision #8 [design]** —
  `economy_audit_log` under-counts coin sinks because `build_structure` /
  `vault_upgrade` emit only a structure/vault LEVEL row while sell / buy / repair
  emit a `target="coins"` row. Default applied: `build_structure` and
  `vault_upgrade` ALSO emit a `target="coins"` ledger row (prev/new = coin
  balance before/after the sink, same reason token, matching the sell/buy/repair
  row shape) IN ADDITION TO the existing level row. Tests: a new assertion that a
  wallet reconstructed from `economy_audit_log` coin rows equals the live wallet
  after a build and a vault upgrade, plus the record-count invariants updated for
  the now-two-row build/vault ops. No balance/economy NUMBER changes; only a
  structural audit row is added.
- **Date:** 2026-07-18 (`date -u` = 2026-07-19T07:36:52Z)
- **Self-initiated:** ⚑ owner-authorized code slice (menno420, live 2026-07-18).
