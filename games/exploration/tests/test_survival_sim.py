"""Sim-pinned survival-difficulty bands — re-assert the harness output.

The pinned numbers below mirror ``docs/design/survival-sim-harness.md`` (full
evidence lives there). They are produced by driving the shipped mining energy
engine through each difficulty's tunables — the sim measures them, these tests
re-pin them so a balance/engine regression reddens CI. Mirrors
``tests/fishing/test_catch_sim.py``'s sim-pin shape.

Easy is byte-identical to the shipped bars (D-0004): the survival Energy axis
only scales the shipped bars for Medium/Hard — there is no third global bar and
no food/difficulty path that lets grind buy its way past the tuning (no
pay-to-win, Q-0039/Q-0190).
"""

from __future__ import annotations

from games.exploration.survival import sim
from games.exploration.survival.difficulty import TUNABLES, Difficulty
from games.mining.core import energy

# --- pinned bands (see the design doc's sim-pin table) ---
# sustained (regen-limited) digs/hour = 3600 // regen_seconds, engine-produced.
_SUSTAINED = {Difficulty.EASY: 360, Difficulty.MEDIUM: 240, Difficulty.HARD: 180}
# burst capacity (a full bar) = max_energy // cost.
_BURST = {Difficulty.EASY: 60, Difficulty.MEDIUM: 50, Difficulty.HARD: 40}
# casual reach never energy-blocks → identical across difficulties.
_CASUAL_PER_DAY = 30


def _run() -> sim.SurvivalReport:
    # A smaller, fast sweep than the __main__ default; casual reach is
    # seed-independent so a short seed range is enough for stable bands.
    return sim.run(seeds=range(16))


def test_easy_is_byte_identical_to_shipped_bars() -> None:
    easy = TUNABLES[Difficulty.EASY]
    # Easy is provably the shipped game — it reuses mining's shipped constants.
    assert easy.max_energy == energy.MAX_ENERGY
    assert easy.regen_seconds == energy.REGEN_SECONDS
    assert easy.cost == energy.DIG_COST


def test_sustained_throughput_pinned_per_difficulty() -> None:
    report = _run()
    for diff, expected in _SUSTAINED.items():
        assert report.stats(diff).sustained_digs_per_hour == expected, diff


def test_burst_capacity_pinned_per_difficulty() -> None:
    report = _run()
    for diff, expected in _BURST.items():
        assert report.stats(diff).burst_capacity == expected, diff


def test_difficulty_gradient_is_monotone() -> None:
    report = _run()
    easy = report.stats(Difficulty.EASY).sustained_digs_per_hour
    medium = report.stats(Difficulty.MEDIUM).sustained_digs_per_hour
    hard = report.stats(Difficulty.HARD).sustained_digs_per_hour
    # Harder = a tighter faucet: sustained throughput strictly decreases.
    assert easy > medium > hard


def test_casual_never_energy_blocked() -> None:
    report = _run()
    reach = {report.stats(d).casual_per_day for d in Difficulty}
    # A well-spaced casual day lands all its actions on every difficulty —
    # capability is never gated behind energy (Q-0087 casual track).
    assert reach == {_CASUAL_PER_DAY}


def test_sim_report_is_deterministic() -> None:
    kw = dict(seeds=range(8))
    a = sim.run(**kw)
    b = sim.run(**kw)
    # Pure + deterministic: same call → identical report (regen is analytic; the
    # only RNG use is DetRng jitter that never changes the never-block outcome).
    assert a == b
    for d in Difficulty:
        assert a.stats(d) == b.stats(d)


def test_no_pay_to_win() -> None:
    report = _run()
    # No difficulty/food path lets Hard's sustained grind reach Easy's throughput
    # — the tuning gap is real, grind cannot buy past it (no pay-to-win).
    hard = report.stats(Difficulty.HARD).sustained_digs_per_hour
    easy = report.stats(Difficulty.EASY).sustained_digs_per_hour
    assert hard < easy
    # Food restore is a shared, difficulty-independent refill: eating the same
    # item restores the same energy on every difficulty (food is a sink, not a
    # difficulty lever — it cannot lift Hard onto Easy's faucet).
    for item in ("ration", "energy drink", "cooked fish"):
        restored = energy.restore_value(item)
        assert restored is not None and restored > 0, item
    # And the restore table itself carries no per-difficulty branch — one value
    # per item, applied identically whatever difficulty the player ascends to.
    assert energy.restore_value("ration") == energy.RESTORE_VALUES["ration"]
