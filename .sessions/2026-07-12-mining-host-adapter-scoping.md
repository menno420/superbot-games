# 2026-07-12 · rung-3 host-adapter scoping (mining) + ⚑ packaging/hermeticity decision

> **Status:** `complete`
>
> 📊 Model: Opus 4.8 · 2026-07-12T21:16:23Z · rung-3 host-adapter scoping

## 💡 Session idea

This session scopes whether a rung-3 host-adapter is buildable against the
binding plugin contract (superbot-next `docs/game-plugin-contract.md`, D-0056):
the contract does **not** require `@workflow` (the hello exemplar is panel-only),
so a contract-proving skeleton is technically possible — but a meaningful mining
adapter wraps the parked rung-2 workflow op, and even a bare skeleton forces
packaging / hermeticity / host-pin preconditions on sbg. So we scope and flag
the packaging/hermeticity decision rather than build.

## ⟲ Previous-session review

Builds on PR #65, whose truth-stamp + claims sweep landed READY + green, and on
PRs #59 / #60 (plugin-contract binding correction + rung-2 workflow-seam scoping)
which the owner merged — establishing the ladder ordering
(PURE CORE → WORKFLOW → HOST) this rung-3 doc continues.
