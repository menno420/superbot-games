# 2026-07-11 · Unified inventory/resource contract (design)

> **Status:** `complete`
>
> 📊 Model: Claude Opus · 2026-07-11T00:26:40Z · design doc unifying item/reward/inventory across world games

## Goal

Deliver ONE merged-on-green PR carrying a **plan/reference design doc**,
`docs/design/world-inventory-resource-contract.md`, that unifies how the world-games
systems (mining, exploration/quest, fishing, shared/encounter) represent an **item**, a
**quantity/stack**, a **reward/grant**, and **inventory capacity**. This is a PLAN doc —
NOT an implementation. No system code, README, tests.yml, or inbox is touched. The doc
must be grounded in the real, divergent representations found in the code (file:line
citations), propose a single pure-domain contract (frozen dataclasses / Protocol,
plugin-package-friendly, Q-0267 nouns-in-data), argue for `games/shared/inventory/` as its
home (claim-first shared surface), lay out an incremental per-system migration path, hold
the integrity floor (deterministic, no pay-to-win, theme-ready), flag genuine
owner-decisions, and specify a shared conformance test each adapter runs.

## What shipped

- **`docs/design/world-inventory-resource-contract.md`** — a PLAN/reference design doc
  (NO code refactor). Seven sections mirroring the `docs/design/` skeleton:
  - **§1 Problem** — the load-bearing section. Read the real code and enumerated SIX
    divergent reward shapes across four systems, each with file:line: mining
    `Reward(item:str, amount:int)` (`encounters.py:129-134`), mining dig
    `(ore, amount)` (`rewards.py:90-96`), mining explore `(desc, item|None, delta)` with
    negative deltas (`rewards.py:137-155`), fishing `Catch(species_id, size)`
    (`catch.py:90-95`), quest `RewardBundle(global_xp, game_xp, currency, capability)`
    (`models.py:56-63`), and the shared encounter free-form `payload: Mapping[str,object]`
    (`interface.py:38-45`). Also: mining item identity = lowercased **display string** as
    catalog+inventory+player key (`items.py:66`, Q-0267 violation) vs fishing's correct
    neutral `species_id` + data table (`species.py:46-79`); inventory everywhere a bare
    `dict[str,int]`; capacity in distinct-types soft-cap (`capacity.py:27,40`); and the
    existing `register_fish_species` bridge drops the neutral id (`items.py:282-304`).
  - **§2 Proposed contract** — one pure vocab: `ItemId` (neutral) + `ItemMeta` +
    `ItemCatalog` Protocol (nouns in data), `Stack(item, qty, attrs)` (fish `size` rides
    as an attr), `ProgressionDelta` + `Grant(items, progression)` (ONE reward shape that
    subsumes all six), and `InventoryView`/`CapacityPolicy` Protocols + `CapStatus` with
    the host store left open.
  - **§3 Where it lives** — `games/shared/inventory/` claim-first, mirroring the
    `games/shared/encounter/` seam; one thin adapter per system (extend-not-duplicate);
    interface-change announcement requirement noted.
  - **§4 Migration** — 6 incremental PRs, dependency-first, each merged-on-green, no
    big-bang.
  - **§5 Integrity floor** — determinism preserved, no-pay-to-win (contract CARRIES
    amounts, never computes them; each system stays sim-pinned), Q-0267 theme-readiness
    (fixes mining's violation).
  - **§6 Open questions** — 4 reversible D-calls vs 3 ⚑ owner-decisions (neutral-id
    namespace + mining key rename; whether `currency` belongs in the shared contract;
    one shared catalog vs per-system).
  - **§7 Verification** — a shared `conformance.py` each adapter runs (round-trip
    identity, no-spend-lever, determinism pass-through, theme-data-only nouns, capacity
    semantics), mirroring mining's existing invariant tests.
- **`docs/claims/world-games-inventory-contract.md`** — ADVISORY claim (design-only, no
  code change), reserving the prospective `games/shared/inventory/` path per
  `docs/lanes.md`.
- **`.sessions/2026-07-11-inventory-resource-contract.md`** — this born-red heartbeat.
- **Collection unbroken:** `python3 -m pytest tests/ games/exploration/tests/ -q` →
  **147 passed** (73 mining + 26 fishing + 48 exploration — matches the #24/#25 floor).
  No system code, README, tests.yml, or inbox touched.

## 💡 Session idea

The `Stack.attrs` escape hatch (a `Mapping` for per-instance magnitudes like a fish's
`size`) is the seam that lets fungible stacks and non-fungible instances share one type.
If it grows a second attr (durability? enchant?) that's the signal a system wants
per-instance items — worth a follow-up idea note on when to promote `attrs` to typed
fields vs keep it open.

## ⟲ Previous-session review

The fishing skeleton (#25) already did the Q-0267 thing right (neutral `species_id` +
`species.py` data table), while the older mining port did NOT (display strings as keys).
This contract's §1a makes that split the central finding — the newer system is the model,
the older one is the migration target. The `games/shared/encounter/` seam (Protocol +
reference impl + claim-first) is the exact structural precedent this contract copies, so
"where it lives" wasn't invented — it's the established shared-surface pattern.
