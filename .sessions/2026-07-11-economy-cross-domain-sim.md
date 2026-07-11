# 2026-07-11 · Cross-domain economy sim (whole-economy invariants)

> **Status:** `✅ complete`
>
> 📊 Model: Opus 4.8 · 2026-07-11T17:58:03Z · cross-domain economy sim

## Goal

Land the **cross-domain economy sim** — one level up from the per-domain balance
sims. A pure, deterministic harness that enumerates EVERY reward source across
mining, exploration, fishing, and dnd by IMPORTING AND DRIVING THE SHIPPED
resolvers/catalogs (never reimplementing them), computes each domain's per-hour
emission, and asserts the whole-economy invariants no single-game sim can see. No
balance change: derive the current emission by running, pin it with tolerance
bands.

## What shipped

- **`games/shared/sim/` pure package** (stdlib-only, no LLM/Discord/DB/IO):
  - **`economy_sim.py`** — `run(*, seeds=range(24), digs_per_seed, casts_per_seed)
    -> EconomyReport`. Samples the shipped `rewards.roll_mine_loot` and
    `catch.resolve_cast` (process-independent injected RNG) for the energy-throttled
    item faucets, and reads the dnd `escort_step` bundle + exploration
    `catalog.TIER_CAPS` / `GLOBAL_MAX` for the host-gated currency/xp faucets. A
    frozen `DomainEmission` per domain + a frozen `EconomyReport` with the three
    named-invariant flags. `format_report` + `__main__`. Helper predicates
    `all_bundles_within_global_cap` / `item_faucets_mint_no_currency_or_xp` /
    `noop_paths_mint_nothing`.
  - **`__init__.py`** — the shared-sim lane rationale.
- **`tests/shared/sim/test_economy_sim.py`** — 7 fast tests: the three invariants,
  both pinned emission bands, in-process determinism, and a subprocess determinism
  check under randomized `PYTHONHASHSEED`.
- **Suite registration** — `tests/shared/sim` added to `tests/EXPECTED_SUITES.txt`;
  new floor `tests/shared/sim/EXPECTED_MIN_TESTS.txt = 7`.
- **Design doc** `docs/design/economy-sim.md` (the emission model + pinned table),
  linked from `docs/design/shared-index.md`.
- Full suite **298 passed** locally; `check_suite_floors.py` exit 0;
  `bootstrap.py check --strict` exit 0. NO resolver constant changed.

## Sim-pin headline

Driving the shipped resolvers over the whole economy:

- **Item faucets mint items only** — mining ≈ **540 items/hr** (mean 1.50 ore/dig ×
  360 digs/hr), fishing ≈ **99 items/hr** (bite ≈ 0.55 × 180 casts/hr); both have
  native currency/gxp/game_xp = **0.0 exactly**. Mining coins are a downstream
  ore→sell conversion (≈ 1,640 coins/hr informational), NOT a mint.
- **Currency/xp faucets are host-gated per-completion** — dnd `escort_step` mints
  tier-I **(5, 25, 10)**; exploration tier-III **(20, 120, 50)** == `GLOBAL_MAX`.
- **Invariants all PASS** — `GRANT_WITHIN_GLOBAL_CAP` (every quest tier + the dnd
  bundle ≤ `GLOBAL_MAX` 20/120/50), `ITEM_FAUCET_MINTS_NO_CURRENCY`,
  `NOOP_MINTS_NOTHING`. Pinned bands: mining (480, 600), fishing (85, 115).

## 💡 Session idea

This is the *fifth* independent witness (after mining, fishing, survival, and dnd
`sim/` harnesses) that every lane wants the same shape — but the first that runs it
ACROSS lanes: drive the shipped code of four games at once, read the aggregate back
out, re-pin it. It reinforces the earlier signal for a shared `games/shared/sim_pin`
helper — the sweep-and-pin boilerplate (per-seed injected RNG, a frozen `*Report`,
module-level bands, the subprocess-determinism test) is now hand-rolled six times.
The natural next slice is to factor that discipline into one shared helper so a new
faucet lands with a one-line pin, and the cross-domain sim grows automatically as
each game adds a reward source.

## ⟲ Previous-session review

Builds directly on the merged per-domain sims (mining encounters, fishing catch,
dnd menu-balance, exploration survival) — it drives their shipped resolvers rather
than duplicating any math, and honours the recon's ground-truth reward model
(item faucets mint no currency/xp; the one `GLOBAL_MAX` binds only the quest/dnd
bundles). The lesson those cards flagged — a card that only flips to `complete`
when the code is green — is honoured: worktree-isolated so no sibling session
resets the checkout mid-flight, and the sim only READS the shipped code, changing
no number any earlier sim already pinned.

## Guard recipe

Behaviour-preservation anchor: the sim is read-only — it edits NO resolver
constant, so every existing per-domain suite stays green unchanged. The
cross-domain bounds live in `games/shared/sim/economy_sim.py` module-level bands
(`_MINING_ORE_PER_HOUR`, `_FISHING_FISH_PER_HOUR`) + `tests/shared/sim/` and are
documented in `docs/design/economy-sim.md`. Regenerate with
`python3 -m games.shared.sim.economy_sim` and re-pin the bands there (only) if a
mining/fishing faucet constant changes intentionally — never edit a resolver to
move a band.
