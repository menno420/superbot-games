# 2026-07-13 · mining WORKFLOW audited seam (rung 2 · build)

> **Status:** 🔴 `in-progress`
>
> 📊 Model: Opus 4.8 · 2026-07-13T00:54:25Z · rung-2 mining workflow seam

## 💡 Session idea

Build rung 2 of the mining ladder — the WORKFLOW audited seam — on the
sanctioned §5 default of `docs/design/mining-workflow-seam.md` (now that the
scoping session landed the D1/D2 flag). The seam is a top-level
`services/mining_workflow.py`: it reads a mutable `MiningState`, calls the pure
core to decide, mutates the state, builds the oracle's 11-field structural
`AuditRecord` (D1), and calls an injected `Sink` for **every** state-changing
action including item grants (D2 — a reversible divergence from the oracle).
The audit types (`AuditRecord` / `Sink` / `InMemorySink`) are factored into a
game-neutral `services/audit.py` so the next-slice fishing seam reuses them
without welding two games together. All ten actions (mine / harvest / sell /
buy / repair / descend / ascend / build / vault / allocate-skill) wire to the
real core decide-fns; every price/reason/weight is quoted VERBATIM — no balance
numbers invented. The seam lives OUTSIDE `games/mining/core/`, so the 19-module
purity guard stays intact. A SIM-REQUEST (surface lock-in + source/sink gap)
and the D1/D2 decision-note are filed in `control/outbox.md` for the owner/lab.

## ⟲ Previous-session review

Builds directly on the 2026-07-12 scoping card
(`.sessions/2026-07-12-mining-workflow-seam-scoping.md`), which deliberately
did NOT build a skeleton because the oracle answers neither D1 (which audit
schema) nor D2 (are item-grants audited) — building then would have invented
the audit contract by fiat under born-red. This session builds on the §5
recommended default the scoping doc raised for ratification: 11-field schema +
audit-everything, both kept explicitly REVERSIBLE and re-flagged in
`control/outbox.md` so the owner/lab call is preserved, not pre-empted. The
purity guard (`tests/mining/test_purity.py`, 19 modules) is honoured by keeping
the seam top-level; a new `services/tests` suite carries its own floor with no
existing floor touched.
