"""Encounter-sim harness: the percentile helper + the balance-report renderer.

`tests/mining/test_encounters.py` pins the sweep loop and the sim-pinned
outcome distributions; this module pins the two pieces it leaves untested —
``_percentile`` (the reward-yield p50/p90 the design doc quotes) and
``format_report`` (section order, the per-depth ``n/a`` zero-denominator
branch, the empty-reward-kind skip, and the energy-line-only-when-triggered
rule). Tests only, at EXISTING constants.
"""

from __future__ import annotations

from collections import Counter

import pytest

from games.mining.sim import encounters_sim as sim

# A cheap, deterministic sweep — big enough to trigger every kind at least once
# (encounter rate is sim-pinned to 8–15%), small enough to stay fast.
_SMALL_RUN_KW = dict(seeds=range(2), coord=range(-8, 8), depths=(0, 8, 15))
_SMALL_RUN_ACTIONS = 2 * 16 * 16 * 3  # seeds × x × y × depths = 1,536


# ---------------------------------------------------------------------------
# _percentile — the quantile read the design-doc yield table quotes.
# ---------------------------------------------------------------------------
def test_percentile_empty_returns_zero() -> None:
    assert sim._percentile([], 0.5) == 0.0


def test_percentile_singleton_is_that_value_at_any_pct() -> None:
    assert sim._percentile([7], 0.0) == 7.0
    assert sim._percentile([7], 0.5) == 7.0
    assert sim._percentile([7], 1.0) == 7.0


def test_percentile_sorts_its_input() -> None:
    # Unsorted input: p0 is the min and p100 the max, not the endpoints as given.
    values = [30, 10, 20]
    assert sim._percentile(values, 0.0) == 10.0
    assert sim._percentile(values, 1.0) == 30.0
    assert values == [30, 10, 20]  # caller's list is not mutated


def test_percentile_median_uses_pythons_round_half_even() -> None:
    # 10 items → k = round(0.5 * 9) = round(4.5) = 4 (banker's rounding), so the
    # p50 of 1..10 is the LOWER middle, 5.0 — pinned so a reimplementation with
    # half-up rounding (k=5 → 6.0) reddens the doc'd yield table.
    assert sim._percentile(list(range(1, 11)), 0.5) == 5.0
    # Odd count has a true middle: p50 of 1..11 is 6.0.
    assert sim._percentile(list(range(1, 12)), 0.5) == 6.0
    # p90 of 1..11 → k = round(0.9 * 10) = 9 → 10.0.
    assert sim._percentile(list(range(1, 12)), 0.9) == 10.0


def test_percentile_clamps_overshooting_pct_to_max() -> None:
    # k is clamped to the last index, so pct > 1 degrades to the max, not IndexError.
    assert sim._percentile([1, 2, 3], 2.0) == 3.0


# ---------------------------------------------------------------------------
# format_report — hand-built reports pin the renderer's branch behavior.
# ---------------------------------------------------------------------------
def _tiny_report() -> sim.SimReport:
    """10 actions, 1 hazard; one depth bucket with zero actions; only the
    hazard reward kind non-empty; no energy costs recorded."""
    report = sim.SimReport(actions=10, kind_counts=Counter({"none": 9, "hazard": 1}))
    report.depth_kind_counts = {5: Counter()}
    report.hazard_by_tier = {"fresh": sim.HazardTierStats(won=1, damage_total=4)}
    report.baseline_hazard_by_depth = {5: sim.HazardTierStats()}
    report.reward_amounts = {"loot_cache": [], "rich_vein": [], "hazard": [2, 4]}
    return report


def test_format_report_renders_na_for_a_depth_with_no_actions() -> None:
    lines = sim.format_report(_tiny_report()).splitlines()
    depth_line = next(l for l in lines if l.startswith("  z=5") and "n/a" in l)
    assert depth_line == "  z=5     n/a"


