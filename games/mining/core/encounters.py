"""Grid encounters — a live-rollable encounter layer over the seeded grid (pure).

This is the **first named-next extension** past the pure mining port
(``docs/design/mining-plugin-layout.md`` §7 · Q-0198): sparse, feature-keyed
*encounters* layered on top of the seed-deterministic :mod:`games.mining.core.grid`.

Where :func:`grid.cell_at` decides a cell's *content* (a richness multiplier + a
featured ore, a pure function of ``(seed, x, y, z)``), this module decides *what
happens* when a player acts on that cell — a hazard to fight, a loot cache to
crack, a rich vein to work, or (the common case) nothing.

Design shape (all decisions recorded in the design doc §7):

* **Feature-keyed archetypes.** The encounter *kind* is selected from the cell's
  :class:`grid.CellFeature` alone (never from stats), so two players standing on
  the same cell face the same *category* of encounter:

  =============  =========================================================
  CellFeature    encounter kind (on trigger)
  =============  =========================================================
  ``NORMAL``     ``HAZARD``  — a cave creature / rockfall, resolved via combat
  ``RICH``       ``RICH_VEIN`` — a richer ore pocket (no combat)
  ``TREASURE``   ``LOOT_CACHE`` — a packed cache of the cell's featured ore
  ``BARREN``     never triggers (always ``NONE``)
  =============  =========================================================

* **Sparse by construction.** Each action first rolls a *trigger* keyed on the
  feature (and, for hazards, gently depth-scaled — "deeper = more dangerous").
  Most actions on most cells return ``EncounterKind.NONE`` — the baseline.

* **Deterministic by default, live-roll by injection.** ``rng=None`` derives a
  deterministic stream from the grid's splitmix64 ``(seed, x, y, z)`` convention,
  so ``(seed, x, y, z)`` → the *same* encounter (reproducible · testable · matches
  grid determinism). A host that wants the founding "live-roll" variance (two
  players' runs differ) injects its **own** ``rng`` seeded with player/action
  entropy — the resolver is pure either way.

* **Combat reuses the shared stat model.** Hazards resolve against
  :class:`equipment.EffectiveStats` ``damage`` / ``defense`` / ``max_health`` — the
  *same* combat stats deathmatch reads. A bare-handed miner can still fight weak
  creatures (a base attack/HP floor); earned gear only ever helps.

* **No parallel economy, no pay-to-win.** Rewards are drawn from the existing
  ore/depth tables (:func:`rewards.ore_weights_for_depth`, the cell's featured
  resource). The resolver takes **no** coin/purchase/spend input — the only inputs
  that improve an outcome are ``EffectiveStats`` (gear/skills *earned in-domain*).

* **Pure data, no IO.** :class:`EncounterOutcome` is a frozen record of *what
  happened* (kind, rewards, damage taken, energy cost, resolution). Applying it to
  a player — decrementing energy, adding loot, docking HP — is the workflow layer's
  job; this module never writes state.

**Additive-safety invariant** (the domain's recurring rule): a baseline input —
zero :class:`EffectiveStats`, a non-triggering cell — yields a fixed baseline
``EncounterKind.NONE`` outcome *independent of stats*, and stats only ever improve
a hazard (more damage → never fewer wins; more defense → never more damage taken;
more health → never more losses). Asserted in ``tests/mining/test_encounters.py``.

**Deferred to later slices** (design doc §7): multi-turn combat depth, a hard
depth-gate + per-action cooldown (both *stateful across actions* → a host/workflow
concern, not pure-domain), image ``ResultRender``, and host wiring.

Pure: stdlib + dataclasses/enum/random only — no Discord, no DB, no IO.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum

from games.mining.core import energy as energy_model
from games.mining.core import equipment, grid, rewards

# 64-bit mask — mirrors grid._cell_seed's convention (Python ints are unbounded).
_MASK = (1 << 64) - 1

# A domain salt so the encounter stream is *independent* of the grid's
# feature-selection stream at the same cell (mixing the same base seed twice with
# no salt would correlate the two rolls). Mirrors grid._cell_seed's splitmix64
# step; kept self-contained here to avoid depending on a private grid helper.
_ENCOUNTER_SALT = 0xD1B54A32D192ED03


def _cell_seed(seed: int, x: int, y: int, z: int) -> int:
    """Stable 64-bit hash of ``(seed, x, y, z)`` — mirrors ``grid._cell_seed``.

    Integer-only splitmix64 mixing, so it never depends on Python's per-process
    string-hash randomisation; negative coordinates wrap deterministically.
    """
    h = seed & _MASK
    for value in (x, y, z):
        h = (h ^ (value & _MASK)) & _MASK
        h = (h + 0x9E3779B97F4A7C15 + ((h << 6) & _MASK) + (h >> 2)) & _MASK
    return h


def encounter_seed(seed: int, x: int, y: int, z: int) -> int:
    """Deterministic per-cell encounter seed — a distinct stream from the grid's.

    Reuses the grid's ``(seed, x, y, z)`` splitmix64 convention, then mixes a
    domain salt so the encounter roll does not correlate with the cell's feature
    selection. Process-independent (unit-tested via a subprocess check).
    """
    h = (_cell_seed(seed, x, y, z) ^ _ENCOUNTER_SALT) & _MASK
    h = (h + 0x9E3779B97F4A7C15 + ((h << 6) & _MASK) + (h >> 2)) & _MASK
    return h


class EncounterKind(Enum):
    """What the player ran into. ``NONE`` is the sparse-by-design baseline."""

    NONE = "none"
    HAZARD = "hazard"  # combat — cave creature / rockfall (NORMAL cells)
    LOOT_CACHE = "loot_cache"  # a packed cache (TREASURE cells)
    RICH_VEIN = "rich_vein"  # a richer ore pocket, no combat (RICH cells)


class Resolution(Enum):
    """How a triggered encounter turned out (drives the sim's win/flee/lose rates)."""

    NONE = "none"  # no encounter triggered
    COLLECTED = "collected"  # loot cache / rich vein worked
    WON = "won"  # hazard defeated
    FLED = "fled"  # hazard escaped (survivable) — no loot, took a hit
    LOST = "lost"  # hazard overwhelmed the player — full hit, no loot


@dataclass(frozen=True)
class Reward:
    """One item reward from an encounter (reuses the existing item vocabulary)."""

    item: str
    amount: int


@dataclass(frozen=True)
class EncounterOutcome:
    """The pure result of resolving one encounter — a record of state *deltas*.

    Carries no side effects: the workflow layer applies ``rewards`` (add to
    inventory), ``damage_taken`` (dock HP), and ``energy_cost`` (debit energy).
    """

    kind: EncounterKind
    resolution: Resolution
    narration: str
    rewards: tuple[Reward, ...] = field(default_factory=tuple)
    damage_taken: int = 0
    energy_cost: int = 0


# The invariant baseline — a non-encounter. Byte-identical regardless of stats,
# energy, or depth (stats can never *manufacture* an encounter). This object is
# the additive-safety anchor the tests pin.
_NONE_OUTCOME = EncounterOutcome(
    kind=EncounterKind.NONE,
    resolution=Resolution.NONE,
    narration="The passage is quiet — nothing stirs.",
)


# ---------------------------------------------------------------------------
# Sim-pinned tunables. Every number below is justified by a committed sim run
# (games/mining/sim/encounters_sim.py) whose output + bounds live in
# docs/design/mining-grid-encounters.md. New design — NOT preserved-from-oracle.
# ---------------------------------------------------------------------------

# --- Trigger chances (per action, keyed on the cell's feature) ---------------
# Feature weights are 70/10/18/2 (NORMAL/RICH/BARREN/TREASURE — grid.py), so the
# grid-wide encounter rate ≈ .70·hazard + .10·rich + .02·loot ≈ sparse ~10%.
LOOT_CACHE_CHANCE = 0.60  # a TREASURE cell is special → usually pays out
RICH_VEIN_CHANCE = 0.35  # a RICH cell → a bonus pocket about a third of the time
NORMAL_HAZARD_CHANCE = 0.07  # NORMAL cells (the bulk) → rare hazards
# Deeper = more dangerous: hazard chance grows with depth, capped so a deep run
# never becomes a hazard-every-step wall.
HAZARD_DEPTH_SCALE = 0.05  # +5% of the base chance per depth band
HAZARD_MAX_CHANCE = 0.25  # ceiling on the per-action hazard chance

# --- Hazard combat (single-exchange; multi-turn deferred) --------------------
# A bare-handed miner can still fight weak creatures; gear only ever helps.
BASE_PLAYER_DAMAGE = 8  # attack with no weapon equipped
BASE_PLAYER_HP = 20  # survivable buffer before max_health gear
# Monster stats scale with depth (z). toughness gates WON (you must out-damage
# it in one exchange); power gates the hit you take.
HAZARD_BASE_TOUGHNESS = 6.0
HAZARD_TOUGHNESS_PER_DEPTH = 2.0
HAZARD_BASE_POWER = 6.0
HAZARD_POWER_PER_DEPTH = 1.5
HAZARD_ROLL_SPREAD = 0.4  # ± fraction of monster stats rolled per encounter
# Damage fractions of the monster's power taken in each resolution.
GRAZE_FRACTION = 0.5  # a WON fight still costs a graze
FLEE_FRACTION = 0.5  # fleeing a survivable fight
# Energy the encounter costs to engage / escape.
HAZARD_ENERGY_COST = 3
FLEE_ENERGY_EXTRA = 1
# Ore dropped by a defeated hazard.
HAZARD_LOOT_MIN = 1
HAZARD_LOOT_MAX = 3

# --- Reward yields (ore drawn from the existing depth-weighted tables) --------
LOOT_CACHE_MIN = 3
LOOT_CACHE_MAX = 6
RICH_VEIN_MIN = 2
RICH_VEIN_MAX = 4
RICH_VEIN_ENERGY_COST = 1  # working the extra pocket costs a little energy


def _hazard_chance(z: int) -> float:
    """Per-action hazard chance on a NORMAL cell at depth *z* (capped)."""
    grown = NORMAL_HAZARD_CHANCE * (1.0 + max(0, z) * HAZARD_DEPTH_SCALE)
    return min(HAZARD_MAX_CHANCE, grown)


def _trigger(cell: grid.Cell, rng: random.Random) -> EncounterKind:
    """Roll whether — and which — encounter fires for one action on *cell*.

    Keyed on the cell's feature only (never on stats), so the *category* of
    encounter at a cell is stat-independent. Returns ``NONE`` when nothing fires.
    """
    feature = cell.feature
    if feature is grid.CellFeature.BARREN:
        return EncounterKind.NONE
    if feature is grid.CellFeature.TREASURE:
        return EncounterKind.LOOT_CACHE if rng.random() < LOOT_CACHE_CHANCE else EncounterKind.NONE
    if feature is grid.CellFeature.RICH:
        return EncounterKind.RICH_VEIN if rng.random() < RICH_VEIN_CHANCE else EncounterKind.NONE
    # NORMAL
    return EncounterKind.HAZARD if rng.random() < _hazard_chance(cell.z) else EncounterKind.NONE


def _draw_ore(z: int, rng: random.Random) -> str:
    """Pick an ore for a reward from the depth-weighted table (deeper = richer)."""
    weights = rewards.ore_weights_for_depth(z)
    ores = list(weights)
    return rng.choices(ores, weights=[weights[o] for o in ores], k=1)[0]


def _resolve_loot_cache(
    cell: grid.Cell,
    stats: equipment.EffectiveStats,
    rng: random.Random,
) -> EncounterOutcome:
    base = rng.randint(LOOT_CACHE_MIN, LOOT_CACHE_MAX)
    # richness (treasure = ×2) scales the haul; loot_bonus + luck are the *earned*
    # edge (a lucky charm), never a purchased one. luck=0/loot_bonus=0 → base only
    # (additive-safety).
    amount = round(base * cell.richness) + stats.loot_bonus + max(0, stats.luck)
    reward = Reward(cell.featured_resource, max(1, amount))
    return EncounterOutcome(
        kind=EncounterKind.LOOT_CACHE,
        resolution=Resolution.COLLECTED,
        narration=f"💰 A packed loot cache — you haul out {reward.amount} {reward.item}!",
        rewards=(reward,),
    )


def _resolve_rich_vein(
    cell: grid.Cell,
    stats: equipment.EffectiveStats,
    rng: random.Random,
) -> EncounterOutcome:
    base = rng.randint(RICH_VEIN_MIN, RICH_VEIN_MAX)
    amount = round(base * cell.richness) + stats.loot_bonus  # luck-neutral pocket
    reward = Reward(cell.featured_resource, max(1, amount))
    return EncounterOutcome(
        kind=EncounterKind.RICH_VEIN,
        resolution=Resolution.COLLECTED,
        narration=f"⛏️ A rich pocket opens up — {reward.amount} more {reward.item}.",
        rewards=(reward,),
        energy_cost=RICH_VEIN_ENERGY_COST,
    )


def _roll_monster(z: int, base: float, per_depth: float, rng: random.Random) -> int:
    """A depth-scaled monster stat with a symmetric ±``HAZARD_ROLL_SPREAD`` roll."""
    center = base + max(0, z) * per_depth
    factor = 1.0 + rng.uniform(-HAZARD_ROLL_SPREAD, HAZARD_ROLL_SPREAD)
    return max(1, round(center * factor))


def _resolve_hazard(
    cell: grid.Cell,
    stats: equipment.EffectiveStats,
    energy: int,
    rng: random.Random,
) -> EncounterOutcome:
    """Single-exchange hazard combat via EffectiveStats. Multi-turn is deferred.

    * **WON** — player damage ≥ monster toughness: kill it, take a graze (reduced
      by defense), gain ore loot.
    * **FLED** — can't out-damage it but would survive the hit: escape, take a
      reduced hit, no loot, extra energy.
    * **LOST** — can't out-damage it and the hit would down you: full hit, no loot.

    Too exhausted to engage (``energy < HAZARD_ENERGY_COST``) → a forced retreat
    (a light hit, minimal energy) so a drained player is never trapped in combat.
    """
    z = cell.z
    monster_toughness = _roll_monster(z, HAZARD_BASE_TOUGHNESS, HAZARD_TOUGHNESS_PER_DEPTH, rng)
    monster_power = _roll_monster(z, HAZARD_BASE_POWER, HAZARD_POWER_PER_DEPTH, rng)

    # Too drained to fight — retreat immediately (a scrape, minimal energy).
    if energy < HAZARD_ENERGY_COST:
        hit = max(0, round(monster_power * FLEE_FRACTION) - stats.defense)
        return EncounterOutcome(
            kind=EncounterKind.HAZARD,
            resolution=Resolution.FLED,
            narration="😮‍💨 Too exhausted to fight — you scramble back the way you came.",
            damage_taken=hit,
            energy_cost=min(energy, HAZARD_ENERGY_COST),
        )

    player_damage = BASE_PLAYER_DAMAGE + stats.damage
    if player_damage >= monster_toughness:
        graze = max(0, round(monster_power * GRAZE_FRACTION) - stats.defense)
        loot = Reward(_draw_ore(z, rng), rng.randint(HAZARD_LOOT_MIN, HAZARD_LOOT_MAX) + stats.loot_bonus)
        return EncounterOutcome(
            kind=EncounterKind.HAZARD,
            resolution=Resolution.WON,
            narration=f"⚔️ You fend off the creature and grab {loot.amount} {loot.item}!",
            rewards=(loot,),
            damage_taken=graze,
            energy_cost=HAZARD_ENERGY_COST,
        )

    # Can't out-damage it in one exchange — flee if survivable, else you're downed.
    player_hp = BASE_PLAYER_HP + stats.max_health
    incoming = max(0, monster_power - stats.defense)
    if incoming < player_hp:
        flee_hit = max(0, round(monster_power * FLEE_FRACTION) - stats.defense)
        return EncounterOutcome(
            kind=EncounterKind.HAZARD,
            resolution=Resolution.FLED,
            narration="🏃 The creature is too tough — you break off and flee.",
            damage_taken=flee_hit,
            energy_cost=HAZARD_ENERGY_COST + FLEE_ENERGY_EXTRA,
        )
    return EncounterOutcome(
        kind=EncounterKind.HAZARD,
        resolution=Resolution.LOST,
        narration="💥 The creature overwhelms you — you barely crawl away.",
        damage_taken=min(player_hp, incoming),
        energy_cost=HAZARD_ENERGY_COST,
    )


def resolve(
    seed: int,
    cell: grid.Cell,
    stats: equipment.EffectiveStats | None = None,
    *,
    energy: int = energy_model.MAX_ENERGY,
    rng: random.Random | None = None,
) -> EncounterOutcome:
    """Resolve one encounter for an action on *cell* in world *seed*.

    *stats* is the player's :class:`equipment.EffectiveStats` (``None`` = a bare
    baseline player). *energy* is remaining energy (gates whether a hazard can be
    engaged). *rng* is injected for live-roll variance / tests; ``None`` derives a
    deterministic stream from :func:`encounter_seed` so ``(seed, x, y, z)`` → the
    same encounter (matching grid determinism).

    Always returns an :class:`EncounterOutcome`; a non-triggering roll (and every
    ``BARREN`` cell) returns the invariant :data:`_NONE_OUTCOME` baseline.
    """
    effective = stats or equipment.EffectiveStats()
    chooser = rng or random.Random(encounter_seed(seed, cell.x, cell.y, cell.z))

    kind = _trigger(cell, chooser)
    if kind is EncounterKind.NONE:
        return _NONE_OUTCOME
    if kind is EncounterKind.LOOT_CACHE:
        return _resolve_loot_cache(cell, effective, chooser)
    if kind is EncounterKind.RICH_VEIN:
        return _resolve_rich_vein(cell, effective, chooser)
    return _resolve_hazard(cell, effective, energy, chooser)


def resolve_at(
    seed: int,
    x: int,
    y: int,
    z: int,
    stats: equipment.EffectiveStats | None = None,
    *,
    energy: int = energy_model.MAX_ENERGY,
    rng: random.Random | None = None,
) -> EncounterOutcome:
    """Convenience: build the cell from the grid, then :func:`resolve` it.

    Composes :func:`grid.cell_at` with :func:`resolve` so a caller with only
    coordinates gets a one-call path; the deterministic default keeps
    ``(seed, x, y, z)`` → the same encounter.
    """
    cell = grid.cell_at(seed, x, y, z)
    return resolve(seed, cell, stats, energy=energy, rng=rng)


__all__ = [
    "EncounterKind",
    "Resolution",
    "Reward",
    "EncounterOutcome",
    "encounter_seed",
    "resolve",
    "resolve_at",
    "LOOT_CACHE_CHANCE",
    "RICH_VEIN_CHANCE",
    "NORMAL_HAZARD_CHANCE",
    "HAZARD_DEPTH_SCALE",
    "HAZARD_MAX_CHANCE",
    "BASE_PLAYER_DAMAGE",
    "BASE_PLAYER_HP",
]
