# 2026-07-11 · Fishing → shared inventory adapter — contract migration PR-2

> **Status:** `red`
>
> 📊 Model: Claude Opus · 2026-07-11T01:13:29Z · fishing→shared-inventory adapter (contract migration PR-2)

## Goal

Deliver **PR-2** of the unified inventory/resource contract migration
(`docs/design/world-inventory-resource-contract.md` §4): a thin, pure **adapter** mapping
fishing's `Catch`/`CastOutcome` output onto the already-shipped `games/shared/inventory/`
§2 contract (PR #29), exercised by the shipped §7 conformance suite — as ONE merged-on-green
PR. Additive only: NEW adapter package, no change to `games/fishing/core/` internals, none
to `games/shared/inventory/`, none to mining.

The slice must:

- Add a pure, deterministic, stdlib-only adapter package (`games/fishing/inventory/`) that
  builds a fishing `ItemCatalog` from `species.py` DATA and maps `Catch → Stack`,
  `Catch → Grant`, `CastOutcome → Grant` (no bite → `EMPTY_GRANT`).
- Map each neutral `species_id` to a namespaced `ItemId` `fish.<species_id>` at the adapter
  boundary ONLY — no rename of any fishing/mining internal id (decide-and-flag, reversible).
- Keep every player-visible noun in `species.py`; the adapter only reads that data and
  relays it (Q-0267 — introduces NO new hardcoded noun).
- Carry values, never roll/scale them by a pay lever (Q-0039/Q-0190).
- Pass the shipped §7 `run_conformance` suite against the fishing catalog + a
  `ReferenceInventory` seeded from adapter grants.
- Bump the CI collected-count floor for the net-new `tests/fishing/` tests.

## Decide-and-flag (reversible, no owner sign-off)

- **Per-system catalog for now** — a fishing-local `ItemCatalog` built from `species.py`,
  NOT a global merged catalog. The §6 "one shared vs per-system catalog" owner-decision
  stays DEFERRED; per-system is the doc's own assumption and is reversible.
- **`fish.<species_id>` namespace mapping** at the adapter boundary only — no persisted id
  changes, no internal rename. The §6 ⚑ neutral-id-namespace/mining-rename owner-decision
  stays DEFERRED; this maps old↔new at the seam and is reversible.

## What shipped

_(filled in the last content commit)_

## 💡 Session idea

_(filled in the last content commit)_

## ⟲ Previous-session review

PR-1 (#29) stood up `games/shared/inventory/` with a reusable §7 conformance suite
explicitly designed for adapter PRs to re-import — this PR is the first consumer, proving
that discipline holds. The design doc §4 sequenced fishing first *because* it is already
neutral-id (`species.py`), so PR-2 is a pure mapping with no Q-0267 remediation, unlike the
mining catalog PR-3 that follows. This card is born-red and flips to `complete` only when
the adapter lands green.
