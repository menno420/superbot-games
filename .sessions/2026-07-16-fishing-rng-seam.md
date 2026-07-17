# 2026-07-16 · fishing RNG seam — migrate fishing onto the shared games/shared/rng.py splitmix64, delete its duplicate mix (pure refactor)

> **Status:** ✅ `complete`
>
> 📊 Model: Claude Opus 4.x · high · mechanical refactor

Completing the shared-deterministic-RNG-seam migration that #150 started
(`docs/ideas/shared-deterministic-rng-seam-2026-07-10.md`). #150 extracted
mining's integer splitmix64 `(seed, coords…)` mix into `games/shared/rng.py`
(`mix64` + `cell_seed`, the mining family) and migrated the two mining call
sites, deliberately leaving fishing for a later slice. Fishing still carries
its own byte-identical copy of that mixing step (`games/fishing/core/rng.py` —
`_mix`, `_MASK`, `_GAMMA`) which its own docstring names a "promotion
candidate" for exactly this seam.

Scope this slice (deliberately narrow — the coordinator's slice + the claim's
scope line): point `games/fishing/core/rng.py` at the shared seam, deleting the
duplicated `_mix`/`_MASK`/`_GAMMA` primitive, keeping only the fishing-domain
logic that is genuinely fishing-specific (`_FISHING_SALT` + the `spot_id`
byte-fold in `fishing_seed`). Nothing else moves: the module stays in the
fishing core (the purity guard still pins exactly `catch/economy/rng/species/
spots`), `fishing_seed`'s public signature is unchanged.

Algorithm-match verified FIRST: fishing's `_mix` is byte-for-byte the shared
`mix64` — same golden-ratio gamma `0x9E3779B97F4A7C15`, same
`(h + γ + ((h<<6)&M) + (h>>2)) & M` step, same 64-bit mask — so the migration
is the *same* algorithm, not the canonical `0xBF58476D…` splitmix64 that
exploration's quest RNG uses. If they had differed this slice would have
STOPPED rather than move fishing's stream.

Hard invariant: fishing's produced RNG sequences must be **byte-identical**
before and after. Pinned empirically — a sequence hash over `fishing_seed` +
`catch.resolve_cast` across seeds `{0,1,7,12345,999,2^63,2^64-1}` (plus
negatives and >64-bit values that exercise the mask wrap) and a `spot_id`
sweep was captured before the refactor and must re-hash identically after.

## 💡 Session idea

#150's own 💡 flagged the exact follow-up guard this slice enables: a
cross-family pin asserting every in-repo seam that *claims* the mining
splitmix64 family (the `0x9E3779B97F4A7C15` + `<<6 … >>2` shape) routes
through `games.shared.rng.mix64` rather than re-inlining the step. With
fishing migrated, the last hand-rolled copy of the mining mix is gone — the
only remaining `<<6 … >>2` inline is the shared module itself. Guard recipe
for a follow-up: extend `tests/shared/rng/test_rng.py` with a repo-grep pin
that FAILS if the `((h << 6)` mixing shape appears in any `games/**/*.py`
outside `games/shared/rng.py`, so a fourth hand-rolled copy can never be
re-introduced untested — anchor `games/shared/rng.py::mix64`, target a new
`test_no_inline_mining_mix_copies` in `tests/shared/rng/`.

## ⟲ Previous-session review

Target: games PR #150 (`claude/shared-rng-seam`, squash `197966d`) — the
seam this slice completes and the newest merged card touching this area.
#150's load-bearing claim ("`games/shared/rng.py` holds the mining
splitmix64 family lifted verbatim; mining's two call sites delegate with a
byte-identical sequence hash held") is re-verified from this session's own
evidence: this slice imports `mix64`/`MASK64` straight from that module and
its own before==after fishing hash holds (Verification below), proving the
shared `mix64` reproduces fishing's local `_mix` bit-for-bit — the extraction
#150 landed is byte-faithful to a *third* independent caller, not just the two
mining ones it migrated. One standing ding carried forward: #150's 💡 (the
cross-family inline-copy grep pin) is still unbuilt at this HEAD, now with one
fewer copy to catch (see Session idea).

## ✅ Close-out — Verification

Shipped in PR [#154](https://github.com/menno420/superbot-games/pull/154)
(`claude/fishing-rng-seam-0716`). `games/fishing/core/rng.py` now does
`from games.shared import rng as shared_rng` (mining's import style) and
`fishing_seed` reuses `shared_rng.mix64` / `shared_rng.MASK64`; the duplicated
`_mix` / `_MASK` / `_GAMMA` primitive is deleted. `_FISHING_SALT` and the
`spot_id` byte-fold stay local (the only fishing-specific logic). No call-site
churn — `catch.py` imports `fishing_seed` unchanged; the fishing purity guard
still pins the core to exactly `catch/economy/rng/species/spots`. No test
added/removed → `tests/fishing/EXPECTED_MIN_TESTS.txt`,
`tests/EXPECTED_SUITES.txt`, `docs/balance.md` untouched.

**Algorithm match — verified FIRST.** Fishing's `_mix` was byte-for-byte the
shared `mix64`: same gamma `0x9E3779B97F4A7C15`, same
`(h + γ + ((h<<6)&M) + (h>>2)) & M` step, same 64-bit mask — the *mining*
family, NOT the canonical `0xBF58476D…` splitmix64 that quest RNG uses. Same
algorithm ⇒ the migration cannot move the stream. (Had they differed the slice
would have STOPPED without opening a PR.)

**Byte-identical invariant — held.** A sequence hash over `fishing_seed` +
`catch.resolve_cast` across seeds `{0,1,7,12345,999,2^63,2^64-1}` (plus
negatives and >64-bit values exercising the `&MASK64` wrap) and a `spot_id`
sweep (empty / unicode / punctuation / 200-char) was captured on `origin/main`
before the change and re-computed after: SHA
`419aeb7afd9897b0e8c8b2fd48d10f07fe6e5a277fd0d25a459940b68d67db22` on **both**
sides — before == after. Fishing's produced RNG sequences did not move a bit.

**Suite — green.** `python3 -m pytest -q` = **827 passed in 35.36s** (baseline
827, unchanged — a byte-identical refactor adds no tests). `python3
bootstrap.py check --strict` pre-flip = exit 1 **solely** on this card's
designed born-red hold (`HOLD (by design): … declares an in-progress Status`);
every other finding is advisory-only and pre-existing at baseline (the
historical `[model-line-*]` nags on the 2026-07-14/16 cards + one
`[owner-action-fields]` nudge on `control/status.md`, none on files this slice
touched). This flip commit clears the hold.

This flip commit releases the claim gate and commits the accumulated
`.substrate/guard-fires.jsonl` telemetry delta (the #142/#143/#150 flip-commit
precedent). The claim file `control/claims/claude-fishing-rng-seam.md` rides
the branch, deleted at session close per `control/claims/README.md`.
