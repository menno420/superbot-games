"""Sim-pinned D&D bounded-menu economy — re-assert the menu-balance harness output.

These re-pin what ``games.dnd.sim.menu_sim`` measures by driving the shipped
resolver over EVERY scene × option: the **no-pay-to-win / bounded-economy** law
(Q-0040 / D-0007). Every menu option's reward is code-owned and
``<= catalog.GLOBAL_MAX`` component-wise, and the narrate-only no-op options mint
nothing — a balance/engine regression that breaks either reddens CI. Mirrors
``tests/exploration/test_survival_sim.py`` / ``tests/fishing/test_catch_sim.py``'s
sim-pin shape.
"""

from __future__ import annotations

from games.dnd.sim import menu_sim
from games.exploration.quest import catalog
from games.exploration.quest.models import RewardBundle

# --- pinned bounds (produced by the harness; see games/dnd/sim/menu_sim.py) --- #
# The per-scene max reward each menu's best option mints — code-owned, seed-stable.
# A future balance change must update these pins consciously. The scene-chain scenes
# reuse the existing sim-pinned effects (``escort_step`` tier-I; ``scout_narrate`` /
# ``rest_noop`` no-ops), so no new balance number: ``treeline_watch`` signals the escort
# (same escort reward as the road), and ``waystation_gate`` is narrate-only (mints
# nothing -> ``None``).
_PER_SCENE_MAX_REWARD: dict[str, RewardBundle | None] = {
    "waystation_road": RewardBundle(global_xp=5, game_xp=25, currency=10),
    "waystation_gate": None,
    "treeline_watch": RewardBundle(global_xp=5, game_xp=25, currency=10),
}
# The global max reward across every option in every scene.
_GLOBAL_MAX_REWARD = RewardBundle(global_xp=5, game_xp=25, currency=10)


def _run() -> menu_sim.MenuBalanceReport:
    # A smaller, fast seed sweep than the __main__ default; rewards are code-owned
    # and seed-independent, so a short range is enough to pin the bounds.
    return menu_sim.run(seeds=range(16))


def test_every_option_reward_within_global_max() -> None:
    # The no-pay-to-win / bounded-economy pin: every menu option's reward is
    # <= the catalog ceiling, component-wise. No option (nor a hallucinating DM
    # picking one) can out-earn GLOBAL_MAX.
    report = _run()
    assert report.all_within_global_max is True
    cap = catalog.GLOBAL_MAX
    for balance in report.by_scene.values():
        for opt in balance.options:
            if opt.reward is None:
                continue
            assert opt.reward.global_xp <= cap.global_xp, opt
            assert opt.reward.game_xp <= cap.game_xp, opt
            assert opt.reward.currency <= cap.currency, opt


def test_noop_option_yields_no_reward() -> None:
    # The default/narrate-only options grant nothing (mints nothing, advances no
    # quest). At least one no-op per scene: the clamp-target default is always a no-op.
    report = _run()
    assert report.total_noops >= 1
    for balance in report.by_scene.values():
        assert balance.noop_count >= 1
        for opt in balance.options:
            if opt.is_noop:
                assert opt.reward is None, opt
            else:
                assert opt.reward is not None, opt


def test_menu_balance_report_is_deterministic() -> None:
    # Same call -> identical report (rewards code-owned; only seeded DetRng in play).
    a = menu_sim.run(seeds=range(16))
    b = menu_sim.run(seeds=range(16))
    assert a == b


def test_per_scene_reward_bounds_pinned() -> None:
    # Pin the exact per-scene max reward + the global max (sim-pinned constants) so a
    # future balance change must update these pins consciously.
    report = _run()
    assert set(report.by_scene) == set(_PER_SCENE_MAX_REWARD), (
        "scene catalog changed — update the per-scene reward pins"
    )
    for scene_id, expected in _PER_SCENE_MAX_REWARD.items():
        assert report.scene(scene_id).max_reward == expected, scene_id
    assert report.global_max_reward == _GLOBAL_MAX_REWARD
