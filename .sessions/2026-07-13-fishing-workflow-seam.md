# 2026-07-13 · fishing WORKFLOW audited seam (rung 2 · build)

> **Status:** ✅ `complete`
>
> 📊 Model: Opus 4.8 · 2026-07-13T01:10:03Z · rung-2 fishing workflow seam

## 💡 Session idea

Build rung 2 of the fishing ladder — the WORKFLOW audited seam — mirroring the
just-landed mining seam (`services/mining_workflow.py`, PR #68). The seam is a
top-level `services/fishing_workflow.py`: it reads a mutable `FishingState`,
calls the pure core (`games.fishing.core.catch.resolve_cast`) to decide, mutates
the state (debit energy, fold the catch into the haul through the shared
inventory adapter), builds the oracle's 11-field structural `AuditRecord` (D1),
and calls an injected `Sink` for the one state-changing action — `cast` (D2). It
REUSES the game-neutral `services/audit.py` types (`AuditRecord` / `Sink` /
`InMemorySink`) so fishing and mining share one audit contract without welding
the two games together — the seam imports from `services.audit`, NEVER from
`services/mining_workflow.py`. Fishing has ONE decide-fn, so ONE audited action:
there is no sell/buy/move leg because no fishing economy exists yet (the shared
`Grant` carries an empty `ProgressionDelta`); those future actions are gated on
that economy gap and filed as SIM-REQUESTs in `control/outbox.md`, not built. The
seam lives OUTSIDE `games/fishing/core/`, so the pure core stays pure — and this
slice ADDS the missing `tests/fishing/test_purity.py` guard (mirroring
`tests/mining/test_purity.py`), which ALLOWS the core's legitimate shared
`games.mining.core` energy/stat reuse and forbids only the host/db/service
layers. Every balance number/noun is quoted VERBATIM from the core — no numbers
invented.

## ⟲ Previous-session review

Builds directly on the 2026-07-13 mining WORKFLOW seam (PR #68), which factored
the audit record + sink port into a game-neutral `services/audit.py` expressly so
"the next-slice fishing seam reuses them without coupling." This session is that
next slice: it consumes that neutral contract unchanged (no edit to
`services/audit.py`, no import of `services/mining_workflow.py`) and mirrors the
mining suite's two required guarantees — one well-formed 11-field audit record
per state-changing action (a too-tired no-op records nothing) and a core-stays-
pure guard. The mining slice pinned its core at 19 modules and carried its floor
in the shared `services/tests` suite; this slice pins the fishing core at 4
modules, bumps the `services/tests` floor for its new tests, and bumps the
`tests/fishing` floor for the new purity guard — no other floor touched. The
outbox APPENDS fishing SIM-REQUESTs beneath the mining entries (one-writer lane,
mining entries preserved); `control/status.md` / `control/inbox.md` are untouched.
