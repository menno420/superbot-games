# 2026-07-11 · Shared inventory seam (games/shared/inventory/) — contract migration PR-1

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus · 2026-07-11T00:48:52Z · shared inventory seam (contract migration PR-1)

## Goal

Implement **PR-1** of the unified inventory/resource contract migration
(`docs/design/world-inventory-resource-contract.md` §4): stand up the pure-domain
foundation package `games/shared/inventory/` — the §2 types + a reference/conformance
layer — as ONE merged-on-green PR. Additive only: this package is a NEW shared surface
that nothing imports yet (correct for a foundation slice). Scope is strictly the §2
contract; NO per-system adapter (mining/fishing/exploration wiring is PR-2..PR-6) and the
three ⚑ owner-decisions in §6 stay deferred, not resolved here.

The slice must:

- Deliver the §2 types EXACTLY as frozen dataclasses + `@runtime_checkable` Protocols,
  stdlib-only, pure/deterministic, no Discord/DB/IO — mirroring the claim-first
  `games/shared/encounter/` seam's style, docstrings, and interface-change-announcement
  rule.
- Keep every player-visible noun OUT of code (Q-0267): the contract is mechanics only;
  catalogs carry nouns as injected data.
- Carry values, never roll them (no pay-to-win, Q-0039/Q-0190): the contract is a
  transport, exposing no luck/pay lever.
- Ship a reusable **conformance suite** (spec §7) that future adapters re-use to prove
  round-trip identity, no-spend-lever, determinism, theme-data-only nouns, and capacity
  semantics — pinned against the reference impls.
- Claim the shared surface first (`docs/claims/world-games-inventory-seam.md`), announce
  the new interface in `control/status.md`, and bump the CI collected-count floor for the
  new tests under `tests/shared/inventory/`.

## What shipped

<!-- filled in the last content commit when code lands -->
- (born-red — populated on the final content commit)

## 💡 Session idea

`games/shared/inventory/` is the third claim-first shared seam to follow the exact same
skeleton (`interface.py` frozen dataclasses + `@runtime_checkable` Protocol + a
`reference.py` conformance impl + ALLOWED constants), after `games/shared/encounter/` and
the pattern the fishing/mining domains reach for independently. The recurring shape —
**neutral-id mechanics + data-only noun tables + a Protocol seam with a reference impl** —
is now witnessed enough times to be a documented house style, not an ad-hoc choice. Worth
a short `docs/patterns/claim-first-shared-seam.md` that codifies the skeleton so PR-2..PR-6
(and any later shared surface) start from a template instead of re-deriving it from the
encounter seam each time.

## ⟲ Previous-session review

The theme-slot audit (#28) and the inventory-contract design doc (#26) set this PR up
precisely: the audit's §1a finding (item identity = display noun as the key) is exactly
the Q-0267 gap the `ItemId`/`ItemMeta` split closes, and the design doc §2 fully specified
the types so this slice implements rather than invents. The design doc's own discipline —
a `plan` badge that must flip to shipped or it's silent drift — is honoured: this card is
born-red and flips to `complete` only when the code lands, and the doc §4 already framed
PR-1 as additive-only (nothing imports the seam yet), which this slice respects verbatim
so no downstream system is perturbed.