def test_format_report_skips_empty_reward_kinds_and_energy_line() -> None:
    text = sim.format_report(_tiny_report())
    reward_section = text.split("reward yield", 1)[1]
    # Only the non-empty kind is rendered; empty aggregates are skipped, not 0-rowed.
    assert "hazard" in reward_section
    assert "loot_cache" not in reward_section
    assert "rich_vein" not in reward_section
    # No triggered-encounter energy was recorded → the energy line is absent.
    assert "mean energy cost" not in text


def test_format_report_reward_line_mean_p50_p90_max() -> None:
    text = sim.format_report(_tiny_report())
    # amounts [2, 4]: mean 3.0, p50 = 2 (k=round(0.5)=0, half-even), p90 = 4, max 4.
    assert "  hazard        3.0 /    2 /    4 /    4  (n=2)" in text


def test_format_report_zero_totals_render_as_zero_rates_not_errors() -> None:
    # An empty per-depth bucket renders 0% / 0 damage via HazardTierStats' guards.
    text = sim.format_report(_tiny_report())
    assert "  z=5   won  0.0%  fled  0.0%  lost  0.0%  dmg  0.0  (n=0)" in text


def test_format_report_with_zero_actions_raises_zero_division() -> None:
    # PINNED CURRENT BEHAVIOR (latent bug, not changed here): the kind-frequency
    # lines divide by report.actions without the guard that SimReport.encounter_rate
    # has, so formatting a truly empty report raises ZeroDivisionError instead of
    # rendering an empty table. Callers must not format a zero-action report.
    with pytest.raises(ZeroDivisionError):
        sim.format_report(sim.SimReport())


# ---------------------------------------------------------------------------
# format_report — end-to-end over a real (deterministic) sweep.
# ---------------------------------------------------------------------------
def test_format_report_sections_in_documented_order() -> None:
    text = sim.format_report(sim.run(**_SMALL_RUN_KW))
    headers = (
        "actions sampled:",
        "overall encounter rate:",
        "kind frequency (overall):",
        "hazard chance by depth",
        "hazard resolution by tier",
        "baseline-tier hazard resolution by depth",
        "reward yield",
        "mean energy cost per triggered encounter:",
    )
    positions = [text.index(h) for h in headers]  # raises if a section vanished
    assert positions == sorted(positions)
    # Kind rows keep their fixed none→hazard→loot_cache→rich_vein order.
    kind_positions = [text.index(f"  {k:<11}") for k in ("none", "hazard", "loot_cache", "rich_vein")]
    assert kind_positions == sorted(kind_positions)
    # One tier row per representative tier, in tier_stats() order.
    tier_positions = [text.index(f"  {name:<8} won") for name in ("fresh", "geared", "veteran")]
    assert tier_positions == sorted(tier_positions)


def test_format_report_counts_use_thousands_separators() -> None:
    report = sim.run(**_SMALL_RUN_KW)
    text = sim.format_report(report)
    assert report.actions == _SMALL_RUN_ACTIONS
    assert f"actions sampled: {_SMALL_RUN_ACTIONS:,}" in text  # "1,536" — comma pinned
    # At the sim-pinned 8–15% trigger rate this sweep records energy costs, so the
    # energy line is present and carries the 2-decimal mean.
    mean_e = sum(report.energy_costs) / len(report.energy_costs)
    assert f"mean energy cost per triggered encounter: {mean_e:.2f}" in text


def test_renderer_kind_list_covers_every_observed_kind() -> None:
    # The renderer iterates a HARDCODED kind tuple; if the encounter model ever
    # grows a new kind, this catches it being silently dropped from the report.
    report = sim.run(**_SMALL_RUN_KW)
    assert set(report.kind_counts) <= {"none", "hazard", "loot_cache", "rich_vein"}


def test_format_report_is_a_pure_function_of_the_sweep() -> None:
    # Same bounds → byte-identical report text (the module docstring's purity claim,
    # extended through the renderer).
    assert sim.format_report(sim.run(**_SMALL_RUN_KW)) == sim.format_report(
        sim.run(**_SMALL_RUN_KW)
    )
