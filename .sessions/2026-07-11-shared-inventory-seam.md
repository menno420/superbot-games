# 2026-07-11 · Shared inventory seam (games/shared/inventory/) — contract migration PR-1

> **Status:** `complete`
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

- **`games/shared/inventory/` pure package** (mirrors `games/shared/encounter/`), all
  stdlib-only, no Discord/DB/IO:
  - **`interface.py`** — the design doc §2 types as frozen dataclasses +
    `@runtime_checkable` Protocols: `ItemId` (neutral str alias) with an
    `is_valid_item_id`/`item_id` validator that rejects non-neutral display nouns
    (`"diamond"`, `"Lucky Charm"`); `ItemMeta` (the only re-theme surface, Q-0267);
    `Stack(item, qty, attrs)` — `attrs` normalised to a read-only proxy, `qty` may be
    negative (a loss, §2c); `ProgressionDelta(global_xp, game_xp, currency, capability)`;
    `Grant(items, progression)` — the ONE reward shape; `CapStatus(used, cap)` with
    `remaining`/`at_cap`; the `ItemCatalog` / `InventoryView` / `CapacityPolicy`
    Protocols. Pure helpers: `EMPTY_GRANT`/`empty_grant`, `merge_grants`, `add_delta`
    (associative, capability last-writer-wins), `scale_delta`.
  - **`reference.py`** — `DictItemCatalog`, an IMMUTABLE dict-backed `ReferenceInventory`
    (`add`/`add_grant` return a NEW inventory — pure, no in-place mutation; negative qty
    clamps at 0), and `DefaultCapacityPolicy` pinned to mining's `PACK_SOFT_CAP=40`
    (distinct-types soft cap, §7.5 regression pin).
  - **`conformance.py`** — the reusable §7 suite future adapters re-run: round-trip
    identity (§7.1), no-spend-lever (§7.2, introspects the types for a coin/purchase/pay
    param), determinism pass-through (§7.3), theme-data-only nouns under a re-skin
    (§7.4), capacity-in-distinct-types (§7.5), plus a `run_conformance` entry point.
  - **`README.md` + `__init__.py`** — public-surface note, the claim/announce rule, the
    public API, and the invariant list.
- **`tests/shared/inventory/`** — 57 tests (collected by the existing `tests/` gate):
  `test_interface.py` (construction/frozen-ness/id-validation/helper algebra),
  `test_reference.py` (round-trips, catalog lookup, cap under/at/over, Protocol
  `isinstance`), `test_conformance.py` (the §7 suite run against the reference impls +
  its failure modes). Full suite **204 passed** (73 mining + 26 fishing + 48 exploration
  + 57 inventory).
- **CI floor** bumped `147 → 204` in `.github/workflows/tests.yml` (comment + `-lt`
  check, `+ 57 (tests/shared/inventory/)`).
- **Claim + announce** — `docs/claims/world-games-inventory-seam.md` (`binding`,
  supersedes the advisory contract claim), linked from `docs/current-state.md`; the new
  interface announced in `control/status.md` (shared-interface-change rule).
- **Deferred (not resolved here):** the three ⚑ owner-decisions in the design doc §6
  (neutral-id namespace / mining rename; whether `currency` belongs in the contract; one
  shared vs per-system catalogs) and all per-system adapters (PRs 2..6).

### Design-doc conformance / spec gaps filled

Implemented §2 verbatim. Two minimal gap-fills, both noted in code: (1) §2b's docstring
says `qty >= 1` but §2c/§6-D explicitly allow a negative `qty` for a loss — resolved
toward §2c (no positivity check; the contract carries, never polices), documented on
`Stack`. (2) §2d named only the two scalar `InventoryView` queries (`held`,
`distinct_types`); added a `stacks()` method so the conformance suite can enumerate a hold
without knowing its ids up front — flagged as a gap-fill in the Protocol docstring.

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
