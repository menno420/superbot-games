# 2026-07-11 · Survival sim harness (games/exploration/survival/)

> **Status:** `in-progress`
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

_(filled on flip to complete)_

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
