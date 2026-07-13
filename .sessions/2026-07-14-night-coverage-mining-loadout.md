# 2026-07-14 · night coverage — pin the set-aware Equip Best picker (tests)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-13T22:48:34Z · night-coverage-mining-loadout

Coverage slice under the ORDER 008(b) production-grade standing directive:
`games/mining/core/loadout.py` — the "Equip Best" picker behind the Gear
panel button — sat at **28% coverage with zero direct tests**, the worst
meaningful number among core engine modules in the 2026-07-13 scope scan
(`pytest --cov`, 556 tests, main `511fa91`). Yet it carries the subtlest
behavior in the gear model: a complete same-tier set (set bonus included)
can beat the naive strongest-piece-per-slot greedy, and the module's whole
reason to exist is choosing correctly between those two candidates.

Shipped `tests/mining/test_loadout.py` — 11 focused tests pinning, at the
EXISTING gear constants (power arithmetic shown in-file): empty/zero-qty/
unequippable inventories; the greedy per-slot pick; the every-pick-lands-
in-its-own-slot invariant; both crossovers (full bronze + iron chestplate →
set wins 42>40; full bronze + diamond sword → greedy wins 44>42); non-set
mining slots preserved alongside a winning set candidate; incomplete tier
(5/6) spawning no set candidate; two complete tiers → diamond; and the
mixed-case pin (a winning set candidate returns constructed lowercase
`"{tier} {family}"` names regardless of inventory casing — current
behavior, documented not changed). Module coverage 28% → **100%** (32/32
stmts); suite 556 → **567 passed**; `python3 bootstrap.py check --strict`
exit 0 with only this card's designed born-red HOLD pre-flip. Tests-only:
zero gameplay-constant changes, no sim-lab surface. No bug found — but one
observation recorded: `best_loadout` has NO production caller yet (neither
`services/mining_workflow.py` nor the CLIs invoke it), so these tests are
the module's only executable spec until the Gear panel button lands.

## 💡 Session idea

CI runs `pytest` but never measures coverage — this slice's target was
found by a hand-run `pytest --cov` scan, and the next under-tested seam
will need the same manual archaeology. Add a coverage ratchet: a small
`tools/` step (or tests.yml line) that runs `pytest --cov` and compares
per-module percentages against a committed baseline file (e.g.
`telemetry/coverage-baseline.json`), failing only on REGRESSION and
letting any improvement auto-tighten the floor. That turns ORDER 008(b)'s
"production-grade" standing target into a machine-held invariant — today's
scan (bootstrap.py 0%, mining loadout 28%→100%, names 37%, taxonomy 63%,
encounters_sim 68%, economy_sim 75%) becomes the first baseline, and every
future test slice moves the ratchet instead of re-discovering the map.
Dedupe check: recent cards seeded the telemetry outcome backfill
(truth-stamp card), the machine-readable truth-stamp anchor, the
ledger-drift check (#89 KIT-ASK), and the cook-leg SIM-REQUEST — none
touches test coverage or CI gating of it; no card idea to date does.

## ⟲ Previous-session review

The previous session is the #94/#95 night wave, re-verified against
`origin/main`: #94 (`06e5b5f`) added exactly the promised night-headline
outbox entry — 31 added lines in `control/outbox.md`, nothing else touched
(inbox/status untouched, as required); #95 (`8106177`) delivered the
truth-stamp groom it claimed — `docs/current-state.md` re-stamped plus
card, claim and telemetry row, docs-only as promised, and its local-state
claim ("pytest -q 556 passed") replays exactly (this session's baseline
scan found 556 at that HEAD). The wave's one structural leftover — its
claim file outliving the merge — was released this session via **#96**
(`ca2184e`, squash `511fa91`), merged by the auto-merge enabler on green,
keeping the claims ledger at zero stale entries. Nothing overstated.
