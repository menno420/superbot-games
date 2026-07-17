# 2026-07-17 · energy-unreachable — fix: `energy.seconds_until` signals an unreachable target instead of reading it as "already reached"

> **Status:** `complete`
>
> 📊 Model: Claude Opus 4.x · high · runtime bugfix

⚑ Self-initiated: small game-improvement slice (owner order 2026-07-17 —
improve the game via contained, tested, independently-landable slices).
Executed at branch base `0a00733` (#158).

`games/mining/core/energy.seconds_until(state, now, target)` answers "how many
seconds of passive regen until the bar reaches *target*". Passive regen caps at
`max_energy` (the settle cap), so any `target` ABOVE `max_energy` can **never**
be reached by waiting. The old body clamped with
`needed = min(max_energy, target) - s.current`, which lied two ways:

- On a **full bar** (`current == max_energy`) an out-of-range target made
  `needed == 0`, so the function returned **`0`** — i.e. "already reached" —
  for a target the player can never hit by regen. A caller reading `0` as
  "the target is satisfied right now" is misled into treating an impossible
  goal as met.
- From a **partial bar** the same clamp silently returned the finite wait to
  the CAP, masking that the requested target sat above the cap entirely.

Fix (surgical, one file): guard the boundary first — `if target > max_energy:
return math.inf`. `math.inf` is the honest "never" and, being a float, is
arithmetic-safe for the one real caller (see below); the return type widens
`int → int | float`. Below the cap the body is unchanged except dropping the
now-redundant `min(max_energy, target)` clamp (target is guaranteed `≤
max_energy` there), so every already-reachable answer is byte-identical — no
player-facing balance / economy / message change.

Caller audit: the only non-test caller is
`games/exploration/survival/sim.py:88` (`_greedy_digs`), which passes
`target = t.cost` (the dig cost, always small and `≤ max_energy`) and does
`now += wait` then `if now > horizon: break`. It never reaches the unreachable
branch; and even if it did, `now += math.inf` → `inf > horizon` → clean loop
exit (whereas `None` would crash the `+=`). That is exactly why the sentinel is
`math.inf`, not `None`.

Scope: `games/mining/core/energy.py` (the fix) +
`tests/mining/test_energy_capacity.py` (3 regression tests pinning
already-reached → `0`, reachable target → correct seconds incl. sub-interval
remainder + caller-supplied `max_energy`, and unreachable `target > max_energy`
→ `math.inf`) + `tests/mining/EXPECTED_MIN_TESTS.txt` floor 193 → 196 +
`docs/balance.md` regenerated to match. Suite 832 → 835. No other surface
touched.

## 💡 Session idea

This was a **cap-boundary sentinel gap**: a function whose domain is bounded by
a cap (`max_energy`) returned an in-band value (`0`) for an out-of-band request,
so "impossible" and "already done" collapsed to the same answer. Mining's core
has a family of cap-bounded formulas — `capacity.vault_capacity` (clamps to the
ladder ceiling), `capacity.vault_upgrade_cost` (returns `None` at max level),
`settle`/`restore` (cap at `max_energy`) — and they disagree on how they signal
"past the ceiling": one clamps silently, one returns `None`, one (now) returns
`inf`. A cheap guard: a shared parametric test that feeds every cap-bounded core
formula an argument PAST its ceiling and asserts it returns a distinguishable
out-of-band sentinel (not an in-band value that aliases a legitimate answer) —
the same "one registry, per-row red" shape the display-table (#123) and
help-parity (#125) sweeps already use, applied to the cap-boundary contract so
the next cap-bounded formula can't silently alias "impossible" onto a real
value.

## ⟲ Previous-session review

Target: games PR #158 (`0a00733`, "fix(mining-cli): case-insensitive
item/branch/structure tokens") — the merge at this branch's base. Its
load-bearing claim (the standalone mining CLI now lower-cases the item / branch
/ structure token at its boundary, mirroring the fishing CLI's
`args[0].lower()` convention) re-checks TRUE from this session's own reading of
the shipped source, not its word: `games/mining/cli.py` lower-cases in
`_split_item_qty` (`" ".join(args[:-1]).lower()` / `" ".join(args).lower()`,
lines 177–178 — feeding `sell`/`build`/`skill`) and in `_do_buy` / `_do_repair`
(`" ".join(args).lower()`, lines 212/219), and the module comment at line 172
explicitly names the fishing-CLI convention it now matches (`games/fishing/cli.py`
still normalises with `args[0].lower()` at line 295). Its 5 regression tests are
present and named in `tests/mining/test_cli.py`
(`test_sell_is_case_insensitive_for_the_item_name`,
`test_sell_default_quantity_is_case_insensitive`,
`test_buy_is_case_insensitive_and_stores_the_canonical_key`, plus the `skill`
and `repair` case pins), and the mining floor it bumped (188 → 193, with
`docs/balance.md` regenerated in the same commit) is the exact baseline this
slice extends (193 → 196). The audited market/skills seam it left untouched is
still case-insensitive at the lookup layer, so its "no balance / audit / economy
change" claim holds. Verified against the shipped tree, green baseline 832
passed at this HEAD.
