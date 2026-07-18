# 2026-07-18 · mining-broke-report-once — fix(mining): report a gear break only on the tick it breaks

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus 4.x · high · runtime bugfix

⚑ Self-initiated: small game-improvement slice (owner night order 2026-07-18 —
land ONE contained, tested, independently-landable game-improvement slice as a PR
on green via auto-merge). This is slice 6, a DEEP bug-hunt on the game LOGIC
(slices 1–5 covered the CLIs). Executed at branch base `30d56b8` (#162, main HEAD).

**The bug (real, player-facing).** The mining WORKFLOW audited seam ticks gear
durability through `_apply_wear` (`services/mining_workflow.py`), whose docstring
promises its return value `broke` names "the items that broke (hit 0) **this
tick**". The loop did not honour that: for every worn slot it ran
`state.durability[item] = max(0, state.durability[item] - 1)` and appended the
item to `broke` whenever the value was `0`. An item that broke on an earlier
action stays in the equipped slot AND in the `durability` map at `0` (the seam
does not clear a broken item — that consumption step is a deferred slice), so on
the NEXT wearing action the same already-broken item decrements `max(0, 0-1) = 0`,
still reads `== 0`, and is reported as broken AGAIN. Result: after a tool breaks
once, every subsequent `mine` (and `explore` / `duel`, which share `WEAR_PLAN`)
re-emits it in `broke` — a host rendering `broke` would show "your iron pickaxe
broke!" on every single dig thereafter, not once.

Reproduced before the fix (durability-1 tool, two digs at the surface): dig 1 →
`broke=('iron pickaxe',)`, durability 0; dig 2 → `broke=('iron pickaxe',)` again.

**The fix (surgical, no balance change).** Skip an already-broken slot: if
`state.durability[item] <= 0` the item does not wear again and is not re-reported.
The break-tick behaviour is preserved exactly (a durability-1 item still
decrements to 0 and reports `broke` on the tick it hits 0); only the spurious
re-report on later ticks is removed, so `broke` now means what its docstring says.
No durability constant, wear-plan entry, price, or economy number is touched, and
the audited seam's `target` / `mutation_type` / message strings are untouched.

Scope: one-branch change in `services/mining_workflow.py::_apply_wear` + one
regression test (`test_mine_reports_break_only_on_the_tick_it_breaks` in
`services/tests/test_mining_workflow.py`) that fails on the old code
(`broke == ('iron pickaxe',)` on the second dig) and passes on the new
(`broke == ()`); `services/tests` `EXPECTED_MIN_TESTS.txt` floor 216 → 217 +
`docs/balance.md` regenerated (its Test-suite-floors section pins that count).

## 💡 Session idea

⚑ Self-initiated. The deep hunt read the whole pure-core surface
(`games/mining/core/*`, `games/exploration/*`, `games/fishing/core/*`,
`games/dnd/*`, `games/shared/*`) and the workflow seam. The core is
exceptionally clean (5 prior audit slices); the one clear, non-judgment, no-
balance correctness bug is the one fixed here. The remaining findings are all
BALANCE- or CONTRACT-judgment calls, deferred to owner input as backlog:

1. **exploration ore-scaling still uses the runaway curve the 2026-06-22
   rebalance retired.** `games/mining/core/exploration.py::_scale_amount` scales
   ore gains by `1 + mining_power // 2` (×2 / ×3 / ×4 / ×5 at pickaxe / iron /
   gold / diamond). That is the EXACT formula `rewards.mine_multiplier`'s comment
   calls out as having "run the curve away to ×5 at diamond … letting a geared
   veteran out-earn a fresh player ~8×", which the sim-pinned rebalance flattened
   to `1 + power * 0.0625` (×1.5 at diamond) for the dig faucet. The exploration
   engine's scaling was not migrated. Player impact: whenever exploration is
   wired to a command, a diamond-geared explorer's ore payout runs ~3× steeper
   than the rebalanced dig faucet intends. **Owner-input** (whether exploration
   should share mining's flattened curve is a balance-tuning call, and exploration
   is currently additive foundation, not yet on a live command path).

2. **broken gear stays equipped and fully effective at 0 durability.** This slice
   stops the re-report, but the deeper question stands: a tool/light at durability
   0 is never cleared by the seam, so it keeps contributing its full
   `EffectiveStats` (mine multiplier, depth access, light radius) and remains
   usable indefinitely — the durability sink is toothless until a caller removes
   it. Whether a broken item should be unequipped, consumed from inventory, or
   block the action is a design/product call (the equipment docstring says gear is
   "consumed from inventory" on break, but no layer does it yet). **Owner-input.**

3. **`build_structure` trusts a caller-supplied `level` instead of reading
   state.** `services/mining_workflow.py::build_structure(state, structure, level)`
   prices and writes `state.structures[key] = level + 1` from the `level` ARGUMENT,
   never validating it against `state.structures.get(key, 0)` — unlike
   `vault_upgrade` / `allocate_skill`, which read the current value from `state`.
   A stale or wrong `level` from a caller silently corrupts the stored level
   (downgrade / double-charge). It is a latent robustness gap, but tightening the
   contract could change the established caller interface, so it wants a **contract
   decision** before a fix.

## ⟲ Previous-session review

Target: games PR #162 (`30d56b8`, "test(mining): pin CLI negative/non-integer-qty
honest rejection") — this branch's base and main's current HEAD (`git fetch
origin main && git reset --hard origin/main` → `30d56b8`, confirmed; the merge
commit is titled `…(#162)`). Its load-bearing claim — the standalone mining CLI's
qty-taking verbs (`sell` / `build` / `skill`) had two unpinned bad-quantity edges
through the shared `_split_item_qty` boundary (a negative token that `lstrip("-")`
lets pass the isdigit test and forwards to the seam's deeper `qty<=0` /
`points<=0` / `build_cost(level<0)==None` guards, and a non-integer token that
fails isdigit and folds into the multi-word name to be rejected as unknown), with
NO bug found — every path an honest no-op with no state change and no audit row —
re-checks TRUE from this session's own reading: `tests/mining/test_cli.py` carries
the six pins, `tests/mining` floor reads 202, and `docs/balance.md`'s
Test-suite-floors section carries the matching `tests/mining | 202` row. The
mining seam/economy were left untouched by #162, so this slice's edit to
`_apply_wear` is on virgin ground relative to it (that PR added only CLI tests).
Green baseline this HEAD: `848 passed, 1 xfailed` (re-run this session before any
edit).

## ✅ Landed

_(pending — filled on the final commit once the PR is green)_
