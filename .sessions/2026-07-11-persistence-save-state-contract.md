# 2026-07-11 · Persistence & save-state contract (world-games seat)

> **Status:** ✅ `complete`
>
> 📊 Model: Opus 4.8 · 2026-07-11T17:44:28Z · persistence save-state contract

## Goal

Ship the save-state contract + owner transfer-policy mapping doc: give the
rebuilt host (`menno420/superbot-next`) a fixed, versioned contract to implement
storage against, and formalize the owner's spoken cross-server onboarding
transfer directive into named, checkable invariants. Docs-only slice — no
storage backend, no I/O, no balance numbers.

## What shipped

- **`docs/design/persistence-design.md`** — the contract doc:
  - versioned, per-domain-namespaced `PlayerState` schema (envelope +
    `shared-inventory` / `mining` / `exploration` / `fishing` / `dnd`
    namespaces, each with its own inner `v`);
  - deterministic canonical-JSON serialization rules (sorted keys, no
    insignificant whitespace, integer economy fields, `Stack[]` in `ItemId`
    order);
  - forward-only, two-tier, idempotent migration story with an unknown-namespace
    preserve-verbatim rule and new-domain onboarding;
  - the owner cross-server transfer directive as three named invariants —
    `TRANSFER_CONSERVATION`, `TRANSFER_FRACTION_CAP`, `NO_INSTANT_RICHEST` —
    with a precedence rule, the exact percentages left as OWNER-DECIDES
    (sim-pinned at implementation), and a clearly NOT-COMMITTED sketch of what a
    fair player-to-player trading proof would require.
  - Aligned with the shared `Grant/Stack/ItemId/ProgressionDelta` contract; host
    owns storage, this repo owns the shape.
- **`docs/design/shared-index.md`** — linked the new doc so the docs-gate
  reachability BFS reaches it (persistence is a cross-cutting/shared concern).

No `games/**`, no workflow, no `control/**`, no `docs/current-state.md` touched.

## 💡 Session idea

A contract-only doc earns its keep when every deferred number is named as an
explicit OWNER-DECIDES line rather than silently omitted — the named invariant
(`TRANSFER_CONSERVATION`) plus its open-question list is what lets the host build
the mechanism now and let the owner sim-pin the constant later, without the two
decisions blocking each other.

## ⟲ Previous-session review

Builds on the shared-inventory seam work (`2026-07-11-shared-inventory-seam.md`)
and the `world-inventory-resource-contract` it stood up: this contract consumes
that doc's `Grant/Stack/ItemId/ProgressionDelta` shapes directly rather than
re-defining wealth, so `TRANSFER_CONSERVATION` has a single source of truth
(currency/XP stored once in `shared-inventory`, referenced not copied).

## Guard recipe

Docs-gate reachability is the guard for this slice: a new design doc is invisible
to `bootstrap.py check --strict` until it is linked from the right `*-index.md`.
The recipe — for any NEW `docs/design/*.md`, add its relative link to the owning
domain index (persistence = cross-cutting -> `shared-index.md`) in the same list
style as existing entries, then re-run `bootstrap.py check --strict` and confirm
exit 0 BEFORE commit; never edit `docs/current-state.md` directly.
