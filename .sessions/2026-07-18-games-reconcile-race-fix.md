# 2026-07-18 · games-reconcile-race-fix — ci(card-guard): tolerate auto-merge landing before the provenance stamp (port idle #142)

> **Status:** `in-progress`
>
> 📊 Model: opus-4.8 · high · ci bugfix

⚑ Owner-authorized self-initiated CI fix (menno420, live 2026-07-18):
port superbot-idle PR #142 (commit `884aeae`) to games'
`.github/workflows/automerge-card-guard.yml`. Reversible.

**The bug (TOCTOU in the reconcile job's HEAD-REF PROVENANCE branch).**
The guard's provenance-stamp branch (`if not in_progress and armed and
"do-not-automerge" not in labels:`) reads the PR's merged state via the
API, then ~seconds later re-stamps `Head-ref:` into the pending squash
body by disarming and re-arming auto-merge. The disarm was
`gh("pr", "merge", "--disable-auto", pr, "--repo", repo)` on the
`fatal=True` default. GitHub-native auto-merge can land the PR inside
that window, so `--disable-auto` errors `GraphQL: Can't disable
auto-merge for this pull request`, the helper `sys.exit(1)`s, and the
whole `reconcile` job fails. That is the benign post-merge `reconcile`
failures + auto-merge enable/disable churn seen across today's PRs
(#171–#175). The PR still merged correctly every time — provenance
stamping is a survey aid, not a merge gate — so the job failure was
pure noise.

**The fix (mirror idle #142).** Make ONLY that one provenance-stamp
disarm call tolerant: `fatal=False`; on a nonzero return, re-fetch the
PR view and branch — if `merged` → `::notice::auto-merge fired before
the provenance stamp — PR merged without Head-ref, skipping.` + exit 0;
if not merged → `::warning::provenance disarm failed but the PR is not
merged — leaving the enabler's arm standing` + exit 0. Tolerate-and-
exit-clean, NOT a lock. The upstream in-progress-card DISARM call
(`if in_progress and armed:`) stays fatal — a failed disarm on a
born-red card must still fail loud so an in-progress-card PR is never
left silently armed. Minimal diff: the single call's error handling
only; no restructuring of the workflow.

## 💡 Session idea

⚑ Self-initiated. The two disarm calls in this guard now carry opposite
failure contracts, and that asymmetry IS the design: the born-red-card
disarm is a safety gate (must succeed or fail loud — leaving an
in-progress PR armed is a real hazard), whereas the provenance disarm is
cosmetic (a missing `Head-ref:` line degrades a survey, never merge
safety). A single fatal=default helper flattened both into "must
succeed", which is how a cosmetic TOCTOU became a red job. Guard recipe
for the next adopter: when one helper serves both a safety operation and
a best-effort operation, the best-effort caller must opt OUT of fatal
and re-check ground truth (here: the PR's merged state) on failure —
anchor `automerge-card-guard.yml` reconcile step, the
`if not in_progress and armed` branch's `--disable-auto` call.

## ⟲ Previous-session review

Target: superbot-idle PR #142 (commit `884aeae`, HEAD `38648a5`) — the
identical fix already landed in idle's `automerge-card-guard.yml`.
Re-read idle's fixed file from `origin/main` before porting: idle changed
exactly the provenance-stamp branch's disarm from the fatal default to
`d = gh(..., fatal=False)` + a merged/not-merged re-check that exits 0
either way, and left the in-progress-card disarm above it fatal. Games'
guard is a byte-near mirror of idle's post-#137 guard (games PR #142,
`automerge-guard-split`), so the same single-line divergence applies
cleanly. Games' file still carried the unfixed fatal call at branch base
`10d7aa3` (#175, main HEAD) — confirmed the pattern is present before
editing, so this is a live port, not a no-op.
