"""Menu-balance sim — pins the D&D bounded-menu economy (no pay-to-win, Q-0040).

Pure + seeded (mirrors ``games.exploration.survival.sim`` /
``games.fishing.sim.catch_sim``): enumerates **every** scene in the shipped data
catalog (:data:`games.dnd.data.scenes.SCENES`) and **every** option in each menu,
resolves each option's PRE-DEFINED effect through the REAL shipped resolver
(:func:`games.dnd.core.resolver.resolve`, seeded) and reads back the reward it
mints. The harness only READS and EXERCISES the shipped resolver / effects / scene
data — it never changes any outcome.

The property it proves is the **bounded-menu economy** (Q-0040 / D-0007): every
menu option's reward is code-owned and ``<= catalog.GLOBAL_MAX`` component-wise (no
option a player or a hallucinating DM can pick out-earns the ceiling — no
pay-to-win), and the narrate-only no-op options grant nothing. Because the resolver
and effects are deterministic (``DetRng`` / ``derive_seed`` — no wall-clock, no
global RNG), the same call always yields the same :class:`MenuBalanceReport`, and
the matching fast test (``tests/dnd/test_menu_sim.py``) re-pins the bounds.

Run it:  ``python3 -m games.dnd.sim.menu_sim``
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from games.dnd.core.models import DMChoice, Scene
from games.dnd.core.resolver import resolve
from games.dnd.data.scenes import SCENES
from games.exploration.quest import catalog
from games.exploration.quest.models import RewardBundle

# High XP surfaces the full menu (``menu_width`` caps at MAX_MENU_SIZE >= any scene's
# option count), so EVERY option is a genuine, surfaced choice — the sim exercises the
# real reward each option mints rather than a width-clamped no-op.
_FULL_MENU_XP = 5_000


def _reward_leq_global_max(reward: RewardBundle) -> bool:
    """Whether ``reward`` is ``<= catalog.GLOBAL_MAX`` component-wise (the ceiling)."""
    cap = catalog.GLOBAL_MAX
    return (
        reward.global_xp <= cap.global_xp
        and reward.game_xp <= cap.game_xp
        and reward.currency <= cap.currency
    )


def _component_max(a: Optional[RewardBundle], b: Optional[RewardBundle]) -> Optional[RewardBundle]:
    """Component-wise max of two optional bundles (``None`` = the empty reward)."""
    if a is None:
        return b
    if b is None:
        return a
    return RewardBundle(
        global_xp=max(a.global_xp, b.global_xp),
        game_xp=max(a.game_xp, b.game_xp),
        currency=max(a.currency, b.currency),
    )


@dataclass(frozen=True)
class OptionReward:
    """The reward one menu option mints when resolved (``None`` = narrate-only)."""

    scene_id: str
    option_id: str
    effect_id: str
    reward: Optional[RewardBundle]
    is_noop: bool  # True when the option mints no reward (narrate-only / no-op)


@dataclass(frozen=True)
class SceneBalance:
    """Per-scene aggregate: the menu size, its no-op count, and its max reward."""

    scene_id: str
    option_count: int
    noop_count: int
    max_reward: Optional[RewardBundle]  # component-wise max across this scene's options
    options: tuple[OptionReward, ...]


@dataclass(frozen=True)
class MenuBalanceReport:
    """The bounded-menu economy, sim-pinned across every scene × option.

    ``all_within_global_max`` is the headline no-pay-to-win flag: True iff EVERY
    option's reward is ``<= catalog.GLOBAL_MAX`` component-wise. ``global_max_reward``
    is the component-wise max reward across all options in all scenes (``None`` if no
    option mints anything).
    """

    by_scene: dict[str, SceneBalance]
    global_max_reward: Optional[RewardBundle]
    total_options: int
    total_noops: int
    all_within_global_max: bool
    seeds: int

    def scene(self, scene_id: str) -> SceneBalance:
        return self.by_scene[scene_id]


def _resolve_option_reward(
    scene: Scene, option_id: str, *, seed: int
) -> OptionReward:
    """Resolve one option's PRE-DEFINED effect through the shipped resolver."""
    # Full XP surfaces the whole menu so the option is a genuine, non-clamped choice;
    # the resolver applies the option's code-owned effect deterministically (seeded).
    res = resolve(
        scene, DMChoice(option_id=option_id), xp=_FULL_MENU_XP, seed=seed
    )
    return OptionReward(
        scene_id=scene.scene_id,
        option_id=option_id,
        effect_id=res.effect_id,
        reward=res.reward,
        is_noop=res.reward is None,
    )


