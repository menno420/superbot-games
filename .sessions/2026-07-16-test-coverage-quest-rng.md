# 2026-07-16 · test coverage — quest DetRng bad-input contract (games/exploration/quest/rng.py)

> **Status:** `complete`
>
> 📊 Model: Claude Opus 4.x · high · test writing

The quest/encounter engine's deterministic core `games/exploration/quest/rng.py`
is a hard-invariant module (Q-0040): it "owns every outcome the AI later
narrates", so it must be PURE and SEEDABLE. Its determinism seam is well
tested (`test_rng.py`: same-seed identity, cross-`PYTHONHASHSEED` `derive_seed`
stability, order-sensitivity, a pinned known value), BUT its **bad-input
contract is unguarded**. Coverage at branch base (full default collection)
shows `rng.py` at 90% with the misses concentrated in the guard clauses:
`DetRng.randint` line 68 (`hi < lo` → ValueError), `DetRng.choice` line 75
(empty sequence → IndexError), and `DetRng.weighted_choice` lines 84/87
(items/weights length mismatch → ValueError; non-positive weight sum →
ValueError). None of these raise-paths, nor the `lo == hi` single-value
`randint` boundary, nor the direction of weight-proportionality (heavier item
chosen strictly more often than a lighter one) are asserted anywhere.

A refactor that dropped any of these guards — e.g. removing the
length-mismatch check so `weighted_choice` silently zips to the shorter
sequence, or the `total <= 0` check so an all-zero weight vector does
`next_u64() % 0` — would corrupt the deterministic stream the engine depends
on and slip through the current suite green. This slice pins that contract.

## 💡 Session idea

The determinism seam and the bad-input contract are two DIFFERENT test
concerns that tend to get written unevenly: the "same seed → same bytes"
property is exciting and always gets a test, while the "garbage in → loud,
specific raise" property is dull and routinely skipped — yet it is exactly the
guard that catches a careless refactor of the hot path. A cheap check-time
advisory could compare, per pure-RNG module, the count of `raise` statements
in the source against the count of `pytest.raises` targeting that module's
symbols in its suite; a module whose guard clauses outnumber their assertions
is flagged as "contract-under-tested". Guard-recipe anchor: the raise/`pytest.raises`
ratio scan belongs beside the existing model-line/claims scanners in the kit's
`check` pass — one AST count over `games/**/rng.py`, one over the sibling
suite, advisory on imbalance.

## ⟲ Previous-session review

Target: games PR #150 (`claude/shared-rng-seam`, squash `197966d`) — the
shared deterministic-RNG seam. Its card's carried-forward 💡 (a
`tests/shared/rng` cross-family pin so every seam claiming the mining
`0x9E3779B97F4A7C15` splitmix64 family routes through `games.shared.rng.mix64`
rather than re-inlining it) remains unbuilt at this base, and this session
confirms the drift surface is real: `games/exploration/quest/rng.py` carries
its OWN `_splitmix64` (constants `0x9E3779B97F4A7C15` / `0xBF58476D1CE4E5B9` /
`0x94D049BB133111EB`) with no route through the shared seam — a fourth
hand-rolled copy alongside fishing's. This slice does not attempt that
promotion (out of scope, and the module is deliberately dependency-free per
its Q-0040 docstring); it hardens the module's public contract in place so a
future promotion has a bad-input regression net to migrate against.

## ✅ Close-out — Verification

Shipped in PR [#152](https://github.com/menno420/superbot-games/pull/152)
(`claude/test-coverage-quest-rng-0716`). Six deterministic tests appended to
`games/exploration/tests/test_rng.py` pin the module's bad-input contract:
`randint` `hi<lo` → `ValueError` (was line 68, uncovered), `choice` empty
sequence → `IndexError` (line 75), `weighted_choice` items/weights length
mismatch → `ValueError` (line 84), `weighted_choice` non-positive weight sum →
`ValueError` (line 87), the `randint(lo, lo)` span-1 boundary, and the
direction of `weighted_choice` proportionality (heavier chosen strictly more,
both buckets reachable). `games/exploration/quest/rng.py` moves 90% → 98% (only
the documented-unreachable `items[-1]` fallback, line 95, is left — covering it
needs an impossible `total>0`-with-no-bucket state). Suite floor
`games/exploration/tests` bumped 55 → 61 and `docs/balance.md`'s per-suite floor
table regenerated (`tools/gen_balance.py`) to match, so the balance-freshness
gate stays green.

- `python3 -m pytest -q` → **827 passed in 36.16s** (baseline 821 + 6).
- `python3 bootstrap.py check --strict` → **all checks passed** (exit 0;
  "session log …test-coverage-quest-rng.md complete"). Only advisory model-line
  / owner-action warnings (pre-existing, never exit-affecting).

Landing path: hub-venue, auto-merge armed on green per the night landing
grammar. No production code touched — tests + floor + regenerated balance page
only.
