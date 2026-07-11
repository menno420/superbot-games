"""Survival sim harness — drives the shipped energy engine per difficulty.

Pure + deterministic (mirrors ``games.fishing.sim.catch_sim``): for each
difficulty it drives the REAL shipped mining energy engine
(``games.mining.core.energy`` — ``settle`` / ``can_dig`` / ``spend`` /
``seconds_until``) through that difficulty's ``max_energy=/regen_seconds=/cost=``
tunables and reads three Q-0087 dual-track curves back out:

- **casual/day** — a well-spaced ~30-action schedule that never energy-blocks
  (the casual player's daily reach). DetRng only jitters the action spacing; the
  outcome is 30 on every difficulty (casual is never gated).
- **grinder surplus/hr** — the regen-limited sustained throughput (digs/hour a
  grinder can sustain once the opening burst is spent). This is **produced by the
  engine**, not hardcoded: an empty-bar greedy digger is driven over a simulated
  hour and the resulting dig count is read off — it lands on ``3600 //
  regen_seconds`` because regen is analytic, and the tests re-pin that exact
  number.
- **capability-gap** — an 8-hour grind (full opening burst + sustained) divided
  by casual/day: how far grind out-runs casual. Grind earns prestige, never
  gates casual (Q-0087).

Easy drives the shipped constants unchanged, so its numbers are the base game's
(D-0004). No third global energy bar — difficulty is just the engine's kwargs.

Run it:  ``python3 -m games.exploration.survival.sim``
"""

from __future__ import annotations

from dataclasses import dataclass

from games.exploration.quest.rng import DetRng, derive_seed
from games.exploration.survival.difficulty import (
    TUNABLES,
    Difficulty,
    SurvivalTunables,
)
from games.mining.core import energy
from games.mining.core.energy import EnergyState

_HOUR_SECONDS = 3600
_DAY_SECONDS = 86_400
_GRINDER_HOURS = 8
_CASUAL_ACTIONS = 30


@dataclass(frozen=True)
class DifficultyStats:
    """Sim-measured aggregates for one difficulty (one energy tuning)."""

    difficulty: Difficulty
    max_energy: int
    regen_seconds: int
    cost: int
    burst_capacity: int
    sustained_digs_per_hour: int
    casual_per_day: int
    grinder_8h: int
    capability_gap: float


@dataclass(frozen=True)
class SurvivalReport:
    """Per-difficulty aggregates + the sweep bounds that produced them."""

    by_difficulty: dict[Difficulty, DifficultyStats]
    seeds: int
    casual_actions: int

    def stats(self, difficulty: Difficulty) -> DifficultyStats:
        return self.by_difficulty[difficulty]


def _greedy_digs(t: SurvivalTunables, *, horizon: int, start_full: bool) -> int:
    """Drive the real engine: greedily dig for *horizon* seconds, return the count.

    ``start_full=False`` starts on an empty bar so the count isolates the
    regen-limited steady state (no opening burst); ``start_full=True`` starts on
    a full bar so the count includes the opening burst then the sustained tail.
    The loop advances to the next instant a dig is affordable via
    ``seconds_until`` (never busy-loops), then spends through ``energy.spend`` —
    so the number is produced by the shipped engine, not computed here.
    """
    state = EnergyState(t.max_energy if start_full else 0, 0)
    now = 0
    digs = 0
    while True:
        wait = energy.seconds_until(
            state,
            now,
            t.cost,
            max_energy=t.max_energy,
            regen_seconds=t.regen_seconds,
        )
        now += wait
        if now > horizon:
            break
        if not energy.can_dig(
            state,
            now,
            cost=t.cost,
            max_energy=t.max_energy,
            regen_seconds=t.regen_seconds,
        ):
            break
        state = energy.spend(
            state,
            now,
            cost=t.cost,
            max_energy=t.max_energy,
            regen_seconds=t.regen_seconds,
        )
        digs += 1
    return digs


