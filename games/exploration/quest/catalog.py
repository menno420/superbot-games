"""The v1 bounded-menu quest catalog (Q-0040 bounded-authority posture).

The AI DM only PICKS a ``(template_id, RewardTier)`` pair from this pre-approved,
hard-capped catalog. It never computes reward amounts and never mutates state:
the amounts here are CODE-OWNED, clamped to ``TIER_CAPS`` / ``GLOBAL_MAX`` by the
engine, and pinned by the balance sim (``tests/test_balance_sim.py``). Capability
unlocks are play-only (tier III completion), never bought with currency
(Q-0039 / Q-0190, no pay-to-win).

NOTE ON THE NUMBERS: the exact superbot Q-0087 dual-track band constants were not
sourced into this repo. The tier ceilings below are deliberately conservative,
in-band values chosen to be reconciled against the real Q-0087 bands later; they
exist so the engine is fully sim-pinned now. Adjust here (one source of truth) when
the canonical bands are imported — the tests will re-pin to whatever lands.
"""

from __future__ import annotations

from .models import Objective, QuestKind, QuestTemplate, RewardBundle, RewardTier

# Hard per-tier ceilings. The engine grants exactly these bundles (fixed, capped).
TIER_CAPS: dict[RewardTier, RewardBundle] = {
    RewardTier.I: RewardBundle(global_xp=5, game_xp=25, currency=10),
    RewardTier.II: RewardBundle(global_xp=10, game_xp=60, currency=25),
    RewardTier.III: RewardBundle(global_xp=20, game_xp=120, currency=50),
}

# The absolute ceiling; every tier is <= this component-wise.
GLOBAL_MAX = RewardBundle(global_xp=20, game_xp=120, currency=50)


TEMPLATES: dict[str, QuestTemplate] = {
    "supply_run": QuestTemplate(
        template_id="supply_run",
        kind=QuestKind.FETCH,
        title="Supply Run",
        summary="Deliver three supply crates to the outpost.",
        objectives=(
            Objective(
                key="deliver_crates",
                description="Deliver 3 supply crates",
                predicate="item_delivered",
                params=(("match", {"item": "supply_crate"}),),
                required=3,
            ),
        ),
        prestige_capability="trade_route_unlock",
    ),
    "safe_passage": QuestTemplate(
        template_id="safe_passage",
        kind=QuestKind.ESCORT,
        title="Safe Passage",
        summary="Escort a traveler safely to the waystation.",
        objectives=(
            Objective(
                key="escort_traveler",
                description="Escort the traveler to the waystation",
                predicate="npc_reached",
                params=(("match", {"npc": "traveler", "dest": "waystation"}),),
                required=1,
            ),
        ),
        prestige_capability="guild_courier_unlock",
    ),
    "cull_the_pack": QuestTemplate(
        template_id="cull_the_pack",
        kind=QuestKind.HUNT,
        title="Cull the Pack",
        summary="Thin the dire-wolf pack menacing the trail.",
        objectives=(
            Objective(
                key="defeat_wolves",
                description="Defeat 5 dire wolves",
                predicate="target_defeated",
                params=(("match", {"species": "dire_wolf"}),),
                required=5,
            ),
        ),
        prestige_capability="beast_tracker_unlock",
    ),
    "missing_scout": QuestTemplate(
        template_id="missing_scout",
        kind=QuestKind.RESCUE,
        title="Missing Scout",
        summary="Reach the cavern and free the captured scout.",
        objectives=(
            Objective(
                key="reach_cavern",
                description="Reach the cavern",
                predicate="location_reached",
                params=(("match", {"loc": "cavern"}),),
                required=1,
            ),
            Objective(
                key="free_captive",
                description="Free the captive scout",
                predicate="captive_freed",
                params=(),
                required=1,
            ),
        ),
        prestige_capability="field_medic_unlock",
    ),
    "whispering_ruins": QuestTemplate(
        template_id="whispering_ruins",
        kind=QuestKind.MYSTERY,
        title="Whispering Ruins",
        summary="Piece together what happened in the ruins.",
        objectives=(
            Objective(
                key="find_clues",
                description="Find 4 clues",
                predicate="clue_found",
                params=(),
                required=4,
            ),
        ),
        prestige_capability="lorekeeper_unlock",
    ),
}


def get(template_id: str) -> QuestTemplate:
    """Return the template for ``template_id`` or raise ``KeyError``."""
    template = TEMPLATES.get(template_id)
    if template is None:
        raise KeyError(f"unknown quest template: {template_id!r}")
    return template


def menu() -> tuple[str, ...]:
    """Return the ordered template ids — the bounded menu the AI DM picks from."""
    return tuple(TEMPLATES.keys())
