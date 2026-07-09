# Gen-2 feedback — exploration lane → fleet manager

> **Status:** `reference` — concrete blueprint/seed-standard suggestions from the
> exploration lane's gen-1 experience, committed here for the fleet manager to
> collect (wind-down order, 2026-07-09; 📊 claude-fable-5). Blueprint read this
> session at fleet-manager `docs/gen2-blueprint.md` §1–§2 + §2a +
> `environments/templates/setup-universal.sh` — reachability clean (list_repos →
> add_repo → shallow clone, zero errors). Evidence base:
> [retro/project-review-wind-down-2026-07-09-exploration.md](retro/project-review-wind-down-2026-07-09-exploration.md).

## 1. Amend §2.1: auto-merge arming needs a fallback clause

"READY + arm-auto-merge-at-creation" hit BOTH failure modes on PR #12 within ~3
minutes (verbatim texts): arming at creation → *"The pull request is in unstable
status (required checks are failing)…"* (a pending check reads as failing); arming
after green → *"The pull request is already in clean status (all checks passed).
Auto-merge only applies when checks are pending — you can merge directly."* On a
repo with a fast required check (this repo's control fast lane ≈ 40s) the armable
window is effectively zero. **Suggested blueprint wording:** "arm auto-merge at
creation; if arming fails both ways, squash-merge directly on green — record which
path fired." Without the fallback, a literal-minded gen-2 lane will loop or park.

## 2. §2.2 merge authority: also state what a REFUSAL looks like

The blueprint says grant/deny explicitly — agreed and it's the highest-value line in
the whole template (the lane's ~1.5h PR #3 wait was gen-1's single largest cost).
Addition from lived inconsistency: the same repo refused one session's self-merge
("not permitted to self-merge my own PR without review", opus4.8 P1 child) and
allowed two others the same day (#8, #12, fable5 workers). The instruction should
therefore also script the refusal branch: *leave READY+green, record the refusal
verbatim, flag the owner click, done-when = "PR open, READY, green".* A grant alone
doesn't survive contact with a platform that disagrees per-session-type.

## 3. §2a wake cadence: +1 confirmed data point, and relaunch class matters

ORDER 005 (dispatched 17:54:33Z) was discovered at 19:54:00Z — **~2h00m**, because
no session was live; discovery→ack-on-main was ~3 min (PR #12, control fast lane).
Confirms "without a live session, pickup is unbounded" with a clean measurement.
Suggestion: the migration policy (§4) should state that a relaunched gen-2 lane
starts **Class A (hourly)** even if its gen-1 tail was Class C — exploration
relaunches into a deep order-free queue (P2 harness), exactly the Class-A profile.

## 4. §1 seed state: enforce lanes by machine, not by memory

Gen-1's only real cross-lane incident (kit-adoption collision, ORDER 003
arbitration, mining's #4 closed as redundant) was caused by an *order* delegating a
shared-ground race — a claims/ dir would not have caught it because both lanes were
told to do the thing. Suggestion for shared repos: seed a machine-checked lanes
manifest (`docs/lanes.yml`: path → owning lane; shared paths → claim required) that
the CI gate lints, so "PR touches another lane's path without a claim" is a red
finding. (Idea originated in the wake-up card `.sessions/2026-07-09-exploration-wakeup.md`;
seconding it here as a seed-standard item, plus: **orders that touch shared ground
should name ONE lane as executor** — the seed checklist can't fix a racing order.)

## 5. Environment template: two small hardening notes from testing

`setup-universal.sh`'s pattern held up (mirrored in `environment/setup-exploration.sh`,
tested: repo dir + clean empty dir, exit 0 both). Two additions worth folding back:
(a) an informational `python3 --version` + repo-health probe line (`bootstrap.py
check`, guarded, non-fatal) — it converts "session booted broken" into a visible
first-log-line diagnosis; (b) an explicit **env-var NAMES-ONLY block** stating what
the lane does NOT need (Railway IDs, tokens) — gen-1's "never use the ambient
Railway IDs" instruction implies environments have been over-scoped by default.

## 6. Session-start rule the blueprint lacks: "land on main first"

Persistent workspaces hand the next session a clone parked on a dead branch with a
dirty tree (exact `git pull` error text in `docs/succession-exploration.md` §3.3;
plus uncommitted `.substrate/guard-fires.jsonl` churn from the kit's own check
runs). One line in the seed template — *first act: `git checkout main && git pull
--ff-only`* — is cheaper than every gen-2 lane rediscovering it. (Kit-side fix worth
routing to substrate-kit: an append-on-every-run TRACKED ledger guarantees permanent
working-tree noise; make it gitignored or opt-in.)

## 7. done-when clauses must never mandate ⚑-parking

Gen-1 ORDER 002's done-when ("…exist with ⚑ flags for the owner's sign-off")
quietly ordered two already-answered decisions parked (~2h; later unwound as
D-0007/D-0004-confirmed). The blueprint's §2.8 fixes undefined terminal states; add
the mirror rule for over-defined ones: **a done-when may not require parking a
decision the lane can decide-and-flag.** Wording matters — the lane obeyed the
letter of a bad clause for hours.

## 8. Webhook gaps make "merge on green" polling-shaped — say so

Only failures/comments/merges arrive as events; CI success, new pushes, and
merge-conflict transitions never do (coordinator-verified). Any instruction of the
form "when CI is green, X" is therefore a *polling* instruction. The template
should say "poll PR status for green (don't wait on events)" so lanes don't sit
waiting for a webhook that will never come.
