"""Coverage pins for ``games/dnd/sim/menu_sim.py`` — the guards + the renderer.

The existing ``tests/dnd/test_menu_sim.py`` pins the happy-path bounded-menu
economy (every option within ``catalog.GLOBAL_MAX``, no-ops mint nothing,
determinism). This module pins what that suite left dark:

* the reward-not-seed-stable AssertionError in ``_scene_balance`` — the shipped
  resolver IS seed-stable, so the guard is tripped via a stubbed
  ``_resolve_option_reward`` that varies its reward with the seed;
* the over-cap flip of ``all_within_global_max`` in ``run`` — same stub trick,
  one component pushed past ``catalog.GLOBAL_MAX``;
* both branches of ``_fmt_reward`` (narrate-only dash vs the component string);
* the whole ``format_report`` renderer, against a real 2-seed run.

Tests only; the stubs live in the tests, the module's shipped behavior is
asserted at EXISTING catalog constants.
"""

from __future__ import annotations

import pytest

from games.dnd.data.scenes import SCENES
from games.dnd.sim import menu_sim
from games.exploration.quest import catalog
from games.exploration.quest.models import RewardBundle

START_SCENE = SCENES["waystation_road"]


def _stub_option_reward(reward_for_seed):
    """A ``_resolve_option_reward`` stand-in minting ``reward_for_seed(seed)``."""

    def stub(scene, option_id, *, seed):
        return menu_sim.OptionReward(
            scene_id=scene.scene_id,
            option_id=option_id,
            effect_id="stub",
            reward=reward_for_seed(seed),
            is_noop=reward_for_seed(seed) is None,
        )

    return stub


# ---------------------------------------------------------------------------
# The defensive guards — unreachable through the shipped resolver, so stubbed
# ---------------------------------------------------------------------------
def test_seed_unstable_reward_raises_the_named_assertion(monkeypatch) -> None:
    # A reward that grows with the seed violates the code-owned invariance.
    monkeypatch.setattr(
        menu_sim,
        "_resolve_option_reward",
        _stub_option_reward(
            lambda seed: RewardBundle(global_xp=seed, game_xp=0, currency=0)
        ),
    )
    with pytest.raises(AssertionError, match="reward not seed-stable"):
        menu_sim._scene_balance(START_SCENE, range(2))


def test_over_cap_reward_flips_the_no_pay_to_win_flag(monkeypatch) -> None:
    cap = catalog.GLOBAL_MAX
    over = RewardBundle(
        global_xp=cap.global_xp + 1, game_xp=cap.game_xp, currency=cap.currency
    )
    monkeypatch.setattr(
        menu_sim, "_resolve_option_reward", _stub_option_reward(lambda seed: over)
    )
    report = menu_sim.run(seeds=range(2), scenes={"waystation_road": START_SCENE})
    assert report.all_within_global_max is False
    assert report.global_max_reward == over
    assert report.total_noops == 0


# ---------------------------------------------------------------------------
# _fmt_reward — both branches
# ---------------------------------------------------------------------------
def test_fmt_reward_narrate_only_renders_the_dash_line() -> None:
    assert menu_sim._fmt_reward(None) == "—  (narrate-only, mints nothing)"


def test_fmt_reward_renders_every_component() -> None:
    line = menu_sim._fmt_reward(RewardBundle(global_xp=3, game_xp=7, currency=11))
    assert line == "global_xp=3 game_xp=7 currency=11"


# ---------------------------------------------------------------------------
# format_report — the human-readable balance page, against a real 2-seed run
# ---------------------------------------------------------------------------
def test_format_report_headline_ceiling_and_verdict() -> None:
    report = menu_sim.run(seeds=range(2))
    text = menu_sim.format_report(report)
    cap = catalog.GLOBAL_MAX
    assert "seeds swept: 2" in text
    assert (
        f"scenes: {len(report.by_scene)}   options: {report.total_options}   "
        f"no-op options: {report.total_noops}"
    ) in text
    assert (
        "global reward ceiling (catalog.GLOBAL_MAX): "
        f"global_xp={cap.global_xp} game_xp={cap.game_xp} currency={cap.currency}"
    ) in text
    assert "all options <= GLOBAL_MAX (no pay-to-win): True" in text


def test_format_report_lists_every_scene_with_its_option_rows() -> None:
    report = menu_sim.run(seeds=range(2))
    text = menu_sim.format_report(report)
    for scene_id, balance in report.by_scene.items():
        assert f"[{scene_id}]  options={balance.option_count}  no-ops={balance.noop_count}" in text
        for option in balance.options:
            assert option.option_id in text
    assert "no-op : —  (narrate-only, mints nothing)" in text  # a real no-op row
    assert text.count("-> per-scene max reward:") == len(report.by_scene)
    assert "global max reward across all options:" in text
