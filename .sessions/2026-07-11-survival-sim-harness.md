# 2026-07-11 · Survival sim harness (games/exploration/survival/)

> **Status:** `complete`
>
> 📊 Model: Claude Opus · 2026-07-11T01:05:51Z · exploration P2 survival sim harness (re-land after shared-checkout race)

## Goal

Land the **survival-difficulty sim harness** (exploration P2, `docs/founding-plan-exploration.md` §3):
a pure, deterministic sim that drives the *shipped* mining energy engine
(`games.mining.core.energy`) through per-difficulty tunables and pins the Q-0087
dual-track throughput curves (casual reach / grinder surplus / capability-gap) as
tests, so a survival-difficulty tuning is *proven against the bar before it ships*.

- **Easy ≡ shipped bars, byte-identical** (D-0004): the Energy axis does NOT add a
  third global energy bar — it only scales the shipped bars for Medium/Hard, driven
  through the same engine the base game already runs. Easy imports mining's shipped
  constants directly so it can never silently drift.
- Medium/Hard are the first-candidate gradient (sim-pinned; exact tuning is
  consolidation-phase work): Medium `(50, 15s, 1)`, Hard `(40, 20s, 1)`.
- **No pay-to-win** (Q-0039/Q-0190): food is a shared, difficulty-independent refill —
  it cannot lift Hard's faucet onto Easy's.

## What shipped

- **`games/exploration/survival/` pure package** (stdlib-only, no Discord/DB/IO):
  - **`difficulty.py`** — `Difficulty` enum (EASY/MEDIUM/HARD), frozen
    `SurvivalTunables(max_energy, regen_seconds, cost)`, and `TUNABLES`. Easy imports
    mining's shipped constants directly (`energy.MAX_ENERGY/REGEN_SECONDS/DIG_COST`) →
    provably byte-identical to the base game (D-0004); Medium `(50, 15s, 1)` / Hard
    `(40, 20s, 1)` are the sim-pinned first-candidate gradient.
  - **`sim.py`** — pure `run(*, seeds=range(400), difficulties=…) -> SurvivalReport`
    driving the **real shipped mining energy engine** (`settle`/`can_dig`/`spend`/
    `seconds_until`) per difficulty and reading three Q-0087 curves back out. The
    sustained/hr number is *produced by the engine* (an empty-bar greedy digger driven
    over a simulated hour), not hardcoded. `format_report` + `__main__`.
  - **`__init__.py`** — the public surface.
- **`games/exploration/tests/test_survival_sim.py`** — 7 tests: Easy byte-identical to
  shipped bars; sustained 360/240/180; burst 60/50/40; monotone gradient; casual == 30
  across difficulties; `run()`-twice determinism; no-pay-to-win (food is a shared
  difficulty-independent refill).
- **CI floor** `204 → 211` (73 mining + 26 fishing + 55 exploration + 57 shared/inventory)
  in `.github/workflows/tests.yml`. Full suite **211 passed** locally.
- **`docs/design/survival-sim-harness.md`** (`reference`) — purpose, pinned tunables +
  curve tables (real sim output), D-0004, and the scope fence (health/hunger, D-0008
  caps, overlay = follow-ups). Linked from `docs/current-state.md`.

## Sim-pin headline

Driving the shipped energy engine per difficulty: **casual reach is 30/day on every
difficulty** (a well-spaced day never energy-blocks — capability is never gated behind
energy, Q-0087). The *grinder* faucet tightens with difficulty — sustained 360 → 240 →
180 digs/hr (= 3600 ÷ regen), burst 60 → 50 → 40, capability-gap 98.0 → 65.7 → 49.3 —
so difficulty is a *grind* gradient, never a wall on casual play, and food cannot buy
Hard past Easy's faucet (no pay-to-win). Easy is byte-identical to the shipped bars.

## 💡 Session idea

The survival sim is a *third* independent witness (after mining's and fishing's
`sim/` harnesses) that every game lane wants the same shape: a pure seeded sweep that
drives the real engine and pins its aggregates as fast tests. All three now re-roll
the same "drive-the-shipped-engine, read the curve back out, re-pin the number"
discipline — a strong signal for a shared `games/shared/sim_pin` helper (or at least a
documented pattern) so the fourth lane inherits it instead of hand-rolling it again.
The survival harness deliberately keeps Medium/Hard sim-pinned (not owner-tuned) so the
gradient is *falsifiable in CI* the moment consolidation-phase balancing touches it.

## ⟲ Previous-session review

This slice is a **re-land after a shared-checkout race**: an earlier build of this exact
harness went green (7 tests, full suite green, sim printing the pinned bands) but its
worktree was clobbered by another session sharing the checkout before it could push —
the verified work survived only as a dangling commit (`fd091af`) in the shared object
store. This session recovers the survival-owned paths from that commit *by SHA* (not by
pulling the foreign `status.md`/`current-state.md` amend that rode along), re-applies the
CI count-floor bump fresh against *this* main, and re-verifies green locally before push.
The lesson the fishing skeleton (#25) already flagged — a born-red card that flips to
`complete` only when the code lands — is honoured verbatim here, and reinforced: isolate
in a dedicated worktree so no sibling session can reset the checkout mid-flight.
