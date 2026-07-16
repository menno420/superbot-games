# 2026-07-16 · shared RNG seam — extract mining's splitmix64 into games/shared/rng.py, migrate the two mining call sites (pure refactor)

> **Status:** ✅ `complete`
>
> 📊 Model: Claude Opus 4.x · high · refactor/test

Building the captured backlog idea
`docs/ideas/shared-deterministic-rng-seam-2026-07-10.md` (`captured` →
quick-win lane): mining hand-rolls the same integer splitmix64-style
`(seed, coords…)` derivation in two places — `games/mining/core/grid.py`
(`_cell_seed`, feature-selection stream) and
`games/mining/core/encounters.py` (a byte-identical private `_cell_seed`
copy plus `encounter_seed`, which xors a domain salt and mixes once
more). Fishing already re-rolled a third clean copy
(`games/fishing/core/rng.py`) that names itself a promotion candidate.

Scope this slice (deliberately narrow — the coordinator's slice + the
claim's scope line): create `games/shared/rng.py` with the mixing step
and the `(seed, coords…)` derivation extracted **verbatim** from mining's
current implementation, then migrate mining's two call sites to consume
it with **zero behavioural change**. Exploration's RNG
(`games/exploration/quest/rng.py`) is the *canonical* splitmix64 (a
different algorithm — `0xBF58476D…` finalisers), so it is NOT the same
family and stays out of scope; fishing's migration is left for a later
slice so this PR stays contained to the mining seam the idea names first.

Hard invariant: mining's produced RNG sequences must be **byte-identical**
before and after. Pinned empirically — a 7 658-record baseline over
`grid._cell_seed` / `encounters.encounter_seed` / `cell_at` /
`resolve_at` across seeds `{0,1,7,12345,999,2^63,2^64-1}` and a coord
sweep was hashed before the refactor (SHA `f081d413…b634fee`) and must
re-hash identically after.

## 💡 Session idea

The two mining `_cell_seed` copies were kept in sync **by comment** only
(`encounters._cell_seed`'s docstring says "mirrors `grid._cell_seed`");
nothing failed if one drifted, because no test asserted the two produced
equal values. This extraction removes the duplication, but the general
class — N hand-rolled copies of one determinism convention kept aligned
by prose — is exactly what the idea doc flags fleet-wide (mining ×2,
fishing, and a divergent exploration copy). Guard recipe for a follow-up:
a `tests/shared/test_rng.py` cross-family pin that asserts every in-repo
seam that *claims* the mining family (grep for the `0x9E3779B97F4A7C15` +
`<<6 … >>2` shape) routes through `games.shared.rng.mix64` rather than
re-inlining the step — anchor `games/shared/rng.py::mix64`, target the
fishing/exploration copies as the next migrations the idea doc names.

## ⟲ Previous-session review

Target: games PR #143 (`claude/preflight-path-fix`, squash `d7595aa`) —
the newest merged card at this branch's base `5db902a`. Its load-bearing
claim ("`check --strict` stops self-skipping the preflight leg; the local
strict ritual and the CI substrate-gate converge on `tools/preflight.py`
via the planted `scripts/preflight.py` shim") is re-verified from this
session's own evidence in the Verification section below: this slice's
`bootstrap.py check --strict` run emits no `preflight script … not found`
NOTE and exercises the floor-guard → pytest → balance gate list, so the
shim is live and load-bearing at `5db902a`. One standing ding carried
forward: #143's own 💡 (a `tests/tools` pin that every
`preflight_scripts` config token EXISTS as a file) is still unbuilt at
this HEAD (`grep -rl preflight_scripts tests/` empty), so the silent-skip
class it named still has no in-repo tripwire.

## ✅ Close-out — Verification

Shipped in PR [#150](https://github.com/menno420/superbot-games/pull/150)
(`claude/shared-rng-seam`). `games/shared/rng.py` holds the mining
splitmix64 family (`mix64` + `cell_seed`, lifted verbatim);
`grid._cell_seed` delegates to it and `encounters.encounter_seed` reuses
it (its duplicate private `_cell_seed` deleted). New registered suite
`tests/shared/rng/` (11 tests, floor 11) added to
`tests/EXPECTED_SUITES.txt`; `docs/balance.md` regenerated for its row.

**Byte-identical invariant — held.** A 7 658-record sequence hash over
`grid._cell_seed` / `encounter_seed` / `cell_at` / `resolve_at` across
seeds `{0,1,7,12345,999,2^63,2^64-1}` + a coord sweep was captured on
`origin/main` before the change and re-computed after: SHA
`f081d413…b634fee` on **both** sides — `BYTE-IDENTICAL TO BASELINE: True`.
Mining's produced RNG sequences did not move a bit.

**Suite — green.** `python3 -m pytest -q` = **821 passed in 32.94s** (810
baseline + 11 new). `python3 bootstrap.py check --strict` pre-flip = exit
1 **solely** on this card's designed born-red hold (advisory-only findings
otherwise — the pre-existing `[model-line-*]` payload nags on the
historical 2026-07-14 cards + one `[owner-action-fields]` nudge, both at
baseline and on files this slice never touched); post-flip clears the hold.
A tripped `tools/gen_balance` / preflight red during the run was the
expected new-suite balance-doc staleness, resolved by `gen_balance --write`
(the single `tests/shared/rng | 11` row) — not a determinism change.

This flip commit releases the claim gate and commits the accumulated
`.substrate/guard-fires.jsonl` telemetry delta (the #142/#143 flip-commit
precedent). The claim file `control/claims/claude-shared-rng-seam.md` rides
the branch, deleted at session close per `control/claims/README.md`.
