# 2026-07-14 · night test — detector-trip registry: every sim invariant predicate has a proven violation witness

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T02:40:40Z · night-detector-trip-registry

Test slice implementing the detector-trip registry card idea from
`.sessions/2026-07-14-night-coverage-economy-sim.md`, verified
unimplemented at main `fefe16c`: no registry module existed;
`tests/shared/sim/test_economy_sim.py` (#99) constructs violations for
economy_sim's three named invariants individually, but nothing
ENUMERATED the invariant predicates across all sims or structurally
REQUIRED a False-returning violation witness per predicate — a new
always-True dead detector would have landed green.

Shipped `tests/shared/sim/test_detector_trips.py` (11 tests, registered
`tests/shared/sim/` suite). The predicate set is DERIVED from the five
sim modules themselves (`economy_sim`, `menu_sim`, `catch_sim`,
`encounters_sim`, survival `sim`): every module-level function the
module defines with a `bool` return annotation (string `"bool"` under
`from __future__ import annotations`, class `bool` accepted too) — not
hand-listed. Enumeration found exactly four predicates: economy_sim's
`all_bundles_within_global_cap` / `item_faucets_mint_no_currency_or_xp`
/ `noop_paths_mint_nothing`, plus one sibling the originating card
predicted ("the per-domain sims' verdict helpers"): menu_sim's
`_reward_leq_global_max`, whose fail branch had NO trip test anywhere
(the #99 work covered economy_sim only). catch_sim / encounters_sim /
survival sim define no bool predicates — verified by reading each.
The registry maps each key to a (healthy, violate) witness pair —
`dataclasses.replace` on a tiny-sweep report for the cap/faucet trips,
targeted `monkeypatch.setitem` of a minting `rest_noop` for the noop
trip, an over-cap `RewardBundle` for menu_sim — no shipped constant
edited. Completeness both ways (enumerated⊆registered and
registered⊆enumerated each fail loudly, naming the key), a
known-anchors pin so the enumerator itself can't rot to yielding
nothing, and per-predicate parametrized pairs: shipped state True,
witness False. All four predicates trip — no dead detector found.

`tests/shared/sim` floor 29 → **40** (floor==collected convention);
`docs/balance.md` regenerated BEFORE flip (gen-balance gate),
`gen_balance.py --check` green. Full suite 716 → **727 passed** locally
on this branch; strict check exit 0. Claim
`control/claims/night-detector-trip-registry.md` self-released in this
flip commit (established precedent).

## 💡 Session idea

The registry proves each predicate CAN trip — but the report FLAGS that
carry those verdicts to readers are a second, unpinned wiring surface:
`EconomyReport.grant_within_global_cap` /
`item_faucet_mints_no_currency` / `noop_mints_nothing` and
`MenuBalanceReport.all_within_global_max` are bool dataclass fields
that `run()` must populate from the matching predicate, and a
copy-paste slip (a flag wired to the wrong predicate, or set
unconditionally True) would render a healthy-looking report over a
tripped invariant. Add **report-flag wiring pins**: enumerate every
sim report dataclass's bool fields (derived via `dataclasses.fields`,
not hand-listed) and assert each equals its predicate recomputed on the
same report — including on a DOCTORED report where the predicate is
False, proving the flag follows the predicate, not a constant. Dedupe
check against the used-idea list: the detector-trip registry (this
slice) proves predicates can return False; the sim-harness smoke
registry executes render paths; the degenerate-bounds matrix sweeps
empty inputs; none pins flag↔predicate wiring. No card idea to date
targets it.

## ⟲ Previous-session review

The previous slice is this run's #121 (`claude/night-cover-gen-balance`,
born-red `c1708d0`, tests `9142b11`, flip `aeffbcc`, squash-merged to
main as `fefe16c`). Verified against live CI: at flip SHA `aeffbcc` all
three workflows completed green (tests run 29301579259, substrate-gate
29301579242, auto-merge-enabler 29301579234), and born-red `c1708d0`'s
substrate-gate failure (run 29301428722) was exactly the designed
pre-flip HOLD while tests (29301428724) and the enabler (29301428770)
stayed green. Verified against this branch's base (includes `fefe16c`):
`tests/tools/test_gen_balance.py` exists with its 13 tests (8+13=21
collected in `tests/tools`, floor file reads 21), the balance page's
floors table carries `| \`tests/tools\` | 21 |`, and the card's pinned
quirk is real — `gen_balance.check()` on an out-of-repo stale path
raises `ValueError` from `path.relative_to(_REPO_ROOT)` (re-confirmed
by running the pin). One honest nit: #121's card says "all 17
section/subsection headers"; the EXPECTED_HEADERS list in the test is
indeed 17 entries, but that count mixes 8 `##` sections and 8 `###`
subsections plus the `#` page title — calling it "17 headers incl. the
title" would have been the precise phrasing.
