# 2026-07-16 — mirror idle #142: tolerate auto-merge landing before the provenance stamp

> **Status:** `in-progress`
> **Branch:** `claude/mirror-reconcile-race-fix` · claim `control/claims/claude-mirror-reconcile-race-fix.md`

- **📊 Model:** fable-5 · medium · runtime bugfix — mirror idle #142's provenance-disarm race tolerance into the host card-guard · session opened 2026-07-16T01:11Z (`date -u`)

**Goal:** superbot-idle PR #142 (squash `884aeae`) fixed a TOCTOU race in
its host-owned `automerge-card-guard.yml`: when GitHub auto-merge lands a
PR in the ~2 s window between the script's merged-check and the provenance
branch's first `gh pr merge --disable-auto` call, that call — the only one
in the branch still riding the `gh()` helper's `fatal=True` default —
exits 1 on `GraphQL: Can't disable auto-merge for this pull request.` and
the run goes red, contradicting the workflow's own stated policy
("provenance is a survey aid, not a gate"). Idle's card
`.sessions/2026-07-15-reconcile-race-fix.md` names this repo as a mirror
candidate: our guard was split out per #142 mirroring idle's post-#137
guard, and its provenance branch carries the identical fatal-disarm call.
Mirror the semantics — that ONE disarm becomes race-tolerant (fatal=False,
re-check merged state, `::notice::`/`::warning::`, exit 0) — while the
card-disarm branch's fail-loud disarm stays untouched (an
in-progress-card PR must never be left silently armed).
