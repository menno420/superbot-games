# 2026-07-12 · install auto-merge-enabler (uniform fleet landing, fm ORDER 029)

> **Status:** `complete`
>
> 📊 Model: fable-5 · 2026-07-12T23:30Z · install PR-landing workflow

## What happened

Installed `.github/workflows/auto-merge-enabler.yml`, adapted from idea-engine's
enabler (git blob `819a8d5`), per the fleet owner's live directive (fleet-manager
coordinator chat, 2026-07-12T23:00Z: "yes you have my explicit standing
permission to merge all PRs ... can you make sure the same workflows exist
here?"; recorded as fleet-manager inbox ORDER 029, uniform landing fleet-wide).

**Doctrine change:** supersedes this repo's manual-merge doctrine (in force
since the #40 premature-merge incident — arm-at-open out-raced the close-out
card flip). The enabler's in-progress-card SKIP guard is the fix for exactly
that incident class: a PR whose diff carries an `in-progress`/`drafted`
`.sessions/` card is never armed; the flip-to-complete push re-runs the
workflow via `synchronize` and arms it then. `do-not-automerge` is the per-PR
opt-out.

**Guards retained from the reference:** same-repo · non-draft · branch-prefix
allowlist (kit list + observed local prefixes `claude/`, `docs/`, `mining/`,
`exploration/`, `control/`) · do-not-automerge label + 15s fresh re-read ·
rules-count refuse-to-arm (zero required contexts ⇒ warn, never arm) ·
card-skip · arm via `gh pr merge --auto --squash` with `Head-ref:` provenance.

**Host adaptations:** status-badge regex tolerates this repo's observed badge
variants (`complete`, `✅ complete`, ✅ `complete`) via a non-letter-prefix
skip (`[^A-Za-z\n]*`), unit-checked; `drafted` added to the skip statuses
(the kit auto-draft state is also not-final per `.sessions/README.md`);
provenance + re-apply-duty header (this file is host-installed here, not
kit-planted — if a later adopt/upgrade plants a kit-owned enabler, re-apply
the customizations).

**Required-check caution (watch item):** `substrate-gate`'s required-state on
main was unverifiable from this session (rules API walled); the enabler's own
`rules` step on this PR logs the ground truth `required contexts (N)`. If
N=0 the install is a safe no-op until the owner requires `substrate-gate` on
main (clickset in the session report).

## 💡 Session idea

The enabler's `rules` step already computes the exact fact the fleet keeps
re-deriving by hand ("does this repo have a required check?"). A tiny
follow-up: have the step also write that count into the run's job summary
(`$GITHUB_STEP_SUMMARY`) so any agent can read required-check state from the
latest enabler run's summary page instead of probing the walled rules API —
turns every PR into a free, always-fresh branch-protection audit.

## ⟲ Previous-session review

The previous session (#66, mining host-adapter scoping) rendered a clear
partially-buildable verdict with a ⚑ packaging decision instead of inventing
a contract — the right call, and its PR body's Before/After discipline made
tonight's audit trivial to verify. Improvement it surfaces: it left #65/#66
open READY+green awaiting merge — under the manual-merge doctrine that was
correct, but it is exactly the parked-PR class this session's enabler
retires; nothing else to improve there, the doctrine (not the session) was
the bottleneck.
