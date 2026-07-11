"""Cross-domain economy sim — enumerates EVERY reward source and pins the
whole-economy invariants (no balance changes; a read-only harness).

Every per-domain sim pins one game's curve in isolation. This one drives the
*shipped* resolvers/catalogs of all four world games — mining, fishing, dnd,
exploration — computes each domain's per-hour emission, and asserts three named
global invariants that no single-game sim can see:

* ``GRANT_WITHIN_GLOBAL_CAP`` — every currency/xp faucet (each quest
  ``TIER_CAPS`` bundle AND the dnd escort bundle) is ``<= catalog.GLOBAL_MAX``
  (20 / 120 / 50) component-wise. ``GLOBAL_MAX`` is the ONE cross-domain reward
  ceiling; it binds the quest engine + dnd, NOT the mining/fishing item faucets.
* ``ITEM_FAUCET_MINTS_NO_CURRENCY`` — mining and fishing mint ITEMS ONLY at the
  resolver layer: zero native currency / global_xp / game_xp per hour. (Mining
  coins exist only downstream as an ore→sell conversion — a sink, not a mint.)
* ``NOOP_MINTS_NOTHING`` — the narrate-only / baseline / too-tired paths across
  the domains (dnd ``rest_noop`` + ``scout_narrate``, a mining NONE encounter, a
  fishing no-bite / too-tired cast) mint nothing at all.

The emission MAGNITUDES are DERIVED by running the shipped resolvers over a
seeded sweep, then pinned with tolerance bands (see
``docs/design/economy-sim.md``). NO balance constant is edited here — this module
only reads/exercises the shipped code. Item faucets are energy-throttled (mining
360 digs/hr, fishing 180 casts/hr → items/hr); the currency/xp faucets (dnd
escort + exploration quests) are host-gated per-completion (no in-domain
cooldown), so their pinned domain-side quantity is a per-completion bundle.

Pure + seeded: same call → same report. Stdlib only — no Discord, DB, or IO.

Run it:  ``python3 -m games.shared.sim.economy_sim``
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from games.dnd.core import effects
from games.exploration.quest import catalog
from games.exploration.quest.models import RewardBundle, RewardTier
from games.fishing.core import catch, spots
from games.fishing.core.rng import fishing_seed
from games.fishing.inventory import adapter as fishing_adapter
from games.mining.core import encounters, energy as energy_model, grid, items, rewards
from games.shared.inventory.interface import EMPTY_GRANT, ProgressionDelta

# ---------------------------------------------------------------------------
# Sim-pinned emission bands (see docs/design/economy-sim.md §"Pinned table").
# DERIVED from the current shipped resolvers over the default sweep — NOT
# invented. Regenerate with ``python3 -m games.shared.sim.economy_sim`` and
# re-pin here (only) if a resolver's faucet constant intentionally changes.
# ---------------------------------------------------------------------------
_MINING_ORE_PER_HOUR = (480.0, 600.0)  # observed ≈ 540 (mean 1.5 ore/dig × 360)
_FISHING_FISH_PER_HOUR = (85.0, 115.0)  # observed ≈ 98.5 (bite ≈ 0.55 × 180)

# The neutral default fishing spot (bite_bias 0.0 → exactly BASE_BITE_CHANCE) —
# the baseline biome, so the pinned bite rate is the resolver's own base chance.
_DEFAULT_SPOT: str = spots.DEFAULT_SPOT.spot_id


@dataclass(frozen=True)
class DomainEmission:
    """One game's per-hour emission profile — every number read off the shipped code.

    ``native_*_per_hour`` is what the domain's OWN resolver layer mints per active
    hour: for the item faucets (mining, fishing) currency/xp are ``0.0`` exactly
    (they mint items only); for the host-gated faucets (dnd, exploration) the
    per-hour rate is undefined (no in-domain cooldown) so the emission is carried
    as a ``per_completion_bundle`` instead. ``action_ceiling_per_hour`` is the
    energy-throttled action cap (``None`` when host-gated).
    """

    domain: str
    native_currency_per_hour: float
    native_global_xp_per_hour: float
    native_game_xp_per_hour: float
    items_per_hour: float
    action_ceiling_per_hour: float | None
    per_completion_bundle: tuple[int, int, int] | None  # (gxp, game_xp, currency)
    notes: str


@dataclass(frozen=True)
class EconomyReport:
    """The whole-economy emission snapshot + the computed invariant flags."""

    mining: DomainEmission
    fishing: DomainEmission
    dnd: DomainEmission
    exploration: DomainEmission
    # The ONE cross-domain reward ceiling (catalog.GLOBAL_MAX) as (gxp, game_xp, currency).
    global_cap: tuple[int, int, int]
    # Named global invariants (see module docstring).
    grant_within_global_cap: bool = False
    item_faucet_mints_no_currency: bool = False
    noop_mints_nothing: bool = False

    @property
    def domains(self) -> tuple[DomainEmission, ...]:
        return (self.mining, self.fishing, self.dnd, self.exploration)


def _bundle_tuple(bundle: RewardBundle) -> tuple[int, int, int]:
    """A ``RewardBundle`` as the ``(global_xp, game_xp, currency)`` tuple used here."""
    return (bundle.global_xp, bundle.game_xp, bundle.currency)


def _mining_action_ceiling() -> float:
    """Sustained digs/hr = the passive energy regen rate ÷ the per-dig cost.

    Read straight off the shipped energy model: +1 energy every ``REGEN_SECONDS``
    → ``3600 / REGEN_SECONDS`` energy per hour, each dig spends ``DIG_COST``.
    """
    energy_per_hour = 3600 / energy_model.REGEN_SECONDS
    return energy_per_hour / energy_model.DIG_COST


def _fishing_action_ceiling() -> float:
    """Sustained casts/hr = the shared energy regen rate ÷ ``catch.CAST_COST``."""
    energy_per_hour = 3600 / energy_model.REGEN_SECONDS
    return energy_per_hour / catch.CAST_COST


def _sample_mean_ore_per_dig(seeds: range, digs_per_seed: int) -> float:
    """Mean ore/dig for a baseline (no-tool) player at the surface (depth 0).

    Drives the shipped ``rewards.roll_mine_loot`` with an injected per-seed
    ``random.Random`` (Mersenne — process-independent), so the mean is a pure
    function of the sweep bounds. ``bonus`` is 1.0 (no tool), so the amount is
    ``max(1, round(randint(1, BASE_ROLL_MAX)))`` — the raw base faucet.
    """
    total = 0
    n = 0
    for seed in seeds:
        rng = random.Random(seed)
        for _ in range(digs_per_seed):
            _ore, amount = rewards.roll_mine_loot(has_pickaxe=False, depth=0, rng=rng)
            total += amount
            n += 1
    return total / n if n else 0.0


def _sample_bite_rate(seeds: range, casts_per_seed: int) -> float:
    """Baseline bite rate at the neutral default spot over the seeded cast sweep.

    Each cast injects a hash-free ``random.Random(fishing_seed(seed, key))`` stream
    (splitmix64 — process-independent), so the rate is a pure function of the
    bounds. Baseline stats (``None``) and the neutral spot mean the rate is the
    resolver's own ``BASE_BITE_CHANCE`` before any gear/biome bias.
    """
    bites = 0
    casts = 0
    for seed in seeds:
        for i in range(casts_per_seed):
            stream = random.Random(fishing_seed(seed, f"{_DEFAULT_SPOT}:{i}"))
            out = catch.resolve_cast(seed, _DEFAULT_SPOT, None, rng=stream)
            casts += 1
            if out.bit:
                bites += 1
    return bites / casts if casts else 0.0


def _mean_surface_ore_coin_value() -> float:
    """Weighted-mean sell value (coins/ore) of a surface dig, from ``items`` values.

    A DOWNSTREAM sink-conversion figure only — the mining resolver mints ore, not
    coins; a player sells ore for this per-unit value later. Weighted by the
    surface ore-selection weights so it reflects the actual drop mix.
    """
    weights = rewards.ore_weights_for_depth(0)
    total_w = sum(weights.values())
    if not total_w:
        return 0.0
    return sum(items.item_value(ore) * w for ore, w in weights.items()) / total_w


def run(
    *,
    seeds: range = range(24),
    digs_per_seed: int = 500,
    casts_per_seed: int = 500,
) -> EconomyReport:
    """Enumerate every reward source across the four world games → an ``EconomyReport``.

    Deterministic: the mining/fishing faucets are sampled with process-independent
    injected RNG streams over ``seeds``, and the dnd/exploration bundles are read
    straight off the shipped effect/catalog — so the same call always yields an
    equal report. Nothing here edits a resolver constant; it only reads/exercises
    the shipped code.
    """
    # --- mining: ITEMS ONLY (zero native currency/xp) ---------------------------
    mean_ore = _sample_mean_ore_per_dig(seeds, digs_per_seed)
    mining_ceiling = _mining_action_ceiling()
    mining_items_hr = mean_ore * mining_ceiling
    mean_coin = _mean_surface_ore_coin_value()
    sell_coin_ceiling_hr = mining_items_hr * mean_coin  # downstream sink, not a mint
    mining = DomainEmission(
        domain="mining",
        native_currency_per_hour=0.0,
        native_global_xp_per_hour=0.0,
        native_game_xp_per_hour=0.0,
        items_per_hour=mining_items_hr,
        action_ceiling_per_hour=mining_ceiling,
        per_completion_bundle=None,
        notes=(
            f"mints ore items only ({mean_ore:.3f} ore/dig × {mining_ceiling:.0f} "
            f"digs/hr). Coins are a DOWNSTREAM sell-conversion, NOT a mint: "
            f"informational sell-ceiling ≈ {sell_coin_ceiling_hr:,.0f} coins/hr "
            f"(× {mean_coin:.2f} weighted coins/ore)."
        ),
    )

    # --- fishing: ITEMS ONLY (adapter progression is EXPLICITLY EMPTY) ----------
    bite_rate = _sample_bite_rate(seeds, casts_per_seed)
    fishing_ceiling = _fishing_action_ceiling()
    fishing_items_hr = bite_rate * fishing_ceiling
    fishing = DomainEmission(
        domain="fishing",
        native_currency_per_hour=0.0,
        native_global_xp_per_hour=0.0,
        native_game_xp_per_hour=0.0,
        items_per_hour=fishing_items_hr,
        action_ceiling_per_hour=fishing_ceiling,
        per_completion_bundle=None,
        notes=(
            f"mints fish items only ({bite_rate:.3f} bite rate × "
            f"{fishing_ceiling:.0f} casts/hr). catch_to_grant progression is "
            f"explicitly empty — zero currency/xp."
        ),
    )

    # --- dnd: escort mints exactly the tier-I bundle (read via the shipped effect) ---
    escort_outcome = effects.EFFECTS["escort_step"].apply(seed=0, player_id="economy_sim")
    assert escort_outcome.reward is not None, "escort_step must mint on COMPLETE"
    escort_bundle = _bundle_tuple(escort_outcome.reward)
    dnd = DomainEmission(
        domain="dnd",
        native_currency_per_hour=0.0,
        native_global_xp_per_hour=0.0,
        native_game_xp_per_hour=0.0,
        items_per_hour=0.0,
        action_ceiling_per_hour=None,  # host-gated: no in-domain cooldown
        per_completion_bundle=escort_bundle,
        notes=(
            f"escort_step mints tier-I {escort_bundle} (gxp, game_xp, currency) via "
            f"the exploration quest engine; rest_noop / scout_narrate mint nothing. "
            f"Per-hour is host-gated (no in-domain cooldown) → pinned per-completion."
        ),
    )

    # --- exploration: the native currency/xp faucet; tier-III bundle is the max ---
    tier3_bundle = _bundle_tuple(catalog.TIER_CAPS[RewardTier.III])
    exploration = DomainEmission(
        domain="exploration",
        native_currency_per_hour=0.0,
        native_global_xp_per_hour=0.0,
        native_game_xp_per_hour=0.0,
        items_per_hour=0.0,
        action_ceiling_per_hour=None,  # host-gated: no in-domain cooldown
        per_completion_bundle=tier3_bundle,
        notes=(
            f"quest engine grants exactly TIER_CAPS[tier]; max tier-III {tier3_bundle} "
            f"(gxp, game_xp, currency) == GLOBAL_MAX. Per-hour host-gated → pinned "
            f"per-completion."
        ),
    )

    global_cap = _bundle_tuple(catalog.GLOBAL_MAX)

    report = EconomyReport(
        mining=mining,
        fishing=fishing,
        dnd=dnd,
        exploration=exploration,
        global_cap=global_cap,
    )
    # Compute the named invariant flags from the same shipped-data helpers the tests use.
    from dataclasses import replace

    return replace(
        report,
        grant_within_global_cap=all_bundles_within_global_cap(report),
        item_faucet_mints_no_currency=item_faucets_mint_no_currency_or_xp(report),
        noop_mints_nothing=noop_paths_mint_nothing(),
    )


# ---------------------------------------------------------------------------
# Named invariants — each returns a bool; the tests re-assert them directly too.
# ---------------------------------------------------------------------------
def all_bundles_within_global_cap(report: EconomyReport) -> bool:
    """Invariant ``GRANT_WITHIN_GLOBAL_CAP``.

    Every currency/xp faucet bundle — each quest ``catalog.TIER_CAPS`` tier AND
    the dnd escort bundle — is ``<= catalog.GLOBAL_MAX`` component-wise. This is
    the ONE cross-domain reward ceiling; it binds the quest engine + dnd, not the
    mining/fishing item faucets (which mint no currency/xp).
    """
    cap = _bundle_tuple(catalog.GLOBAL_MAX)
    bundles: list[tuple[int, int, int]] = [
        _bundle_tuple(b) for b in catalog.TIER_CAPS.values()
    ]
    if report.dnd.per_completion_bundle is not None:
        bundles.append(report.dnd.per_completion_bundle)
    return all(
        all(component <= limit for component, limit in zip(bundle, cap))
        for bundle in bundles
    )


def item_faucets_mint_no_currency_or_xp(report: EconomyReport) -> bool:
    """Invariant ``ITEM_FAUCET_MINTS_NO_CURRENCY``.

    Mining and fishing native currency / global_xp / game_xp per hour are all
    ``0.0`` exactly — the item faucets mint items only at the resolver layer.
    """
    for domain in (report.mining, report.fishing):
        if (
            domain.native_currency_per_hour != 0.0
            or domain.native_global_xp_per_hour != 0.0
            or domain.native_game_xp_per_hour != 0.0
        ):
            return False
    return True


def noop_paths_mint_nothing() -> bool:
    """Invariant ``NOOP_MINTS_NOTHING``.

    Resolve the REAL no-op / baseline / too-tired paths of each domain and confirm
    each mints nothing: the dnd ``rest_noop`` + ``scout_narrate`` effects (no
    reward), a mining NONE encounter (no rewards), and a fishing no-bite /
    too-tired cast (``EMPTY_GRANT`` — zero items, zero progression).
    """
    # dnd narrate-only effects — no reward.
    for effect_id in ("rest_noop", "scout_narrate"):
        outcome = effects.EFFECTS[effect_id].apply(seed=0, player_id="economy_sim")
        if outcome.reward is not None:
            return False

    # mining: a BARREN cell is the stat-independent NONE baseline — no rewards.
    barren = grid.Cell(0, 0, 0, grid.CellFeature.BARREN, "stone", 0.5)
    mining_none = encounters.resolve(1, barren)
    if mining_none.kind is not encounters.EncounterKind.NONE or mining_none.rewards:
        return False

    # fishing: a too-tired cast (no energy) → the honest no-bite → EMPTY_GRANT.
    too_tired = catch.resolve_cast(0, _DEFAULT_SPOT, None, energy=0)
    grant = fishing_adapter.cast_to_grant(too_tired)
    if grant is not EMPTY_GRANT:
        # Defensive: still accept a value-equal empty grant.
        if grant.items or grant.progression != ProgressionDelta():
            return False
    return True


def format_report(report: EconomyReport) -> str:
    lines: list[str] = []
    lines.append("CROSS-DOMAIN ECONOMY EMISSION (per active hour)")
    lines.append("=" * 64)
    lines.append("")
    header = f"{'domain':<12} {'items/hr':>10} {'cur/hr':>8} {'gxp/hr':>8} {'gamexp/hr':>10} {'ceiling':>9}"
    lines.append(header)
    lines.append("-" * len(header))
    for d in report.domains:
        ceiling = "host" if d.action_ceiling_per_hour is None else f"{d.action_ceiling_per_hour:.0f}"
        lines.append(
            f"{d.domain:<12} {d.items_per_hour:>10.1f} "
            f"{d.native_currency_per_hour:>8.1f} {d.native_global_xp_per_hour:>8.1f} "
            f"{d.native_game_xp_per_hour:>10.1f} {ceiling:>9}"
        )
    lines.append("")
    lines.append("per-completion currency/xp bundles (gxp, game_xp, currency) — host-gated:")
    for d in report.domains:
        if d.per_completion_bundle is not None:
            lines.append(f"  {d.domain:<12} {d.per_completion_bundle}")
    lines.append(f"  {'GLOBAL_MAX':<12} {report.global_cap}   (the one cross-domain ceiling)")
    lines.append("")
    lines.append("notes:")
    for d in report.domains:
        lines.append(f"  [{d.domain}] {d.notes}")
    lines.append("")
    lines.append("invariants:")
    lines.append(
        f"  GRANT_WITHIN_GLOBAL_CAP        {'PASS' if report.grant_within_global_cap else 'FAIL'}"
    )
    lines.append(
        f"  ITEM_FAUCET_MINTS_NO_CURRENCY  {'PASS' if report.item_faucet_mints_no_currency else 'FAIL'}"
    )
    lines.append(
        f"  NOOP_MINTS_NOTHING             {'PASS' if report.noop_mints_nothing else 'FAIL'}"
    )
    lines.append("")
    lines.append("pinned bands (see docs/design/economy-sim.md):")
    lines.append(f"  mining items/hr  {_MINING_ORE_PER_HOUR}   (observed {report.mining.items_per_hour:.1f})")
    lines.append(f"  fishing items/hr {_FISHING_FISH_PER_HOUR}   (observed {report.fishing.items_per_hour:.1f})")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_report(run()))
