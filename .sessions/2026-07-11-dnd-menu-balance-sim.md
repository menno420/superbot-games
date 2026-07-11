# 2026-07-11 · D&D menu-balance sim (bounded economy, no pay-to-win)

> **Status:** `born-red`
>
> 📊 Model: Opus 4.8 · 2026-07-11T15:08:22Z · D&D menu-balance sim (bounded economy, no pay-to-win)

## Goal

Land the **D&D menu-balance sim** — the next slice after the merged D&D walking
skeleton. A pure, deterministic sim that enumerates EVERY scene in the shipped data
catalog and EVERY option in each menu, resolves each option's PRE-DEFINED effect
through the *shipped* resolver (seeded), and pins the **bounded-menu economy**
(Q-0040 / D-0007) as tests: every option's reward is code-owned and
`<= catalog.GLOBAL_MAX` component-wise (no pay-to-win), and the narrate-only no-op
options mint nothing.

The skeleton already asserted this by *design* (the resolver clamps, effects are
pre-priced). This slice makes it **sim-pinned**: a deterministic harness measures
the reward every menu path yields and re-pins the bounds as fast tests, so a balance
regression that lets any option out-earn the ceiling reddens CI.

## What shipped

- **`games/dnd/sim/` pure package** (stdlib-only, no LLM/Discord/DB/IO):
  - **`menu_sim.py`** — pure `run(*, seeds=range(256), scenes=SCENES) -> MenuBalanceReport`.
    Enumerates every scene × option, drives the **real shipped resolver**
    (`games.dnd.core.resolver.resolve`, full-menu XP so every option is a genuine
    surfaced choice) and reads back each option's code-owned reward. Aggregates a
    frozen `MenuBalanceReport`: per-scene max reward, global max reward, option count,
    no-op count, and the headline `all_within_global_max` flag. `format_report` +
    `__main__`. The sim only READS/EXERCISES the shipped resolver/effects/scene data —
    it never changes an outcome.
  - **`__init__.py`** — the public surface + the sim-lane rationale.
- **`tests/dnd/test_menu_sim.py`** — 4 tests: every option's reward `<= GLOBAL_MAX`
  (the no-pay-to-win pin); the no-op options yield no reward; `run()`-twice
  determinism; the exact per-scene + global max reward bounds pinned as constants.
- **CI floor** `tests/dnd` 15 → 19 in `tests/dnd/EXPECTED_MIN_TESTS.txt`. Full suite
  **291 passed** locally; `check_suite_floors.py` exit 0; `bootstrap.py check
  --strict` exit 0.

## Sim-pin headline

Driving the shipped resolver over every scene × option: the one shipped scene
`waystation_road` surfaces 3 options — 1 rewarded, 2 narrate-only no-ops. The rewarded
`advance_escort` option mints exactly `catalog.TIER_CAPS[I]` =
**global_xp=5 game_xp=25 currency=10** (per-scene max = global max), well under the
`GLOBAL_MAX` ceiling (20 / 120 / 50). The two no-op options (`scout_ahead`,
`make_camp`) mint nothing. `all_within_global_max = True` — the no-pay-to-win property
is now test-enforced, not just asserted by design.

## 💡 Session idea

This is a *fourth* independent witness (after mining, fishing, and survival `sim/`
harnesses) that every game lane wants the same shape: a pure seeded sweep that drives
the real engine and re-pins its aggregates as fast tests. The D&D lane pins a
*different axis* than the throughput lanes — not a curve but a **ceiling**: every
bounded-menu path is proven `<= GLOBAL_MAX`. That reinforces the earlier signal for a
shared `games/shared/sim_pin` helper: the four lanes now re-roll the same
"drive-the-shipped-code, read the aggregate back out, re-pin the number" discipline by
hand. The menu-balance sim also grows naturally with the catalog — each new scene/effect
lands with its per-scene reward pin, so the economy can never expand untracked.

## ⟲ Previous-session review

This slice builds directly on the merged D&D walking skeleton (the bounded-menu
resolver + its data catalog). The lesson the fishing and survival skeletons already
flagged — **a born-red card that flips to `complete` only when the code lands** — is
honoured verbatim here: the card is committed `born-red` first, then the sim + tests,
then flipped to `complete` only once the suite is green and the sim prints its pinned
bounds. Isolated in a dedicated worktree so no sibling session can reset the checkout
mid-flight, and the sim only READS the shipped resolver/effects/scene logic — it
changes no outcome the skeleton already pinned.
