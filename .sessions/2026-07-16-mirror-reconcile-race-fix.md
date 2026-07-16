# 2026-07-16 — mirror idle #142: tolerate auto-merge landing before the provenance stamp

> **Status:** ✅ `complete`
> **Branch:** `claude/mirror-reconcile-race-fix` · claim `control/claims/claude-mirror-reconcile-race-fix.md` (deleted at close)

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

## What happened

Confirmed the vulnerable pattern before editing: this repo's guard at
`5db902a` carried the byte-identical pre-fix line — the provenance
branch's first `gh("pr", "merge", "--disable-auto", pr, "--repo", repo)`
riding `fatal=True` — at the same structural spot as idle's pre-#142
file, so idle's hunk applied semantically 1:1 (only the in-comment
incident citation was adapted). The card-disarm branch's fail-loud
disarm and the `gh()` helper's `fatal=True` default are untouched.
Also swept the claim ledger: `claude-eap-ack.md` and
`claude-truth-refresh.md` were stale (work merged as #148/#147 —
merged-state API-verified before deleting) and are dropped in this PR.

## Verify at flip

- `python3 -m pytest -q` → `810 passed in 39.38s`
- `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/automerge-card-guard.yml'))"`
  → parses; the embedded reconcile Python also `ast.parse`s clean
- `python3 bootstrap.py check --strict` → red ONLY on this card's
  designed born-red hold; 16 `model-line` payload advisories on the
  historical 2026-07-14 night cards + 1 `owner-action-fields` nudge are
  pre-existing, untouched scope (advisory-only, never exit-affecting)
- guard-fires delta from the check run committed per kit instruction

## 💡 Session idea

The card-guard is host-owned and hand-mirrored from idle, so this exact
fix can silently regress the next time someone hand-edits or re-mirrors
the file — and no test reads the workflow at all today. Add a
`tests/test_card_guard_workflow.py` tripwire: `yaml.safe_load` the
workflow, extract the reconcile step's embedded Python, `ast.parse` it,
and assert (a) it parses, (b) the provenance branch's first
`disable-auto` call carries `fatal=False` while (c) the card-disarm
branch's disarm carries no `fatal` kwarg (fail-loud default). Dedupe
checked: no existing card's 💡 touches the workflow files —
truth-refresh's is a kit-version-drift advisory, preflight-path-fix's
is a `preflight_scripts` existence pin, the night cards' ideas are
game-runtime scoped.

## ⟲ Previous-session review

previous-session review: `.sessions/2026-07-15-truth-refresh.md`
(landed as PR #147) plus the card-less eap-ack control slice (#148).
Verified from this session's own evidence: (1) truth-refresh's "810
passed" suite claim reproduces exactly at this HEAD (39.38s); (2) its
#142-split description of the guard matches the file this session
edited (host-owned reconciler, kit enabler separate). One ding, now
fixed here: both 2026-07-15 sessions left stale claim files behind on
main — truth-refresh's card even says its branch went LOCAL-ONLY with
the claim riding un-deleted, yet the work later merged as #147, and
eap-ack (#148) merged without its flip ever deleting
`claude-eap-ack.md` — so the ledger showed two live claims for
terminal work until this PR's sweep. Delete-at-close is the whiteboard
rule; when a close-out can't land (platform denial, as truth-refresh
recorded), the NEXT session's collision scan should treat merged-PR
claims as deletable clutter, exactly as done here.
