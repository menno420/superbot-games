# 2026-07-12 · mining WORKFLOW audited-seam scoping (rung 2 · ⚑ audit-schema decision)

> **Status:** `in-progress`
>
> 📊 Model: Opus 4.8 · 2026-07-12T01:51:48Z · mining workflow-seam scoping

## 💡 Session idea

The rung-2 audited seam (`services/mining_workflow.py`) could not be honestly
built as a skeleton this session because the oracle does not answer the two
questions a skeleton would have to hard-code: which audit schema mining adopts
(the 11-field structural `audit.action_recorded` contract vs the 6-column
`economy_audit_log` row) and whether state-changing item-grant actions
(`mine`/`harvest`) get audited at all — in the oracle they are UNAUDITED. So
this session scopes the seam and raises a ⚑ owner/lab decision rather than
inventing an audit contract by fiat.

## ⟲ Previous-session review

Builds on PR #59, which landed READY + green correcting stale
"plugin-contract in flight" claims to "defined and binding at superbot-next
`docs/game-plugin-contract.md@d3dba9b` (D-0056)". That correction is what makes
the ladder (PURE CORE → WORKFLOW → HOST adapter) a deliberate ordering rather
than a wait on a missing contract; ORDER 004's fleet self-review was verified
satisfied via the retro on that lane.
