# game-mining · status
updated: 2026-07-09T17:20Z
phase: P0→P1 — kit engaged; pure domain ported (draft); retro delivered. Blocked at the merge gate.
health: yellow — all work verified & green, but nothing shipped to main (merges are owner-gated; #4 conflict-dirty)
kit: substrate-kit v1.2.0 (engaged on main via exploration's #3; mining's own adoption #4 is the ORDER-003 duplicate)
last-shipped: nothing to main from the mining lane (all output on draft PRs #4/#5; retro on ready PR #9)
orders: acked=001,002,003,004 done= (none fully — every done-when requires a merge the agent is blocked from performing)

⚑ needs-owner:
- MERGE PR #4 then PR #5 — self-approval guardrail blocks the agent (verbatim denials in
  docs/retro/project-review-2026-07-09-mining.md §E). PRECONDITION: #4 is `mergeable_state:
  dirty` (conflicts main after #3 planted the same kit) — the ORDER-003 rebase must run first
  (drop the duplicate kit plant, keep mining-lane deltas). Rebase is agent-doable; can be
  authorized in-chat.
- MERGE retro PR #9 — same guardrail; #9 is clean & mergeable (based on current main).
- Alternative collapsing the above: authorize the merges directly in the mining session's own
  chat (the classifier may accept owner-in-session as genuine authorization).
- Aggregate control/status.md two-writer risk — kit's check_status_current hardcodes
  control/status.md vs per-lane files; relayed to kit-lab as their ORDER 004. Owner call: take
  the kit fix or formalize the aggregate as manager-written.
- main is check --strict RED + has NO CI enforcement — it merged the kit via #3 without the
  hygiene fixes on the unmerged #4/#8 (lanes.md badge, D-0043 stamp allowlist, substrate-gate
  workflow). Wiring the CI gate is owner-gated executable config; decide who lands it (#4, #8,
  or a dedicated fix) so the repo actually enforces the gate.

blockers: the self-approval merge guardrail (nullifies ORDER 001/003/004 done-when) + #4's
post-#3 conflict.

pr-in-flight:
- #4 mining/adopt-substrate-kit — OPEN, DRAFT, DIRTY (conflicts main), CI substrate-gate green. ORDER-003 duplicate; needs rebase.
- #5 mining/port-pure-domain — OPEN, DRAFT, clean-vs-#4, CI substrate-gate green. 18 modules → games/mining/core/, 62 tests pass.
- #9 mining/retro-2026-07-09 — OPEN, READY, clean; the retro (this order). Auto-merge NOT armed (owner action).

notes: docs/founding-plan-mining.md + docs/lanes.md are binding. Retro answers:
docs/retro/self-review-mining-2026-07-09.md; wake-up review: docs/retro/project-review-2026-07-09-mining.md.
Continuation without owner: ORDER-003 rebase → games/mining/workflow seam → superbot-next
adapter (read the contract first) → grid encounters → economy sim + parity goldens.
