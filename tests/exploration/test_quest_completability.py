"""Quest-catalog completability sweep — every quest × tier walks to COMPLETED.

The dnd side has liveness sweeps for scenes (#126) and effects (#129), but
nothing proved every quest in `games/exploration/quest/catalog.py` is
COMPLETABLE end-to-end via the real seam (`services/exploration_workflow`:
offer → accept → bounded `apply_action` loop → `grant_rewards`) at every
offered RewardTier. An uncompletable or budget-starved quest is dead catalog
data a player can accept and never finish.

Budget discipline: every walk is bounded by the quest's OWN declared budget —
the sum of its objectives' ``required`` counts (each catalog objective's
predicate carries no ``count_field``, so one on-menu action advances exactly
one objective step; the tightness test pins that). No loop here can run past
``sum(required)`` iterations; nothing is unbounded.

An uncompletable quest×tier is a HEADLINE: the sweep collects each failure
with its quest id, tier, and stall point and asserts the list is EMPTY, so a
red names every broken row instead of deleting or skipping it.

Determinism: fixed ``world_seed`` (the state default 0), fixed ``now``, no
wall-clock, no global rng — the engine derives everything from the seed.
"""

from __future__ import annotations

from datetime import datetime, timezone

from services import exploration_workflow as ew
from services.audit import InMemorySink

from games.exploration.quest import catalog
from games.exploration.quest.models import QuestState, RewardTier
from games.exploration.survival.difficulty import TUNABLES

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)

ALL_TIERS = tuple(RewardTier)


def _budget(template_id: str) -> int:
    """A quest's own declared action budget: the sum of objective requireds."""
    return sum(obj.required for obj in catalog.get(template_id).objectives)


def _walk_to_completed(template_id: str, tier: RewardTier):
    """Offer → accept → act along pending_actions, bounded by the budget.

    Returns ``(state, sink, ok_actions, stall)`` where *stall* is ``None`` on
    a clean walk or a human-readable reason string (the headline evidence).
    """
    state = ew.ExplorationState()
    sink = InMemorySink()

    offered = ew.offer(state, template_id, tier, sink=sink, now=FIXED_NOW)
    if not offered.ok:
        return state, sink, 0, f"offer refused: {offered.message}"
    accepted = ew.accept(state, sink=sink, now=FIXED_NOW)
    if not accepted.ok:
        return state, sink, 0, f"accept refused: {accepted.message}"

    budget = _budget(template_id)
    ok_actions = 0
    for _ in range(budget):  # bounded by the quest's own declaration
        pending = ew.pending_actions(state.quest)
        if not pending:
            break
        res = ew.apply_action(state, pending[0], sink=sink, now=FIXED_NOW)
        if not res.ok:
            return state, sink, ok_actions, (
                f"action {pending[0]!r} refused after {ok_actions} ok actions: {res.message}"
            )
        ok_actions += 1

    quest = state.quest
    if quest is None or quest.state is not QuestState.COMPLETED:
        got = "no quest" if quest is None else quest.state.value
        return state, sink, ok_actions, (
            f"not COMPLETED after {ok_actions}/{budget} budgeted actions (state: {got})"
        )
    return state, sink, ok_actions, None


def test_every_quest_x_tier_walks_to_completed_within_its_own_budget():
    """THE sweep: all catalog ids × all offered tiers, seam-driven, budget-bounded."""
    headlines: list[str] = []
    for template_id in catalog.menu():
        for tier in ALL_TIERS:
            state, sink, ok_actions, stall = _walk_to_completed(template_id, tier)
            if stall is not None:
                headlines.append(f"{template_id} × tier {tier.value}: {stall}")
                continue
            # Tight budget: completion consumed EXACTLY the declared budget.
            if ok_actions != _budget(template_id):
                headlines.append(
                    f"{template_id} × tier {tier.value}: completed in {ok_actions} "
                    f"actions, declared budget {_budget(template_id)}"
                )
    assert not headlines, "uncompletable quest×tier rows:\n" + "\n".join(headlines)


