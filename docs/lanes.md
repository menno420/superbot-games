# Lanes — the cohabitation contract

> **⟵ GEN-1 HISTORY.** The two-lane split is archived; the single world-games seat owns `games/**` and the unified `control/inbox.md` + `control/status.md`. Read this as an archive, do not resurrect the split.

> **Status:** `binding`

> **BINDING on both resident Projects.** Two autonomous Projects share this repo; lanes
> are what keep them from colliding. When in doubt: your lane only.

## Ownership

| Path | Owner |
|---|---|
| `games/mining/**` · `docs/founding-plan-mining.md` · `control/status-mining.md` | **mining Project only** |
| `games/exploration/**` · `docs/founding-plan-exploration.md` · `control/status-exploration.md` | **exploration Project only** |
| `games/shared/**` (encounter engine, shared domain code) | **claim-first** (below) |
| `control/inbox-mining.md` · `control/inbox-exploration.md` | manager only (one writer per file) |

**One PR lane each** — a PR touches only your own lane (plus shared paths you have
claimed). **Never edit the other Project's lane.**

## `games/shared/**` — claim-first

1. Before touching anything under `games/shared/`, create
   `docs/claims/<project>-<topic>.md` (one line: project · paths · what · date). If a
   conflicting claim exists, coordinate via your status file or wait.
2. **Delete the claim file at session end.**
3. **Interface changes** — any change to a shared engine's public surface — are announced
   in **BOTH** status files (a note in `control/status-mining.md` AND
   `control/status-exploration.md`) in the same session they ship.

Mining implements the shared encounter engine first; exploration consumes it.

## Kit adoption — ONCE

substrate-kit is adopted **once**, by whichever Project runs first. The second Project
**verifies** the engagement (`check --strict` green) instead of re-adopting — never a
second adopt over a live `.substrate/`.

## Shared files

`README.md`, `.substrate/**`, and the session journal are common ground: they follow the
kit's own concurrent-session conventions (per-file session logs, append-only ledgers, one
claim file per lane). Edit shared files by section, keep changes additive, and prefer your
own status file for anything Project-specific.
