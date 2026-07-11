# superbot-games · status

updated: 2026-07-11T00:31:33Z
phase: unified inventory/resource contract DESIGN DOC shipped — READY PR to main (green-pending); plan doc only, no system code refactored
health: green — full suite 147 pure-domain tests pass (99 tests/ [73 mining + 26 fishing] + 48 games/exploration/tests/); no system code/README/tests.yml/inbox touched
last-shipped: (pending PR #) — docs/design/world-inventory-resource-contract.md
orders: acked=001,002 done=001,002

## Boot record
Landed on origin/main HEAD `9b09b99` (PR #25 fishing skeleton merged; PR #24 unified
single-seat base merged). Branch `feat/inventory-resource-contract` off origin/main.
This seat owns all of `games/**` and reports here (single-seat status file).

## Last shipped — unified inventory/resource contract (design doc, 2026-07-11)
- **`docs/design/world-inventory-resource-contract.md`** — a PLAN/reference doc (NOT an
  implementation; no system code refactored). Enumerates the SIX divergent reward shapes
  across four systems with file:line citations and proposes ONE pure-domain contract.
  - **The divergence (§1, load-bearing, all cited):** mining `Reward(item:str,amount:int)`
    (`encounters.py:129-134`), mining dig `(ore,amount)` (`rewards.py:90-96`), mining
    explore `(desc,item|None,delta<0)` (`rewards.py:137-155`), fishing
    `Catch(species_id,size)` (`catch.py:90-95`), quest `RewardBundle(global_xp,game_xp,
    currency,capability)` (`models.py:56-63`), shared encounter free-form
    `payload:Mapping[str,object]` (`interface.py:38-45`). Plus: mining item identity =
    lowercased display string as catalog+inventory+player key (`items.py:66`) — a Q-0267
    violation — vs fishing's correct neutral `species_id`+data table (`species.py`);
    inventory everywhere a bare `dict[str,int]`; capacity in distinct-types soft-cap
    (`capacity.py:27,40`); `register_fish_species` bridge drops the neutral id
    (`items.py:282-304`).
  - **The contract (§2):** `ItemId` (neutral) + `ItemMeta` + `ItemCatalog` Protocol
    (nouns-in-data, Q-0267); `Stack(item,qty,attrs)` (fish size as an attr);
    `ProgressionDelta` + `Grant(items,progression)` — one reward shape subsuming all six;
    `InventoryView`/`CapacityPolicy` Protocols + `CapStatus`, host store left open.
  - **Home (§3):** `games/shared/inventory/` claim-first, mirroring the shipped
    `games/shared/encounter/` seam; one thin adapter per system (extend-not-duplicate).
  - **Migration (§4):** 6 incremental merged-on-green PRs, dependency-first, no big-bang.
  - **Integrity (§5):** determinism preserved; no-pay-to-win (contract CARRIES amounts,
    never computes them — each system stays sim-pinned); Q-0267 theme-readiness.
- **`docs/claims/world-games-inventory-contract.md`** — ADVISORY claim (design-only, no
  code change), reserving the prospective `games/shared/inventory/` path per docs/lanes.md.
- **Collection:** `python3 -m pytest tests/ games/exploration/tests/ -q` → **147 passed**
  (matches the #24/#25 floor). This is a docs-only PR — no code, README, tests.yml, or
  inbox edited.

## ⚑ needs-owner
- **PR owner-click.** If branch protection walls the merge of this agent-authored,
  human-unreviewed PR (the expected Self-Approval / Merge-Without-Review wall, documented
  in `docs/retro/next-boot-mining-2026-07-09.md:23-28`), the OWNER clicks Merge once CI is
  green. Terminal state for this work is "PR READY + CI green + ⚑ owner-click".
- **Design decisions flagged in doc §6** (not blocking this doc; decide before the
  implementation slices): (a) neutral-id namespace + whether to rename mining's persisted
  inventory keys; (b) whether `currency` belongs in the shared contract at all; (c) one
  shared `ItemCatalog` vs per-system catalogs.

## Orders
`orders: acked=001,002 done=001,002`
- ORDER 001 — done (merged #24). ORDER 002 — done (superseded by Q-0265, see history).

## Queue (inherited)
- done: fishing walking skeleton (#25); unified inventory/resource contract design doc
  (this PR).
- next: implement migration PR-1 (stand up `games/shared/inventory/` seam) per the doc
  §4; then theme-slot audit per Q-0267.

## Notes
blockers: none. This is a plan doc — the actual `games/shared/inventory/` seam is a
later, separate merged-on-green PR (doc §4 step PR-1), at which point the advisory claim
is superseded by a real claim + the interface-change announcement (docs/lanes.md:28-30).
