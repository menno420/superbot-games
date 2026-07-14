# 2026-07-14 · night test — test: dnd effects liveness — every effect reachable and executable

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T03:45:24Z · night-dnd-effects-liveness

Test slice from #126's card idea, verified fresh at branch base `1d38230`:
nothing in `tests/dnd/` swept `games/dnd/core/effects.py`'s `EFFECTS`
registry against the reachable scene graph — `Scene.__post_init__`
validates referenced-if-used, never *used*, so an orphaned pre-priced
effect would ship silently as dead balance data.

The data model was read first: 3 effects (`rest_noop`, `scout_narrate`,
`escort_step`), 3 scenes × 3 options each, `leverage.menu_width` floor 2
(xp 0) / 4 (xp 1000), and the seam's VERDICT-044 `bundle_minted` one-shot
guard (`services/dnd_workflow.py:261-270`). Shipped **7 tests** (≤8 as
specced) in `tests/dnd/test_effects_liveness.py`, read-only over
data + seam: the orphan sweep (every `EFFECTS` id referenced by ≥1 option
on a scene BFS-reachable from `START_SCENE`); each effect executed once
via `services/dnd_workflow.choose` from a fresh session steered along a
BFS-derived option path — no raise, `ok=True`, exactly one audit row per
choose (D2); narrate-only effects mint nothing (checked at EVERY
referencing site, totals snapshot-compared); `escort_step` mints exactly
`catalog.TIER_CAPS[RewardTier.I]` verbatim with the mint recorded as the
audited mutation; the mint-at-most-once guard pinned INTACT across both
escort sites (second site suppressed, totals unchanged — not weakened);
registry-level determinism (`apply(seed, player_id)` twice ⇒ equal
outcomes); and the floor-width truth that every scene's `rest_noop`
option sits third (never surfaced at width 2) so its liveness at the xp
floor is the CLAMP path — pinned per scene via an off-menu choose.

**No headline bug found**: no orphaned effect, no raising effect, the
guard holds at both sites — the value is the tripwire. Floor `tests/dnd`
68 → **75** (floor==collected); `docs/balance.md` regenerated BEFORE
flip; suite **766 → 773 passed** locally. This slice's local gate was ONE
command for the first time — `python3 tools/preflight.py` (#128's
deliverable, dogfooded green) — plus strict exit 0 post-flip. Claim
`control/claims/night-dnd-effects-liveness.md` self-released here.

## 💡 Session idea

The dnd side now has both liveness sweeps (scenes #126, effects here),
but the exploration quest catalog — the richer registry the dnd effects
themselves borrow from — has neither: nothing proves every quest in
`games/exploration/quest/catalog.py` is COMPLETABLE end-to-end via the
seam (offer → accept → its own `pending_actions` loop → banked reward)
within its bounded action budget at every tier. An uncompletable or
budget-starved quest is dead catalog data a player can accept and never
finish. Add a **quest-catalog completability sweep** in
`tests/exploration/`: for each catalog id × tier, drive the seam's
pending-actions loop to COMPLETED in ≤ the quest's own objective bound,
asserting the banked bundle equals the tier cap. Dedupe check against the
used-idea list: detector-trip registry proves sim predicates fire, not
quest completability; degenerate-bounds matrix pins bounds, it doesn't
walk quests to completion; sim-smoke runs renderers; effects-liveness
(this card) covers dnd's EFFECTS, not the exploration catalog; the
verb-table and display-table ideas are surface-sync. No card idea to date
walks every catalog quest to completion via the seam.

## ⟲ Previous-session review

The previous slice is this run's own #128
(`claude/night-preflight-gate-parity`, born-red `06db813`, implementation
`21410c2`, flip `514bcff`, squash-merged to main as `1d38230` — this
branch's base — by github-actions[bot] at 2026-07-14T03:43:34Z).
Same-session review, so discount accordingly; the external evidence is
strong because that PR changed CI itself and the new path was watched
actually running: at the flip SHA, tests run 29304183318 and
substrate-gate run 29304183316 both success; the tests job (86994067899)
shows step 5 renamed to "gate-parity preflight (floor guard → pytest →
balance freshness)" and its log tail reads "preflight GREEN — all three
gates passed" — the workflow really executed `tools/preflight.py`, not
the old hand-synced steps. Born-red `06db813`'s substrate-gate failure
(run 29304019063) was the designed pre-flip HOLD. Re-checked its numbers
here: `--print-suites` at base emits exactly
`tests` / `games/exploration/tests` / `services/tests`, and this slice's
own preflight run collected the suite green through the derived roots.
One honest wrinkle its card undersells: in CI the run reported
"765 passed, 1 skipped" — the skip is the preflight smoke ITSELF
(`SBG_PREFLIGHT=1` re-entrancy guard), which means the end-to-end smoke
never executes in CI, only in direct local `pytest` runs like this
slice's canonical 773. That's the designed trade (no unbounded nesting),
but it leaves the smoke's assertions CI-unverified — worth remembering
if preflight's banners ever change.
