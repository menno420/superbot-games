# 2026-07-17 · cli-case-sweep — test: pin a cross-CLI case-normalisation invariant (guards the #158 drift class)

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus 4.x · high · test-hardening + surgical bugfix

⚑ Self-initiated: small game-improvement slice (owner order 2026-07-17 —
improve the game via contained, tested, independently-landable slices).
Executed at branch base `b0a9cfe` (#159).

PR #158 fixed a real bug: the standalone mining CLI silently failed on a
CAPITALISED item/branch token (`sell Iron` falsely read "0 held") because it
never lower-cased the token before the seam's lowercase-keyed lookups. That is a
**drift class**, not a one-off — any game CLI that forwards a name/id token to a
lowercase-keyed seam without normalising case can regress the same way, and no
single-CLI test would catch it. This slice adds the sweep that pins the
invariant across **every** game CLI.

`tests/cross_cli/test_cli_case_normalisation.py` drives each CLI's REAL scripted
entry point twice — once with a lowercase token, once with the same token
CAPITALISED — and asserts an IDENTICAL committed outcome (same state delta, same
audit-row count). Each adapter also asserts its lowercase baseline actually
COMMITTED, so a CLI that silently no-ops on BOTH cases cannot pass the sweep
vacuously.

The sweep surfaced a **real latent bug of the #158 class**: the exploration CLI
never lower-cased its `offer <id>` / `act <action>` tokens, so `offer Supply_Run`
was an honest-but-wrong "unknown quest" no-op (quest never set) and
`act Deliver_Crates` advanced no objective — exactly the "capitalised token
silently misfires" failure #158 fixed in mining. Fix (surgical, mirrors #158):
lower-case the token at the CLI boundary in `_offer_and_echo` and `_do_act`
(`games/exploration/cli.py`) — the template ids and objective-action names are
all lowercase, so this only ever normalises case, never meaning; the audited
quest seam is untouched and no balance/economy/reward number changes.

Scope: new suite `tests/cross_cli/` (the parametric sweep + `EXPECTED_MIN_TESTS.txt`
floor) + `tests/EXPECTED_SUITES.txt` registry row + `games/exploration/cli.py`
(the two boundary `.lower()`s) + `docs/balance.md` regenerated (its Test-suite-floors
section pins the new suite). Mining (`sell`) and fishing (`sell`) already
normalise and the sweep pins them; the dnd gap is xfailed (see idea below).

## 💡 Session idea

The sweep left one CLI **deliberately uncovered**: dnd. Its bounded-menu pick
treats a capitalised option id (`Advance_Escort`) as OFF-MENU and clamps to the
scene's deterministic safe default — that is not the #158 *silent-failure* bug
but a DOCUMENTED product semantic ("anything off-menu keeps you safe"). Folding
case-variant option ids into exact matches is a product-semantics decision, not
the mechanical `.lower()` the other CLIs take, so it is deferred (xfailed with a
strict marker so a future fix trips XPASS and forces the sweep to absorb it).
Follow-up backlog item: **decide whether the DM's-seat bounded pick should
case-fold option ids before the off-menu clamp** — if yes, lower-case the token
in `games/dnd/cli.py:_resolve_choice_id` (seam untouched, mirroring this slice)
and drop the xfail so dnd joins the sweep; if no, keep the xfail as the pinned,
intentional gap. Either way the invariant is now explicit instead of silent.

## ⟲ Previous-session review

Target: games PR #159 (`b0a9cfe`, "fix(mining): energy.seconds_until signals
unreachable targets instead of 0") — this branch's base and main's current HEAD.
Its load-bearing claim (a passive-regen target ABOVE `max_energy` can never be
reached, so `seconds_until` must return a distinguishable "never" sentinel
instead of the in-band `0` that aliased "already reached") re-checks TRUE from
this session's own reading of the shipped source, not its word:
`games/mining/core/energy.py` now guards the boundary first with
`if target > max_energy: return math.inf` (the honest, arithmetic-safe "never"),
and below the cap the body is unchanged bar the now-redundant
`min(max_energy, target)` clamp, so every reachable answer is byte-identical —
no player-facing balance/economy/message change. Its 3 regression tests are
present in `tests/mining/test_energy_capacity.py` (already-reached → `0`,
reachable → correct seconds incl. sub-interval remainder, unreachable → `inf`),
the mining floor it bumped (193 → 196) is intact, and its sole non-test caller
(`games/exploration/survival/sim.py` `_greedy_digs`) passes a small
`target = t.cost ≤ max_energy` that never reaches the unreachable branch, so the
`math.inf` sentinel is caller-safe. Verified against the shipped tree, green
baseline 835 passed at this HEAD.
