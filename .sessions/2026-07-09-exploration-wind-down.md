# 2026-07-09 · exploration wind-down — gen-1 → gen-2 succession package

> **Status:** `complete`

- **📊 Model:** claude-fable-5 · standard · wind-down/succession (worker session, exploration lane)

## Scope (declared up front — born-red)

Owner's WIND-DOWN order for the exploration lane (gen-1 → gen-2 fleet transition;
blueprint §4 natural-boundary migration). Seven deliverables, one branch
(`claude/exploration-wind-down-2026-07-09`), READY PR, merge on green:

1. Finish/park — open-PR disposition + the lane's roadmap/queue state committed.
2. Extensive dated project review → `docs/retro/project-review-wind-down-2026-07-09-exploration.md`.
3. Succession doc (first-10-minutes read order, walking skeleton, known walls with
   exact error text) → `docs/succession-exploration.md`.
4. Gen-2 Custom Instructions rewrite proposal → `docs/gen2-custom-instructions-exploration.md`.
5. Tested defensive environment setup script → `environment/setup-exploration.sh` (+ env var names).
6. Gen-2 blueprint feedback → `docs/gen2-feedback-exploration.md`.
7. Ready marker — `control/status-exploration.md` flipped to wind-down-complete as the
   deliberate LAST commit (with this card's flip).

Pre-work already landed this session: ORDER 005 PING-ACK (PR #12, merged `27d0673` —
dispatch 17:54:33Z → discovery 19:54:00Z → ack-on-main 19:56:08Z). Exploration-lane files
only; mining's draft PRs #5/#11 are out of lane and untouched.

## Close-out

All seven deliverables shipped (paths in the PR body / retro §7). fleet-manager
blueprint reachability: SUCCESS (gen2-blueprint §1–§2 + setup-universal.sh read).
Setup script tested twice (repo dir + clean dir), exit 0 both. Local CI mirror
(`check --strict --require-session-log --session-log <this card>`): only the
born-red session gate was red before this flip; badges/stamps clean (8
reason-carrying allowlist suppressions, pre-existing entries whose reasons cover
the new retro/ledger citations).

### Commits
- `f4b5d3c` — born-red card, PR #13 open READY.
- `5d80d6f` — deliverables 1–6 (retro · succession · gen-2 instructions ·
  gen-2 feedback · tested env setup · ledger/index drift fixes).
- (final) — this flip + status ready-marker.

## 💡 Session idea

`bootstrap.py skeleton` — a kit subcommand that runs the walking-skeleton check
mechanically: create a control-only heartbeat branch, open a READY PR, attempt
auto-merge arming (recording which of the two known arming errors fires), poll to
green, squash-merge, and print a one-line verdict ("merge path proven: direct-merge
lane" / "arming works" / "REFUSED: <verbatim>"). Today the skeleton is a prose
procedure (`docs/succession-exploration.md` §2) every new session re-derives by
hand; making it a command turns the gen-2 seed standard's most important check into
a 2-minute mechanical step and captures authority-refusal text as data. Dedup: not
in `docs/ideas/` (README only) or the retro docs as an implemented mechanism.

## ⟲ Previous-session review

The wake-up session (PR #8) was the lane's best: it converted four parked flags into
decisions with sourced evidence (D-0008's "the constants don't exist" find was real
verification work) and its retro honesty markers ("cannot determine") held the right
bar. Two genuine misses: (1) **timestamp drift** — its status file stamps
`updated: 18:05Z` while git says its PR merged 17:06:06Z; both cannot be right, and
git wins (fleet blueprint §2a caught other lanes doing local-time-as-Z; retro §3(f)
records ours). (2) **Index drift** — it added two retro docs but not to
`docs/retro/README.md`'s landed-reviews list (fixed on sight this session). To be
fair: NOT its miss — ORDER 005, which it never acked, only reached main 49 minutes
*after* its merge. Concrete workflow improvement: the session-close ritual should
include "timestamps from `date -u` only, cross-checked against git" and "every new
doc lands in its index in the same commit" as mechanical checklist lines.
