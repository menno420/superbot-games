# 2026-07-14 · night test — test: dnd scene graph — reachability sweep from the start scene

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T03:16:02Z · night-dnd-scene-reachability

Test slice from `.sessions/2026-07-11-dnd-scene-chaining.md`, verified
at branch base `e196b85`: `games/dnd/data/scenes.py:145`
`_assert_transitions_resolve()` checks DANGLING edges only; nothing
checked the converse — that every registered scene is REACHABLE from
the start scene, so an orphaned scene (in `SCENES`, pointed at by
nobody) would ship silently as copy the player can never see.

The scene data model was read first and its truths pinned: 3 scenes
(`waystation_road` → `waystation_gate` / `treeline_watch`,
`waystation_gate` → `treeline_watch`); `START_SCENE =
"waystation_road"` (`services/dnd_workflow.py:80`); the model has NO
explicit terminal marker — `choose()` sets `ended = next_scene is None`
per OPTION (`services/dnd_workflow.py:279`), so "terminal" is a
property of options, and a scene whose options are ALL `None`-edged is
a sink.

Shipped `tests/dnd/test_scene_reachability.py` (5 tests, ≤8 as
specced, read-only over the data):

* `START_SCENE` is registered and is the walking-skeleton anchor.
* BFS over `next_scene_id` edges from `START_SCENE` covers `SCENES`
  exactly — the orphan sweep. **No unreachable scene found** at HEAD
  (no headline bug; the value is the tripwire).
* Every scene offers ≥1 option (catalog-level; `Scene.__post_init__`
  enforces it per-scene, pinned here so the sweep stands alone).
* No edge dangles — CI-visible complement to the import-time assert,
  which `python -O` would strip.
* Sinks are deliberate, not dead ends: exactly one sink today
  (`treeline_watch`, the escort's end-of-beat, pinned with a comment
  saying a new sink must be a decision), and every scene's clamp
  default is a stay-put (`next_scene_id=None`) option, so no scene can
  strand the player mid-transition.

Floor `tests/dnd` 63 → **68** (floor==collected); `docs/balance.md`
regenerated BEFORE flip (gen-balance gate), `--check` green. Full
suite **744 → 749 passed** locally; strict check exit 0 post-flip.
Claim `control/claims/night-dnd-scene-reachability.md` self-released
in this flip commit (established precedent).

## 💡 Session idea

Reachability now proves every SCENE is live, but nothing proves every
EFFECT is: `games/dnd/core/effects.py`'s `EFFECTS` registry rows are
validated as *referenced-if-used* (`Scene.__post_init__`), never as
*used* — a pre-priced effect nobody's option references is dead
balance data that silently drifts (today: are all of `escort_step` /
`scout_narrate` / `rest_noop` reachable? only a sweep says). Add an
**effects-liveness sweep**: every `EFFECTS` id is referenced by ≥1
option on a scene REACHABLE from `START_SCENE` (composing this slice's
BFS), and each such effect is executed once via the seam in a scripted
walk asserting its reward bundle lands in the ledger. Dedupe check
against the used-idea list: detector-trip registry proves sim
predicates can fire, not effect rows are wired; the display-table
completeness registry syncs vocab↔display strings, not
registry-row→graph liveness; effect-grant-derived gen_balance DND
table renders effect numbers into docs, it doesn't prove
reachability/execution; sim-harness smoke runs renderers. No card idea
to date sweeps EFFECTS liveness against the reachable scene graph.

## ⟲ Previous-session review

The previous slice is this run's #125
(`claude/night-verb-table-help-parity`, born-red `8846a75`, refactor
`8a9ab80`, flip `2ccb7d0`, squash-merged to main as `e196b85` by
github-actions[bot]). Verified against live CI: at the flip SHA both
tests (run 29302973647) and substrate-gate (run 29302973681) completed
success; the born-red SHA's substrate-gate failure (run 29302699306)
was exactly the designed pre-flip HOLD. Verified against this branch's
base (which includes `e196b85`): the three `_ACTIONS` tables exist with
`_ACTION_VERBS = frozenset(_ACTIONS)` in mining/fishing/exploration,
dnd's structure is untouched as its card honestly reports, the four
`tests/<game>/test_help_parity.py` files collect 8 tests via the
`tests/conftest.py` extractor fixture, and the four floors read
188/121/63/17 with `pytest tests/dnd -q` matching before this slice's
own bump. Its byte-identity claim is credible but note the honest
limit: the transcripts live in the session scratchpad, not the repo,
so the evidence is the card's hashes plus the untouched CLI test
suites staying green — a future scripted-transcript check would make
that reproducible in CI (that idea is already on the used list, not
re-claimed here).
