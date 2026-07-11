# Survival sim harness — sim-pinned difficulty bands (IMPLEMENTED)

> **Status:** `reference` · lane: game-exploration · 2026-07-11 · (P2 harness IMPLEMENTED)
>
> A pure, deterministic sim that drives the **shipped** mining energy engine
> (`games.mining.core.energy`) through per-difficulty tunables and pins the Q-0087
> dual-track throughput curves as tests — so a survival-difficulty tuning is *proven
> against the bar before it ships*. Companion to `docs/design/survival-d1-rebaseline.md`
> (whose D-0004 re-baseline this implements) and mirrors the mining/fishing `sim/`
> sim-pin discipline.

Purpose: exploration P2 (`docs/founding-plan-exploration.md` §3) asks for a survival
overlay whose difficulty gradient is *measured, not asserted*. This slice stands up the
thinnest provable core: a sim that reads the throughput curves back out of the real
engine per difficulty, and a fast test suite that re-pins those numbers so a balance or
engine regression reddens CI. It ships **pure domain only** — tunables + sim + tests.
Health/hunger, D-0008 caps, and the player-facing overlay are deferred (§5).

## 1. What ships this slice

- **`games/exploration/survival/difficulty.py`** — the `Difficulty` enum
  (`EASY`/`MEDIUM`/`HARD`), the frozen `SurvivalTunables(max_energy, regen_seconds,
  cost)`, and the `TUNABLES` table. **Easy imports mining's shipped constants directly**
  (`energy.MAX_ENERGY` / `energy.REGEN_SECONDS` / `energy.DIG_COST`) so it can never
  silently drift from the base game.
- **`games/exploration/survival/sim.py`** — the pure sim: `run(*, seeds=range(400),
  difficulties=tuple(Difficulty)) -> SurvivalReport`. It drives the real engine
  (`settle`/`can_dig`/`spend`/`seconds_until`) per difficulty and reads three curves
  back out. `format_report` + `__main__` print the band table.
- **`games/exploration/tests/test_survival_sim.py`** — 7 tests re-pinning the bands.
- **`games/exploration/survival/__init__.py`** — the public surface.

## 2. Pinned tunables

The Energy axis does **not** add a third global energy bar (D-0004). It only scales the
shipped mining bar; Easy *is* that bar, byte-identical.

| Difficulty | max_energy | regen_seconds | cost | source |
|------------|-----------|---------------|------|--------|
| Easy       | 60        | 10            | 1    | **shipped mining constants** (imported, D-0004) |
| Medium     | 50        | 15            | 1    | sim-pinned first-candidate gradient |
| Hard       | 40        | 20            | 1    | sim-pinned first-candidate gradient |

## 3. The three Q-0087 curves (pinned numbers)

Driven by the engine over `seeds=range(400)`; the tests use a smaller seed sweep since
casual reach is seed-independent by construction.

| Difficulty | burst (cap÷cost) | sustained/hr (3600÷regen) | casual/day | grind 8h | capability-gap |
|------------|------------------|---------------------------|-----------|----------|----------------|
| Easy       | 60               | 360                       | 30        | 2940     | 98.0           |
| Medium     | 50               | 240                       | 30        | 1970     | 65.7           |
| Hard       | 40               | 180                       | 30        | 1480     | 49.3           |

- **casual/day** — a well-spaced ~30-action schedule that never energy-blocks (the
  casual player's daily reach). It lands 30 on every difficulty: capability is never
  gated behind energy (Q-0087 casual track).
- **sustained/hr (grinder surplus/hr)** — the regen-limited steady-state throughput,
  **produced by the engine** (an empty-bar greedy digger driven over a simulated hour),
  not hardcoded. It lands on `3600 // regen_seconds` because regen is analytic; the
  tests re-pin the exact number.
- **capability-gap** — an 8-hour grind (opening burst + sustained) ÷ casual/day: how far
  grind out-runs casual. Grind earns prestige, never gates casual.

## 4. Decisions carried

- **D-0004 — "Easy ≡ shipped bars"**: Easy reuses mining's shipped constants rather than
  restating them, and `test_easy_is_byte_identical_to_shipped_bars` re-asserts the
  identity. A change to the shipped bars can never silently drift Easy from the base game.
- **No pay-to-win (Q-0039/Q-0190)**: food restore is a shared, difficulty-*independent*
  refill — one value per item, applied identically whatever difficulty the player
  ascends to. Eating cannot lift Hard's faucet onto Easy's; `test_no_pay_to_win` pins it.
- **Monotone gradient**: harder = a tighter faucet — sustained throughput strictly
  decreases Easy > Medium > Hard.

## 5. Scope fence (deferred — follow-ups)

- **Health / hunger axes** — this slice pins only the *Energy* axis. Health/hunger are
  separate survival axes and land as follow-up slices.
- **D-0008 caps** — the per-difficulty progression/prestige caps are not modelled here;
  the sim measures throughput, not caps.
- **Player-facing overlay** — the difficulty *choice* UX, one-way ascent wiring
  (Q-0078), and host adapters are deferred; this slice is pure domain only.
- **Medium/Hard exact tuning** — the `(50, 15s, 1)` / `(40, 20s, 1)` gradient is the
  **first candidate**, sim-pinned so it is falsifiable in CI. Exact balancing (the
  15s/20s regen values are the first lever to revisit) is consolidation-phase work; the
  sim-pin exists precisely so that tuning reddens CI until the tests are re-pinned.
