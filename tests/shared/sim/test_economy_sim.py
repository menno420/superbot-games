"""Cross-domain economy sim — the whole-economy emission pins + global invariants.

Re-asserts the three named invariants (``GRANT_WITHIN_GLOBAL_CAP``,
``ITEM_FAUCET_MINTS_NO_CURRENCY``, ``NOOP_MINTS_NOTHING``) and the sim-pinned
per-domain emission bands over a smaller sweep, so a cross-domain balance
regression reddens CI. The full-scale evidence + pinned-table live in
``docs/design/economy-sim.md``.
"""

from __future__ import annotations

import subprocess
import sys

from games.exploration.quest import catalog
from games.shared.sim import economy_sim as sim

# A smaller sweep than the sim default — fast, still stable at the pinned bands.
_KW = dict(seeds=range(8), digs_per_seed=300, casts_per_seed=300)


def test_all_bundles_within_global_cap() -> None:
    report = sim.run(**_KW)
    assert sim.all_bundles_within_global_cap(report) is True
    assert report.grant_within_global_cap is True

    # Directly: every quest tier bundle AND the dnd escort bundle <= GLOBAL_MAX.
    cap = (
        catalog.GLOBAL_MAX.global_xp,
        catalog.GLOBAL_MAX.game_xp,
        catalog.GLOBAL_MAX.currency,
    )
    for bundle in catalog.TIER_CAPS.values():
        tup = (bundle.global_xp, bundle.game_xp, bundle.currency)
        assert all(c <= limit for c, limit in zip(tup, cap)), tup
    assert report.dnd.per_completion_bundle is not None
    assert all(
        c <= limit for c, limit in zip(report.dnd.per_completion_bundle, cap)
    ), report.dnd.per_completion_bundle


def test_item_faucets_mint_no_currency_or_xp() -> None:
    report = sim.run(**_KW)
    assert sim.item_faucets_mint_no_currency_or_xp(report) is True
    for domain in (report.mining, report.fishing):
        assert domain.native_currency_per_hour == 0.0
        assert domain.native_global_xp_per_hour == 0.0
        assert domain.native_game_xp_per_hour == 0.0
        # Item faucets DO mint items.
        assert domain.items_per_hour > 0.0


def test_noop_paths_mint_nothing() -> None:
    # Resolves the real dnd/mining/fishing no-op paths through the shipped code.
    assert sim.noop_paths_mint_nothing() is True


def test_mining_emission_within_pinned_band() -> None:
    lo, hi = sim._MINING_ORE_PER_HOUR
    items_per_hour = sim.run(**_KW).mining.items_per_hour
    assert lo <= items_per_hour <= hi, items_per_hour


def test_fishing_emission_within_pinned_band() -> None:
    lo, hi = sim._FISHING_FISH_PER_HOUR
    items_per_hour = sim.run(**_KW).fishing.items_per_hour
    assert lo <= items_per_hour <= hi, items_per_hour


def test_report_is_deterministic_within_process() -> None:
    a = sim.run(**_KW)
    b = sim.run(**_KW)
    assert a == b


def test_report_is_deterministic_across_process() -> None:
    # A fresh interpreter (PYTHONHASHSEED randomised) must produce the identical
    # pinned emission values — proving the sweep never depends on str-hashing.
    report = sim.run(**_KW)
    inproc = (
        f"{report.mining.items_per_hour:.6f}|{report.fishing.items_per_hour:.6f}|"
        f"{report.dnd.per_completion_bundle}|{report.exploration.per_completion_bundle}|"
        f"{report.global_cap}"
    )
    code = (
        "from games.shared.sim import economy_sim as sim;"
        "r = sim.run(seeds=range(8), digs_per_seed=300, casts_per_seed=300);"
        "print(f'{r.mining.items_per_hour:.6f}|{r.fishing.items_per_hour:.6f}|"
        "{r.dnd.per_completion_bundle}|{r.exploration.per_completion_bundle}|{r.global_cap}')"
    )
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        cwd=_repo_root(),
        env=_randomized_hashseed_env(),
    ).stdout.strip()
    assert out == inproc


def _repo_root() -> str:
    import os

    # tests/shared/sim/ -> repo root is three levels up.
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )


def _randomized_hashseed_env() -> dict[str, str]:
    import os

    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "random"
    return env
