# Claim · games-reconcile-race-fix

- **Branch:** `claude/games-reconcile-race-fix`
- **Scope:** Port superbot-idle PR #142 (commit `884aeae`) to games'
  `.github/workflows/automerge-card-guard.yml`. The reconcile job's
  HEAD-REF PROVENANCE branch reads the PR's merged state, then ~seconds
  later calls `gh pr merge --disable-auto <pr>` on a fatal-by-default
  helper. GitHub-native auto-merge can land the PR inside that TOCTOU
  window, so the disarm call errors `GraphQL: Can't disable auto-merge
  for this pull request` and the whole reconcile job fails — the benign
  post-merge `reconcile` failures + auto-merge enable/disable churn seen
  across today's PRs (#171–#175).

  Fix (mirror idle #142): make ONLY the provenance-stamp disarm call
  tolerant — `fatal=False`; on a nonzero return, re-fetch the PR's
  merged state via the API and branch: if merged → `::notice::` + exit
  0; if not merged → `::warning::` (leave the enabler's arm standing) +
  exit 0. Tolerate-and-exit-clean, NOT a lock — provenance stamping is a
  survey aid, not a merge gate. The in-progress-card DISARM call
  upstream stays fatal (an unreadable/failed disarm on a born-red card
  must still fail loud). Minimal diff, single call's error handling
  only; no workflow restructuring.
- **Date:** 2026-07-18 (owner-authorized self-initiated CI fix)
- **Self-initiated:** ⚑ ports idle #142 (commit `884aeae`) to games'
  card-guard; observed as the benign reconcile failures + auto-merge
  churn on today's PRs (#171–#175). Reversible.
