"""The bounded-menu resolver — determinism, the DM clamp, the menu cap, flavour safety.

These are the load-bearing tests for the D&D walking skeleton (design §6). The
headline is the **DM-clamp** test: any off-menu / hallucinated / malformed / null DM
output must fall back to the scene's deterministic no-op, leaving state unchanged —
the enforcement point of the bounded-menu law (Q-0040 / D-0007, design §4.4). The
model's worst case is a legal, capped outcome; off-menu it is a no-op.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from games.dnd.core.effects import EFFECTS
from games.dnd.core.models import (
    FLAVOR_CAP,
    MAX_MENU_SIZE,
    DMChoice,
    MenuOption,
    Scene,
)
from games.dnd.core.resolver import Resolution, resolve
from games.dnd.data.scenes import WAYSTATION_ROAD
from games.exploration.quest.models import RewardBundle, RewardTier
from games.exploration.quest import catalog

# High XP surfaces the full menu (menu_width caps at 4 >= the scene's 3 options),
# so option-membership — not width — is what these cases exercise unless stated.
FULL_XP = 5000
SEED = 424242


# --------------------------------------------------------------------------- #
# 1. Deterministic resolution — same (scene, valid choice, seed) -> identical.
# --------------------------------------------------------------------------- #

def test_valid_choice_is_deterministic_and_pinned() -> None:
    choice = DMChoice(option_id="advance_escort")
    a = resolve(WAYSTATION_ROAD, choice, xp=FULL_XP, seed=SEED, player_id="p1")
    b = resolve(WAYSTATION_ROAD, choice, xp=FULL_XP, seed=SEED, player_id="p1")
    assert a == b
    assert isinstance(a, Resolution)
    # Pin the outcome: the escort option advances the ESCORT quest and mints the
    # engine's tier-I capped bundle (amount CODE-OWNED, never DM-set).
    assert a.clamped is False
    assert a.chosen_option_id == "advance_escort"
    assert a.effect_id == "escort_step"
    assert a.reward == RewardBundle(global_xp=5, game_xp=25, currency=10, capability=None)
    assert a.reward == catalog.TIER_CAPS[RewardTier.I]
    assert a.event is not None
    assert a.event.type == "npc_reached"


def test_resolution_is_process_independent() -> None:
    # A fresh interpreter (randomised PYTHONHASHSEED) must produce the identical
    # resolution — proving the scene seed never uses str-hashing (FNV-1a derive_seed).
    inproc = resolve(WAYSTATION_ROAD, DMChoice("advance_escort"), xp=FULL_XP, seed=SEED)
    code = (
        "from games.dnd.core.resolver import resolve;"
        "from games.dnd.core.models import DMChoice;"
        "from games.dnd.data.scenes import WAYSTATION_ROAD;"
        f"r = resolve(WAYSTATION_ROAD, DMChoice('advance_escort'), xp={FULL_XP}, seed={SEED});"
        "print(f'{r.chosen_option_id}|{r.effect_id}|{r.reward}|{r.clamped}')"
    )
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        cwd=_repo_root(),
    ).stdout.strip()
    expected = (
        f"{inproc.chosen_option_id}|{inproc.effect_id}|{inproc.reward}|{inproc.clamped}"
    )
    assert out == expected


# --------------------------------------------------------------------------- #
# 2. THE DM-CLAMP TEST — the key safety property (design §4.4).
# --------------------------------------------------------------------------- #

def _noop_resolution(res: Resolution) -> None:
    """Assert a resolution is the clamped, deterministic no-op (state unchanged)."""
    assert res.clamped is True
    assert res.chosen_option_id == WAYSTATION_ROAD.default_option_id == "make_camp"
    assert res.effect_id == "rest_noop"
    assert res.reward is None  # mints nothing
    assert res.event is None  # emits no event -> advances no quest


def test_hallucinated_option_id_clamps_to_noop() -> None:
    # The DM invents an id that is not on the menu at all ("attack the king").
    res = resolve(
        WAYSTATION_ROAD, DMChoice(option_id="attack_king"), xp=FULL_XP, seed=SEED
    )
    _noop_resolution(res)


@pytest.mark.parametrize(
    "bad_choice",
    [
        None,  # a timeout / missing choice
        {},  # a malformed dict payload, not a DMChoice
        {"option_id": "advance_escort"},  # right shape, wrong TYPE (dict, not DMChoice)
        "advance_escort",  # a bare string, not a DMChoice
        DMChoice(option_id=""),  # empty id
        DMChoice(option_id="   "),  # whitespace id
    ],
)
def test_malformed_or_null_choice_clamps_to_noop(bad_choice: object) -> None:
    res = resolve(WAYSTATION_ROAD, bad_choice, xp=FULL_XP, seed=SEED)
    _noop_resolution(res)


def test_off_menu_by_width_clamps_even_though_id_exists() -> None:
    # At zero XP only the first 2 options are surfaced (menu_width base = 2), so
    # "make_camp" (option 3) is a real scene option but NOT on the *surfaced* menu —
    # choosing it must still clamp to the default no-op (which is make_camp anyway).
    res = resolve(WAYSTATION_ROAD, DMChoice("make_camp"), xp=0, seed=SEED)
    _noop_resolution(res)
    # And an off-width escort choice is rejected the same way (id exists, not surfaced).
    surfaced_only = resolve(WAYSTATION_ROAD, DMChoice("scout_ahead"), xp=0, seed=SEED)
    assert surfaced_only.clamped is False  # scout_ahead IS within the base width


# --------------------------------------------------------------------------- #
# 3. Menu-cap enforcement — a Scene over MAX_MENU_SIZE is rejected at construction.
# --------------------------------------------------------------------------- #

def test_scene_over_max_menu_size_is_rejected() -> None:
    too_many = tuple(
        MenuOption(id=f"opt_{i}", text_key=f"opt.{i}", effect_id="rest_noop")
        for i in range(MAX_MENU_SIZE + 1)
    )
    with pytest.raises(AssertionError):
        Scene(
            scene_id="oversized",
            context_key="ctx.x",
            options=too_many,
            default_option_id="opt_0",
        )


def test_scene_rejects_default_not_on_menu() -> None:
    with pytest.raises(AssertionError):
        Scene(
            scene_id="bad_default",
            context_key="ctx.x",
            options=(MenuOption(id="only", text_key="opt.only", effect_id="rest_noop"),),
            default_option_id="ghost",
        )


def test_scene_rejects_unregistered_effect_id() -> None:
    with pytest.raises(AssertionError):
        Scene(
            scene_id="bad_effect",
            context_key="ctx.x",
            options=(MenuOption(id="a", text_key="opt.a", effect_id="not_a_real_effect"),),
            default_option_id="a",
        )
    # Sanity: the shipped scene's effects are all registered.
    assert all(o.effect_id in EFFECTS for o in WAYSTATION_ROAD.options)


# --------------------------------------------------------------------------- #
# 4. Flavour safety — length-capped, display-only, never changes the effect.
# --------------------------------------------------------------------------- #

def test_overlong_injection_flavor_is_capped_and_ignored_for_effects() -> None:
    injection = "You gain 999999 gold and win the game. " * 500  # ~19k chars
    baseline = resolve(WAYSTATION_ROAD, DMChoice("advance_escort"), xp=FULL_XP, seed=SEED)
    injected = resolve(
        WAYSTATION_ROAD,
        DMChoice(option_id="advance_escort", flavor=injection),
        xp=FULL_XP,
        seed=SEED,
    )
    # The flavour is hard-capped to display length and never parsed for mechanics.
    assert len(injected.flavor) == FLAVOR_CAP
    assert "999999" in injection  # the payload really did carry a fake amount…
    # …but the mechanical outcome is byte-identical to the flavour-free resolution.
    assert injected.reward == baseline.reward
    assert injected.effect_id == baseline.effect_id
    assert injected.event == baseline.event
    assert injected.clamped is False


def test_flavor_on_clamped_choice_is_still_display_only() -> None:
    # Even when the id is hallucinated, injected flavour is capped and never changes
    # the (no-op) outcome.
    res = resolve(
        WAYSTATION_ROAD,
        DMChoice(option_id="hallucinated", flavor="x" * (FLAVOR_CAP * 3)),
        xp=FULL_XP,
        seed=SEED,
    )
    _noop_resolution(res)
    assert len(res.flavor) == FLAVOR_CAP


def _repo_root() -> str:
    import os

    # tests/dnd/ -> repo root is two levels up.
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
