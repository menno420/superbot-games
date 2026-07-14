# 2026-07-14 · preflight path fix — plant scripts/preflight.py, converge check --strict on the gate-parity preflight (runtime bugfix)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable-class · medium · runtime bugfix

At HEAD `8c9c320`, `substrate.config.json` → `preflight_scripts` names
`scripts/preflight.py` (the kit default), but that file does not exist —
the repo's real gate-parity preflight lives at `tools/preflight.py`
(#128). Every `bootstrap.py check --strict` full-lane run therefore
self-skips the preflight leg with:

    check: NOTE — preflight script scripts/preflight.py not found —
    skipped (config preflight_scripts; plant one to converge the local
    ritual and the CI gate on one check list).

So the local strict ritual and the CI substrate-gate never actually run
the repo's own check list (floor guard → pytest → balance freshness);
only `tests.yml` does.

Fix (least-divergent, decided from the kit contract): PLANT the
conventional wrapper — `scripts/preflight.py` as a thin shim that
ensures the deps `tests.yml` installs (pytest) and delegates to
`tools/preflight.py` (default 3-step mode), keeping the gate sequence
single-sourced in `tools/preflight.py`. The kit's own
`_default_preflight_scripts` docstring names `scripts/preflight.py` as
"the conventional wrapper path (idea-engine's `scripts/preflight.py`
convergence pattern) so parity arrives on upgrade WITHOUT a config
edit"; superbot-idle PR #137 (squash `8ff9f59`) is the sibling
precedent — it planted the same wrapper (with the same quiet dep-ensure,
because the substrate-gate runner is stdlib-only) rather than editing
the config. Editing the config to point at `tools/preflight.py` would
work mechanically but diverges from the kit default and the fleet
convergence pattern for zero benefit. The shim self-skips (exit 0, one
NOTE line) when `SBG_PREFLIGHT=1` — i.e. when it is reached from INSIDE
a `tools/preflight.py` run (`--flip` step 4 invokes
`bootstrap.py check --strict`) — so the one-command flip flow does not
run the 810-test suite twice; the outer preflight run owns the leg, the
same doctrine as the kit's `SUBSTRATE_KIT_PREFLIGHT` nested-run guard.

Work claim `control/claims/claude-preflight-path-fix.md` rides this
branch (the #97–#104 same-branch claim precedent); it is deleted at
session close per `control/claims/README.md`.

Verified at flip time on this head: `python3 -m pytest -q` = **810
passed in 42.50s** · `python3 scripts/preflight.py` = `preflight GREEN —
all three gates passed (floor guard, pytest, balance)`, exit 0 (inner
pytest 809 passed, 1 skipped — the skip is the preflight smoke test's
designed `SBG_PREFLIGHT` self-skip) · `bootstrap.py check --strict`
pre-flip = the not-found NOTE GONE, exit 1 solely from this card's
designed born-red hold; post-flip = exit 0. Failure propagation proven
empirically: a temporary injected `exit 42` in the wrapper surfaced as
an exit-affecting `[preflight-script] scripts/preflight.py: exit 42:
INJECTED-FAILURE-PROBE` finding (then reverted). CI at first push:
tests / reconcile / enable-auto-merge SUCCESS; substrate-gate red was
exactly the designed `[session-card-hold]` hold, with no
`[preflight-script]` finding in the gate's stdlib-only venue — the
dep-ensure worked where it matters. This flip commit also releases the
claim and commits the accumulated `.substrate/guard-fires.jsonl` delta
(the #142 flip-commit precedent).

## 💡 Session idea

The not-found NOTE this slice closed is a SILENT-FOREVER class: a repo
whose `preflight_scripts` entry never resolves stays unconverged
indefinitely (games shipped #128's real preflight six merges before
anyone noticed strict wasn't running it — the NOTE scrolls past in
advisory noise). Pin the wiring in-repo: a `tests/tools` test that (1)
every `substrate.config.json` → `preflight_scripts` entry's script
token exists as a file, and (2) `scripts/preflight.py` stays delegating
to `tools/preflight.py` (subprocess it with a stub target or assert on
`GATE_PARITY_PREFLIGHT`) — so a future rename of `tools/preflight.py`
or a config regen reds in pytest instead of re-opening the silent skip.
Dedupe against existing cards' ideas: the #131/#133 cards' preflight
ideas are about `--flip` CARD SELECTION (diff-derived vs mtime), the
#142 card's idea is config↔workflow allowlist drift, the #134 card's is
clock-seam injection; no card pins config-path EXISTENCE. (A kit-side
variant — upgrade the NOTE to an advisory when a conventional
alternative like `tools/preflight.py` exists — belongs to the kit lane;
the in-repo test needs no kit change.)

## ⟲ Previous-session review

Target: games PR #142 (`claude/automerge-guard-split`, squash
`8c9c320`, merged by `github-actions[bot]` 2026-07-14T18:39:36Z — the
guard split it shipped landed it). Its load-bearing claims re-verified
from this session's own evidence, not its card's word: (1) "regenerated
byte-identical to the kit template output" REPRODUCES —
`automerge_enabler_workflow(*_automerge_params(config))` == the live
`.github/workflows/auto-merge-enabler.yml` at `8c9c320` → **True**
(run fresh this session); (2) its "known merge-safe delta" (enabler
arms card-blind at PR open, merge stays blocked by the required
substrate-gate) observed LIVE on this PR #143: `enable-auto-merge`
SUCCESS armed squash auto-merge at open while substrate-gate held the
designed `[session-card-hold]` red — window real, floor held, exactly
as documented; (3) its `reconcile` guard ran SUCCESS on this PR's
born-red head. One ding: #142's card claims the drift advisory
"quieted" but the guard's own job-level `if:` re-introduces the same
hand-copied allowlist unwatched — its own 💡 concedes this; until that
advisory extension exists, the guard list drifts by convention only.
One observation for the next reader: #142 merged 2m51s after PR open
(open 18:36:45Z → bot merge 18:39:36Z) — the flip was already on the
branch at open, so the born-red hold never engaged on that PR; the
hold's live proof came from THIS PR instead.
