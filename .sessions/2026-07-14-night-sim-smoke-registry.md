# 2026-07-14 · night test — sim-harness smoke registry: every sim's render path executes in CI

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T02:18:33Z · night-sim-smoke-registry

Test slice implementing the sim-harness smoke registry idea from
`.sessions/2026-07-14-night-coverage-encounters-sim.md` (verified
unimplemented at main `5fde718` — no `test_sim_harnesses.py` existed).
The gap it closes is exactly how #106's `format_report(SimReport())`
`ZeroDivisionError` stayed latent: every balance harness's `__main__`
entry is `pragma: no cover` and its full-scale run is manual, so
nothing executed the render paths end-to-end in CI.

Shipped `tests/shared/sim/test_sim_harnesses.py`: a parametrized
registry of (sim module, tiny sweep kwargs) covering all five shipped
sims — `games/mining/sim/encounters_sim` (seeds=2, coord=±3, two
depths), `games/shared/sim/economy_sim` (seeds=2, 5 digs/casts per
seed), `games/fishing/sim/catch_sim` (seeds=2, 2 casts/spot),
`games/dnd/sim/menu_sim` (seeds=2), and the exploration survival sim,
whose exact module path was confirmed first:
`games/exploration/survival/sim.py`, NOT a `*_sim.py` name (seeds=2).
Each entry asserts `format_report(run(**tiny_kw))` returns non-empty
text without raising (each measured <0.05s at these bounds); a
companion pin asserts every registry line resolves to a real module
file, so a renamed/moved sim reddens its own entry. Completeness is
glob-enforced: every `*_sim.py` under `games/` (test files and
`__pycache__` excluded) must appear in the registry, so a new sim
cannot dodge the smoke — the survival sim is enumerated explicitly as
the documented union of both signals. Placement honesty: the spec named
`tests/shared/test_sim_harnesses.py`, but the ORDER-001 floor guard
discovers any dir directly containing `test_*.py` as a suite, so a file
at `tests/shared/` root would have forced a brand-new overlapping suite
registration that recursively double-counts `tests/shared/inventory` +
`tests/shared/sim`; the registered shared-sim suite is the semantic
home the originating card's "e.g." pointed at. 11 new tests;
`tests/shared/sim` floor 7 → **29** (pinned to collected, matching
every other suite's convention — the 7 had lagged since #54);
`docs/balance.md` regenerated and `gen_balance.py --check` green
(gen-balance gate). Full suite 684 → **695 passed** locally on this
branch; strict check exit 0. Claim
`control/claims/night-sim-smoke-registry.md` self-released in this flip
commit (established precedent).

## 💡 Session idea

The smoke registry proves every renderer runs at healthy tiny bounds —
but #106's actual bug class was a DEGENERATE bound (zero actions →
divide by zero), and only the mining sim has that case pinned. Add a
**degenerate-bounds matrix** to the registry file: parametrize the same
five sims over empty sweeps (`seeds=range(0)`, zero
`digs_per_seed`/`casts_per_spot`, empty `depths`/`difficulties`) and
assert each either renders a clean report or raises a documented,
named guard — pinning every zero-denominator/empty-bucket branch
registry-wide instead of sim-by-sim as bugs are found. Dedupe check
against the used-idea list: the sim-harness smoke registry (this slice)
executes healthy bounds; the adversarial-payload corpus targets
user-facing input parsing, not sweep bounds; the CI coverage ratchet
and detector-trip registry are unrelated mechanisms. No card idea to
date sweeps the sims' degenerate bounds as a matrix.

## ⟲ Previous-session review

The previous slice is this run's #118
(`claude/night-readme-four-games`, born-red `5d4449e`, README edit
`1a3a993`, flip `5e9b4ea`, squash-merged to main as `5fde718` at
2026-07-14T02:12:13Z by github-actions[bot]). Verified against live CI:
at the flip SHA all three workflows completed green (tests run
29300461994, substrate-gate run 29300461974, auto-merge-enabler run
29300461967), and the born-red SHA's substrate-gate failure (run
29300377547) was exactly the designed pre-flip HOLD. Verified against
this branch's base (which includes `5fde718`): README's "Playing the
games" section now opens "All four of the world games", carries the
post-#117 four-game hub transcript, fishing's `sell <species> [qty]`,
both new standalones, and all four workflow seams — every claim in its
card checks out against the committed text. One honest nit: #118's card
says "lines 29–59" for the stale section; the refreshed section now
spans further (the diff was +23/−5), which is expected growth, not
drift.
