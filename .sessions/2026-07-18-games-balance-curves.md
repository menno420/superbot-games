# 2026-07-18 · games-balance-curves — flatten exploration ore-scaling + make the fishing V043 curve canonical for fish valuation

> **Status:** `complete`
>
> 📊 Model: opus-4.8 · high · feature build

⚑ Owner-authorized code slice (menno420, live 2026-07-18): resolve two queued
owner-input **balance** decisions from `docs/NEXT-TASKS.md` (§ "Owner-input
decisions queued (2026-07-18 overnight loop)") as one flagged, reversible PR.
Both findings are **latent / not player-reachable today** (exploration is
unwired; no seam routes a caught fish into `MiningState.inventory`), so risk is
low — the stated owner-defaults are applied and flagged for owner review, the
exact ×-factors remaining a balance call the owner can override.

**Decision #1 [balance] — exploration ore-scaling still on the retired runaway
curve.** `games/mining/core/exploration.py::_scale_amount` scaled ore gains by
the pre-2026-06-22 steep curve `1 + mining_power // 2` (×5 at diamond power 8) —
the exact formula the sim-pinned 2026-06-22 rebalance flattened to
`1 + power * TOOL_POWER_GAIN` (`TOOL_POWER_GAIN = 0.0625` → ×1.5 at diamond) in
`rewards.mine_multiplier` for the live dig faucet, never propagated to the
still-unwired exploration engine. Owner-default applied: **propagate the
flattened curve**, reusing `rewards.TOOL_POWER_GAIN` and the same
`max(1, round(base * mult))` rounding the faucet uses in `roll_mine_loot` (one
source of truth for the constant + rounding).

**Decision #7 [balance] — cross-game fish valuation gap.**
`games/mining/core/items.py::register_fish_species` folded each fish into the
mining market worth `max(1, size_rank)` (1–4 coins), while the fishing V043
curve (`games/fishing/core/economy.py`) sells the same species at 8 / 13 / 27 /
80 — a ~20× gap. Owner-default applied: **make the fishing V043 curve
canonical** — a registered fish is now valued by its fishing-economy V043 price,
reusing the fishing curve as the single source of truth. A **lazy** import at
call time (register_fish_species runs only at host-wiring, when fishing is
present) preserves the mining core's import-time fishing severance; a species
not on the V043 curve keeps the `max(1, size_rank)` fallback (so the existing
`_FakeFish` injection test stays honest).

## 💡 Session idea

A sim-pinned rebalance is only as complete as its propagation: flattening the
LIVE faucet constant without chasing every other place that re-derived the OLD
curve leaves a latent balance fork that only surfaces the day a second code path
goes live. The durable move is to make the rebalance's constant a single
imported source of truth (here `rewards.TOOL_POWER_GAIN`) rather than a number
copied into each faucet — and, symmetrically, to make a cross-game price a
single reused function rather than two ad-hoc formulas that agree only by
accident. Both fixes here trade a duplicated literal for a reused source.

## ⟲ Previous-session review

Target: games PR #173 (`729694c`, "fix(mining): consume gear on break
(durability 0)") — this branch's base and main's current HEAD (`git fetch origin
main && git reset --hard origin/main` → `729694c`, confirmed). #173 resolved
queued decision #2 (consume-on-break) in `services/mining_workflow.py::
_apply_wear`; a runtime seam change, its regression tests live in
`services/tests/test_mining_workflow.py`. Green baseline re-run this session
before any edit — recorded in the Landed section below. Verified on current main
that BOTH premises this session targets are still live (a sibling decision, #3,
had turned out already-fixed): `_scale_amount` still reads `1 + mining_power //
2`, and `register_fish_species` still values via `_fish_value = max(1,
size_rank)`.

## ✅ Landed (PR #174)

Shipped in PR [#174](https://github.com/menno420/superbot-games/pull/174)
(`claude/games-balance-curves`). Two balance changes + tests + bookkeeping + this
card. Base = `729694c` (#173, main HEAD at branch cut).

- `games/mining/core/exploration.py::_scale_amount` — ore gains now scale on the
  flattened faucet curve `1 + power * rewards.TOOL_POWER_GAIN` (importing the
  constant from `rewards`, one source of truth) with the faucet's
  `max(1, round(base * mult))` rounding, retiring the `1 + mining_power // 2`
  ×5 runaway. Diamond power 8 → ×1.5. Penalties still never amplified;
  `loot_bonus` still flat-added.
- `games/mining/core/items.py::register_fish_species` / `_fish_value` — a
  registered fish is valued by its fishing V043 price via a **lazy**
  `from games.fishing.core.economy import is_sellable, sell_value` (import-time
  fishing severance preserved); off-curve/no-`species_id` rows keep the
  `max(1, size_rank)` fallback. `FishLike` gains an optional `species_id`.
- Tests: `tests/mining/test_exploration_world.py::
  test_scale_amount_uses_flattened_faucet_curve` (diamond ×1.5-equivalent, not
  ×5, and parity with `rewards.mine_multiplier`);
  `tests/mining/test_items_market.py::
  test_register_fish_species_values_on_fishing_v043_curve` (registered fish =
  V043 price; legend_carp 80 not 4) + `…_off_curve_falls_back_to_size_rank`. The
  pre-existing `…_injection_point` test (no `species_id`) still pins the
  size-rank fallback.
- Bookkeeping: `tests/mining/EXPECTED_MIN_TESTS.txt` 204 → 207; `docs/balance.md`
  regenerated (`python3 tools/gen_balance.py --write`, `--check` exit 0);
  `docs/NEXT-TASKS.md` items #1 and #7 marked RESOLVED with applied default +
  PR.

**Suite green:** `python3 -m pytest -q` = `860 passed, 1 xfailed` (base was `857
passed, 1 xfailed`; the three new mining tests — one exploration + two
items-market — lift it to 860, no tests removed).
`python3 tests/check_suite_floors.py` passes.
`bootstrap.py check --strict` pre-flip = exit 0 with the designed born-red HOLD
on this card's in-progress Status; this flip-to-complete commit clears the hold
so the live auto-merge apparatus lands the squash on green. No live faucet
number changed (`TOOL_POWER_GAIN` unchanged); both changes are latent today and
flagged for owner review.