def test_budget_is_tight_one_step_short_leaves_the_quest_active():
    """budget-1 on-menu actions never complete a quest (no hidden multi-counts)."""
    for template_id in catalog.menu():
        state = ew.ExplorationState()
        sink = InMemorySink()
        ew.offer(state, template_id, RewardTier.I, sink=sink, now=FIXED_NOW)
        ew.accept(state, sink=sink, now=FIXED_NOW)
        for _ in range(_budget(template_id) - 1):  # bounded: one short of budget
            res = ew.apply_action(
                state, ew.pending_actions(state.quest)[0], sink=sink, now=FIXED_NOW
            )
            assert res.ok, (template_id, res.message)
        assert state.quest is not None, template_id
        assert state.quest.state is QuestState.ACTIVE, (
            f"{template_id}: completed a step EARLY — an action advanced more than 1"
        )


def test_completed_quest_banks_exactly_the_tier_cap_and_retires():
    """grant_rewards on each walked quest×tier: capped bundle, fold, retire."""
    for template_id in catalog.menu():
        for tier in ALL_TIERS:
            state, sink, _, stall = _walk_to_completed(template_id, tier)
            assert stall is None, (template_id, tier, stall)
            rows_before = len(sink.records)
            granted = ew.grant_rewards(state, sink=sink, now=FIXED_NOW)
            assert granted.ok, (template_id, tier, granted.message)
            bundle = granted.reward
            cap = catalog.TIER_CAPS[tier]
            assert (bundle.global_xp, bundle.game_xp, bundle.currency) == (
                cap.global_xp,
                cap.game_xp,
                cap.currency,
            ), (template_id, tier)
            # Capability is play-only and tier III-only (Q-0039: no pay-to-win).
            expected_capability = (
                catalog.get(template_id).prestige_capability
                if tier is RewardTier.III
                else None
            )
            assert bundle.capability == expected_capability, (template_id, tier)
            # Global ceiling holds component-wise.
            assert bundle.global_xp <= catalog.GLOBAL_MAX.global_xp
            assert bundle.game_xp <= catalog.GLOBAL_MAX.game_xp
            assert bundle.currency <= catalog.GLOBAL_MAX.currency
            # The grant folded the ledger, retired the quest, audited ONE row.
            assert state.quest is None, (template_id, tier)
            assert state.ledger.currency >= cap.currency, (template_id, tier)
            assert len(sink.records) == rows_before + 1, (template_id, tier)


def test_every_quest_budget_fits_the_energy_bar_at_every_difficulty():
    """No catalog quest is energy-starved: budget × cost ≤ max_energy everywhere.

    There is no rest/regen op on the seam, so a quest whose declared budget
    cannot be paid from a full bar would be uncompletable at that difficulty —
    a headline, not a tuning nit.
    """
    headlines: list[str] = []
    for template_id in catalog.menu():
        need = _budget(template_id)
        for difficulty, tunables in TUNABLES.items():
            cost = need * tunables.cost
            if cost > tunables.max_energy:
                headlines.append(
                    f"{template_id} @ {difficulty.value}: needs {cost} energy, "
                    f"bar caps at {tunables.max_energy}"
                )
    assert not headlines, "energy-starved quest×difficulty rows:\n" + "\n".join(headlines)


def test_walk_is_deterministic_for_a_fixed_seed():
    """Same seed/tier/now ⇒ identical instance, encounter stream, and bundle."""

    def run():
        state, sink, _, stall = _walk_to_completed("supply_run", RewardTier.II)
        assert stall is None, stall
        encounters = [
            (r.mutation_type, r.new_value)
            for r in sink.records
        ]
        instance_id = state.quest.instance_id
        granted = ew.grant_rewards(state, sink=sink, now=FIXED_NOW)
        return instance_id, encounters, granted.reward

    first, second = run(), run()
    assert first == second


def test_audit_trail_is_one_row_per_committed_op():
    """offer + accept + budget actions + grant = budget + 3 rows, per quest."""
    for template_id in catalog.menu():
        state, sink, ok_actions, stall = _walk_to_completed(template_id, RewardTier.I)
        assert stall is None, (template_id, stall)
        ew.grant_rewards(state, sink=sink, now=FIXED_NOW)
        assert len(sink.records) == ok_actions + 3, (
            template_id,
            [r.mutation_type for r in sink.records],
        )