def _scene_balance(scene: Scene, seeds: range) -> SceneBalance:
    """Enumerate every option in ``scene`` and aggregate its rewards.

    Rewards are code-owned and seed-independent by construction (the escort effect
    mints exactly ``catalog.TIER_CAPS[tier]``, no-ops mint nothing), so sweeping the
    seed range only *proves* that invariance — the aggregate is identical each seed.
    """
    options: tuple[OptionReward, ...] = ()
    for opt in scene.options:
        # Sweep the seeds; the reward must be identical across every seed (code-owned,
        # not seed-sized). Assert that invariance rather than silently taking one.
        rewards = {
            _resolve_option_reward(scene, opt.id, seed=seed).reward for seed in seeds
        }
        if len(rewards) != 1:
            raise AssertionError(
                f"scene {scene.scene_id!r} option {opt.id!r}: reward not seed-stable: "
                f"{sorted(str(r) for r in rewards)}"
            )
        reward = next(iter(rewards))
        options += (
            OptionReward(
                scene_id=scene.scene_id,
                option_id=opt.id,
                effect_id=opt.effect_id,
                reward=reward,
                is_noop=reward is None,
            ),
        )

    max_reward: Optional[RewardBundle] = None
    for o in options:
        max_reward = _component_max(max_reward, o.reward)
    noop_count = sum(1 for o in options if o.is_noop)
    return SceneBalance(
        scene_id=scene.scene_id,
        option_count=len(options),
        noop_count=noop_count,
        max_reward=max_reward,
        options=options,
    )


def run(
    *,
    seeds: range = range(256),
    scenes: dict[str, Scene] = SCENES,
) -> MenuBalanceReport:
    """Enumerate every scene × option, resolve each, and aggregate the economy.

    Deterministic and pure: same call -> identical report (rewards are code-owned and
    seed-independent; the only RNG is the resolver's seeded ``DetRng``). Proves the
    bounded-menu economy — every option's reward ``<= catalog.GLOBAL_MAX``, no-ops
    mint nothing (Q-0040 / D-0007, no pay-to-win).
    """
    by_scene: dict[str, SceneBalance] = {
        scene_id: _scene_balance(scene, seeds)
        for scene_id, scene in scenes.items()
    }

    global_max: Optional[RewardBundle] = None
    total_options = 0
    total_noops = 0
    all_within = True
    for balance in by_scene.values():
        total_options += balance.option_count
        total_noops += balance.noop_count
        global_max = _component_max(global_max, balance.max_reward)
        for o in balance.options:
            if o.reward is not None and not _reward_leq_global_max(o.reward):
                all_within = False

    return MenuBalanceReport(
        by_scene=by_scene,
        global_max_reward=global_max,
        total_options=total_options,
        total_noops=total_noops,
        all_within_global_max=all_within,
        seeds=len(seeds),
    )


def _fmt_reward(reward: Optional[RewardBundle]) -> str:
    if reward is None:
        return "—  (narrate-only, mints nothing)"
    return (
        f"global_xp={reward.global_xp} game_xp={reward.game_xp} "
        f"currency={reward.currency}"
    )


def format_report(report: MenuBalanceReport) -> str:
    cap = catalog.GLOBAL_MAX
    lines: list[str] = []
    lines.append(f"seeds swept: {report.seeds:,}")
    lines.append(
        f"scenes: {len(report.by_scene)}   options: {report.total_options}   "
        f"no-op options: {report.total_noops}"
    )
    lines.append(
        "global reward ceiling (catalog.GLOBAL_MAX): "
        f"global_xp={cap.global_xp} game_xp={cap.game_xp} currency={cap.currency}"
    )
    lines.append("")
    for scene_id in report.by_scene:
        b = report.scene(scene_id)
        lines.append(
            f"[{scene_id}]  options={b.option_count}  no-ops={b.noop_count}"
        )
        for o in b.options:
            tag = "no-op " if o.is_noop else "reward"
            lines.append(
                f"  {o.option_id:<16} {o.effect_id:<14} {tag}: {_fmt_reward(o.reward)}"
            )
        lines.append(f"  -> per-scene max reward: {_fmt_reward(b.max_reward)}")
        lines.append("")
    lines.append(f"global max reward across all options: {_fmt_reward(report.global_max_reward)}")
    lines.append(
        "all options <= GLOBAL_MAX (no pay-to-win): "
        f"{report.all_within_global_max}"
    )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_report(run()))