def _casual_digs(t: SurvivalTunables, difficulty: Difficulty, seed: int) -> int:
    """Drive a ~30-action, well-spaced day; count the actions that land.

    Spacing (``_DAY_SECONDS / _CASUAL_ACTIONS`` ≈ 2880s) dwarfs any difficulty's
    regen interval, so the bar is always refilled between actions and none blocks
    — the count is 30 on every difficulty. DetRng only jitters the spacing (a
    quarter-window wobble), never enough to eat into the regen headroom, so the
    determinism holds regardless of seed.
    """
    rng = DetRng(derive_seed("survival-casual", difficulty.name, seed))
    spacing = _DAY_SECONDS // _CASUAL_ACTIONS
    state = EnergyState(t.max_energy, 0)
    digs = 0
    for i in range(_CASUAL_ACTIONS):
        jitter = rng.randint(0, spacing // 4)
        now = i * spacing + jitter
        if energy.can_dig(
            state,
            now,
            cost=t.cost,
            max_energy=t.max_energy,
            regen_seconds=t.regen_seconds,
        ):
            state = energy.spend(
                state,
                now,
                cost=t.cost,
                max_energy=t.max_energy,
                regen_seconds=t.regen_seconds,
            )
            digs += 1
    return digs


def _difficulty_stats(
    difficulty: Difficulty, t: SurvivalTunables, seeds: range
) -> DifficultyStats:
    burst = t.max_energy // t.cost
    sustained = _greedy_digs(t, horizon=_HOUR_SECONDS, start_full=False)
    grinder_8h = _greedy_digs(
        t, horizon=_GRINDER_HOURS * _HOUR_SECONDS, start_full=True
    )
    # Casual reach is seed-independent by construction; sweep the seeds and take
    # the common value (asserting the sim really never blocks a casual player).
    casual_values = {_casual_digs(t, difficulty, seed) for seed in seeds}
    if len(casual_values) != 1:
        raise AssertionError(
            f"casual reach not seed-stable for {difficulty}: {sorted(casual_values)}"
        )
    casual = next(iter(casual_values))
    gap = grinder_8h / casual if casual else 0.0
    return DifficultyStats(
        difficulty=difficulty,
        max_energy=t.max_energy,
        regen_seconds=t.regen_seconds,
        cost=t.cost,
        burst_capacity=burst,
        sustained_digs_per_hour=sustained,
        casual_per_day=casual,
        grinder_8h=grinder_8h,
        capability_gap=gap,
    )


def run(
    *,
    seeds: range = range(400),
    difficulties: tuple[Difficulty, ...] = tuple(Difficulty),
) -> SurvivalReport:
    """Drive the shipped energy engine per difficulty; aggregate the curves.

    Deterministic and pure: same call → identical report (regen is analytic; the
    only RNG use is DetRng jitter on casual spacing, which never changes the
    never-block outcome). Easy drives the shipped constants unchanged, so its
    numbers are the base game's (D-0004).
    """
    by_difficulty = {
        d: _difficulty_stats(d, TUNABLES[d], seeds) for d in difficulties
    }
    return SurvivalReport(
        by_difficulty=by_difficulty,
        seeds=len(seeds),
        casual_actions=_CASUAL_ACTIONS,
    )


def format_report(report: SurvivalReport) -> str:
    lines: list[str] = []
    lines.append(f"seeds swept: {report.seeds:,}   casual actions/day: {report.casual_actions}")
    lines.append("")
    lines.append("per-difficulty energy tuning (Easy ≡ shipped bars — D-0004):")
    header = (
        f"  {'difficulty':<8}{'cap':>5}{'regen_s':>9}{'cost':>6}"
        f"{'burst':>7}{'sustain/hr':>12}{'casual/day':>12}"
        f"{'grind8h':>9}{'gap':>8}"
    )
    lines.append(header)
    for d in Difficulty:
        if d not in report.by_difficulty:
            continue
        s = report.by_difficulty[d]
        lines.append(
            f"  {d.value:<8}{s.max_energy:>5}{s.regen_seconds:>9}{s.cost:>6}"
            f"{s.burst_capacity:>7}{s.sustained_digs_per_hour:>12}"
            f"{s.casual_per_day:>12}{s.grinder_8h:>9}{s.capability_gap:>8.1f}"
        )
    lines.append("")
    lines.append(
        "curves: casual/day (Q-0087 casual reach) · sustain/hr (grinder surplus/hr) · "
        "gap = grind8h / casual/day"
    )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_report(run()))
