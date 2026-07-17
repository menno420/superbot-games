# 2026-07-16 · overnight planning menu — docs: 60-idea un-filtered owner-triage proposal set (docs-only)

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus 4.x · high · planning/docs

Planning-menu slice, landing the doc committed on branch
`claude/overnight-menu-0716` at base `0dc8f99` (branched off `197966d`, #150).
The deliverable is `docs/planning/2026-07-16-overnight-menu.md` — a deliberately
**un-filtered** 60-proposal menu (M1…, grouped A–F by category) for the owner to
triage tomorrow: each idea carries a one-line Pitch, an Effort (S/M/L), a Risk &
reversibility line (↩️/⚠️/🔒), and an Unblocks/enables line. It is a `plan`-badged
candidate set, NOT approved or claimed work — breadth over a curated shortlist,
so the owner accepts/defers/vetoes per number.

Scope: docs-only. This session adds only the born-red session card, its claim
(`control/claims/claude-overnight-menu.md`), and the flip to complete — the
60-idea doc itself is already committed at `0dc8f99`. `control/status.md` (the
read-only archive) is deliberately NOT touched, and no code, workflow, or game
logic moves. The doc is grounded in a fresh read of the repo at HEAD `197966d`:
citations are to real files/PRs (e.g. A1 cites `games/fishing/core/rng.py` as
the third splitmix64 copy #150 left outside the shared seam), but sizes/risks
are estimates the owner re-weighs.

## 💡 Session idea

A planning menu is only as durable as its HEAD anchor: this doc pins itself to
`197966d`/#150 and a "821 passed" suite baseline, both of which go stale the
moment the next PR merges — exactly the drift the current-state ledger keeps
tripping on (#151's whole slice was re-stamping a ledger four merges behind
main). The machine-watchable companion here is a check-time advisory
(`[planning-menu-stale-head]`) that greps a `docs/planning/*.md` doc's
`**HEAD:** \`<sha>\`` line and compares it to the merge-base of the doc's own
last-touched commit against main — advisory (never exit-affecting) when the doc
cites a HEAD more than N merges behind, so a menu that references a superseded
tree surfaces in one finding instead of misleading a triage read. Guard-recipe
anchor: extend the same stamp-scanning pass the #89 ledger-drift KIT-ASK and
#151's `[ledger-open-pr-drift]` idea both target (`tools/stamp_scaffold.py`
already reads a `<!-- truth-stamped-at: -->` anchor) — one grep of the
`**HEAD:**` line, one merge-base count, one advisory. The fact this very session
found by hand: the menu's own baseline (`197966d`, 821 passed) is already one
merge behind main once #151 lands.

## ⟲ Previous-session review

Target: games PR #151 (`claude/current-state-refresh-0716`) — the newest
merged card at this branch's post-merge base (its card
`.sessions/2026-07-16-current-state-refresh.md` and claim arrived via the
`git merge origin/main` this session ran). Its load-bearing claim
(`docs/current-state.md` re-stamped 2026-07-16 at HEAD `197966d`, "through #150
with #149 open", suite 810→821) is re-checked from this session's own evidence,
not its card's word: `docs/current-state.md` EXISTS at this merged HEAD carrying
the `<!-- truth-stamped-at: 197966d… -->` anchor and the corrected open-PR /
watermark claims, and its "821 passed" figure REPRODUCES here —
`python3 -m pytest -q` = 821 passed (see Close-out), the #150 baseline unmoved
by docs. Its claim-file discipline holds: `control/claims/` at this base carries
the README plus `claude-current-state-refresh.md` (#151's own, rides-then-deletes
per convention) and the still-un-swept `claude-eap-ack.md` /
`claude-shared-rng-seam.md` / `claude-truth-refresh.md` leftovers (out of THIS
slice's scope, flagged not touched — PR #149 is already deleting two of them).
One standing ding carried forward: #151's 💡 (`[ledger-open-pr-drift]`, an
open-PR-count advisory companion to the #89 watermark check) is still unbuilt at
this HEAD — this session's 💡 above extends the same stamp-scan seam to planning
docs, so both remain candidates for one future guard slice.

## ✅ Close-out — Verification

*(to be filled at flip)*
