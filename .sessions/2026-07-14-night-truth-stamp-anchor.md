# 2026-07-14 · night docs — machine-readable truth-stamp anchor + stamp scaffold tool + groom

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T02:27:27Z · night-truth-stamp-anchor

Docs slice, three parts, from #90's card idea and
`.sessions/2026-07-14-night-truth-stamp-night-wave.md`'s card idea —
both verified unimplemented at main `fdea103` before building (no
`truth-stamped-at` marker anywhere under docs/ or tools/, no
`tools/stamp_scaffold.py`).

Shipped: **(a)** `docs/current-state.md`'s prose stamp now carries a
machine-readable `<!-- truth-stamped-at:
fdea103255096962210b8243d5a437ccc724830d -->` HTML comment beside it.
**(b)** `tools/stamp_scaffold.py`: parses that anchor
(`ANCHOR_RE`, 7–40 hex), runs `git log <anchor>..HEAD --first-parent`
(UTC dates), and emits the `- **#N** (YYYY-MM-DD, \`sha\`) — subject`
bullet skeletons the "Recently shipped" groom hand-transcribes today —
squash subjects' trailing `(#N)` is promoted to the citation, a commit
without one gets a loud `**#?**` placeholder; an authoring aid,
deliberately NOT a CI gate. 8 unit tests in the NEW registered
`tests/tools` suite (anchor grammar, bullet formatting, missing-anchor
ValueError, empty-range behavior — kept shallow-checkout safe — and a
pin that the real ledger carries a parseable anchor). Verified
end-to-end: run against the PREVIOUS anchor (`24f6e04`), the tool's
twelve emitted bullets match this groom's hand-written #108–#119
citations exactly (same PR#s, dates, short SHAs). **(c)** the owed
groom: "Recently shipped" records #108–#119, each verified against the
local `origin/main` log before writing (#108 `bcaed58` outbox review
verdict on #102 · #109 `b4c306f` truth-stamp · #110 `a51c5d5` catch_sim
· #111 `0efb7ac` hub loop · #112 `6de5666` mining items · #113
`73111d0` mining/cli · #114 `bdc3445` dnd cli+menu · #115 `d4654f8`
resolver clamp fix · #116 `673cb95` dock grammar fix · #117 `d47e28b`
hub banner order fix · #118 `5fde718` README four games · #119
`fdea103` sim smoke registry); "In flight" re-stamped at `fdea103`
("PRs through" #107 → #119) with suite **695 passed** and measured
total coverage **97%** across `games/` + `services/` (5476 stmts, 163
missed, `--cov` run this session). Suite-delta honesty: #111–#114's
cards cite overlapping local baselines (parallel sessions), so the
groom records the wave's aggregate 606 → 684 rather than fabricating a
per-PR chain. New suite ⇒ `tests/EXPECTED_SUITES.txt` + floor 8;
`docs/balance.md` regenerated, `gen_balance.py --check` green
(gen-balance gate). Full suite 695 → **703 passed** locally; strict
exit 0. Claim `control/claims/night-truth-stamp-anchor.md`
self-released in this flip commit (established precedent).

## 💡 Session idea

Building the `tests/tools` suite exposed that `tools/gen_balance.py` —
the generator whose output IS CI-gated (`gen_balance.py --check` and
the committed `docs/balance.md`) — has zero direct tests: a formatting
or import bug there mis-generates the balance page everywhere and the
gate would happily pin the wrong output. Add **gen_balance generator
pins** to the now-existing `tests/tools` suite: unit-test its section
builders against the live economy modules (the V043 table's values must
equal `games/fishing/core/economy.py`'s constants, the floors table
must equal the `EXPECTED_MIN_TESTS.txt` files it reads) and pin that
`--check` is a pure no-write comparison. Dedupe check against the
used-idea list: the CI coverage ratchet, committed coverage ledger,
display-table completeness registry, and sim-harness smoke registry all
gate OTHER artifacts; the truth-stamp scaffold generator is the
authoring aid this slice shipped; none tests the balance GENERATOR
itself. No card idea to date does.

## ⟲ Previous-session review

The previous slice is this run's #119
(`claude/night-sim-smoke-registry`, born-red `76d3b65`, registry
`59f3e37`, flip `78ad5d2`, squash-merged to main as `fdea103` at
2026-07-14T02:20:07Z by github-actions[bot]). Verified against live CI:
at the flip SHA all three workflows completed green (tests run
29300791212, substrate-gate run 29300791130, auto-merge-enabler run
29300791129), and the born-red SHA's substrate-gate failure (run
29300660542; its tests run 29300660555 was green) was exactly the
designed pre-flip HOLD. Verified on this branch (whose base includes
`fdea103`): the registry's 11 tests execute in this session's local
runs, the floor table shows `tests/shared/sim` 29/29, and the
completeness check enumerates all five sims including the non-glob
`games/exploration/survival/sim.py`. One honest note carried forward:
#119's file placement deviates from its slice spec
(`tests/shared/sim/…` instead of `tests/shared/…`) — the deviation is
documented in its card and PR body with the floor-guard overlap
rationale, and this session independently confirms the rationale: the
guard discovers any dir directly containing `test_*.py`, which is
precisely why THIS slice's new suite had to be registered in
`tests/EXPECTED_SUITES.txt`.
