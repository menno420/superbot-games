# 2026-07-14 · preflight path fix — plant scripts/preflight.py, converge check --strict on the gate-parity preflight (runtime bugfix)

> **Status:** `in-progress`
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
