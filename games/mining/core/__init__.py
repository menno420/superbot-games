"""Mining domain — pure, shared game logic (no Discord, no DB, no views).

Ported VERBATIM from ``menno420/superbot`` ``disbot/utils/mining/*`` +
``disbot/utils/equipment.py`` (the pure-domain "spec is the shipped behaviour").
Every formula and balance constant is preserved unchanged (sim-pinned upstream;
pinned here as *preserved-from-oracle, unchanged* — no new tuning). stdlib +
dataclasses/enum/random only.

One module is **new design, not an oracle port**: ``encounters`` (the grid-encounters
extension's first slice, ``docs/design/mining-grid-encounters.md``). Its balance
numbers are freshly **sim-pinned** in-repo (``games/mining/sim/encounters_sim.py``),
not preserved-from-oracle — the only module here whose constants originate locally.

Two fishing couplings from the oracle are severed for the mining-only port
(see ``docs/design/mining-plugin-layout.md``):
    * ``items`` no longer imports ``utils.fishing.fish.SPECIES`` — fish rows fold
      in through the documented ``items.register_fish_species`` injection point.
    * ``structures`` drops the four fishing structures (tide pool / dock /
      boathouse / fishery), keeping forge / home / campfire.

Modules:
    equipment    — cross-game gear→stats model (EffectiveStats, tiers, sets)
    items        — item taxonomy (kinds, tiers, values, tool ladders)
    rewards      — mining/harvest loot tables (injectable RNG)
    world        — depth↔biome model + descent gating (z axis)
    exploration  — loadout-aware exploration outcome engine (injectable RNG)
    grid         — seed-deterministic procedural grid (x/y at a depth)
    encounters   — live-rollable encounter layer over the grid (feature-keyed; NEW design)
    energy       — passive-regen energy "fuel" model
    capacity     — pack soft-cap + vault capacity/upgrade math
    skills       — 4-branch capped skill tree → stats
    character    — gear + skills merge point
    titles       — earned-title catalogue (derived from progression)
    market       — pure pricing (sell values, the gear shop)
    recipes      — crafting recipes (in-code defaults + injection; no file IO)
    workshop     — durability/repair/craft helpers
    structures   — buildable structures (forge / home / campfire) + forge gate
    taxonomy     — 3-layer menu grouping (Category→Type→Variant)
    loadout      — best-loadout ("Equip Best") set-aware picker
    names        — fuzzy item-name resolver
"""
