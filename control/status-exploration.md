# game-exploration · status
updated: 2026-07-09T20:09Z
phase: WIND-DOWN COMPLETE — ready for archive + fresh (gen-2) session
health: green
last-shipped: #13 — gen-1 succession package (whole-life wind-down retro · succession doc · gen-2 Custom Instructions proposal · tested env setup script · gen-2 feedback); #12 — ORDER 005 PING-ACK (merged 19:56:08Z)
blockers: none
orders: acked=001,002,003,004,005 done=001,002,003,004,005
kit: substrate-kit v1.2.0 — adopted (D-0002); substrate-gate.yml live; check --strict green on this head
⚑ needs-owner: |
  NOTHING BLOCKING. Gen-2 relaunch clicks (optional, in order):
  (1) paste the proposed gen-2 Custom Instructions from
  docs/gen2-custom-instructions-exploration.md §B into the relaunched Project (agents
  cannot edit Project settings); (2) create the wake routine — relaunch starts Class A
  hourly per the lane's gen-2 feedback §3 (the measured ORDER-005 pickup without a
  routine was ~2h); (3) branch-deletion housekeeping (agents 403 on branch delete):
  claude/exploration-ping-ack-005, claude/exploration-wind-down-2026-07-09 (after #13
  merges), claude/exploration-wakeup-2026-07-09, plus the older merged branches listed
  in docs/retro/project-review-2026-07-09-exploration.md §e — do NOT delete
  mining/port-pure-domain or mining/grid-encounters (live mining drafts #5/#11);
  (4) the #13 merge click ONLY IF this session's own merge-on-green failed (the PR
  records the exact error if so). Standing veto windows unchanged: D-0007 (Q-0040
  posture, open until the P3→P4 gate), D-0009 (CI gate; revert = veto).
notes: |
  GEN-1 CLOSED. Succession read order for the next session: docs/succession-exploration.md
  (first-10-minutes files, walking-skeleton check, known walls with exact error text).
  Whole-life retro: docs/retro/project-review-wind-down-2026-07-09-exploration.md.
  QUEUE AT CLOSE — done: P0+P1 (#3), wake-up audit + first CI (#8), ORDERs 001–005;
  in-flight: nothing after #13; NEXT DEFAULT (order-free, gen-2 first real session):
  P2 survival sim harness on the D-0004 option-(a) baseline
  (docs/design/survival-d1-rebaseline.md) — it also produces the pinned bands that
  retire D-0008's placeholder caps in games/exploration/quest/catalog.py.
  SHARED INTERFACE ANNOUNCEMENT (standing, docs/lanes.md): the public shared
  encounter seam is games/shared/encounter/interface.py (EncounterResolver Protocol +
  EncounterRequest/Outcome + EncounterTrigger GRID_ROAM/EXPLORE_ACTION/CHAT_ACTIVITY);
  mining owns the PRODUCTION core and replaces the reference impl via the Protocol —
  coordinate before changing the interface.

---

## Close-out heartbeat — 2026-07-10T13:47Z (final; appended below the wind-down marker, which stands)

updated: 2026-07-10T13:47Z
phase: archived-pending-gen-2
health: green — all lane PRs terminal (#3, #8, #12, #13 merged; mining #5/#11 out-of-lane drafts remain)
routine: not armed — coordinator holds no scheduled wakes; next wake is owner-initiated (gen-2 boot or grand-review session)
orders: acked=001,002,003,004,005 done=001,002,003,004,005

### NEXT-SESSION BRIEF

1. Owner answers the Part 1 framing questions
   (superbot `docs/eap/gen1-wrapup-email-part1-questions-2026-07-09.md`) and finalizes
   the wrap-up email from the grand-review's final candidate.
2. Run the grand-review prompt
   (superbot `docs/planning/gen1-grand-review-session-prompt-2026-07-10.md`).
3. Gen-2 lane resumes at P2 survival sim harness (D-0004 baseline).

### Non-derivable facts for the next session

- superbot's session gate requires a `telemetry/model-usage.jsonl` row in any PR that
  adds a `.sessions/` card (Q-0194 guard).
- Auto-merge arming window ≈ zero on fast-CI repos — arm immediately after PR
  creation, or squash-merge directly if "already in clean status".
- Git is the clock of record where docs disagree (canonical trap: PR #8 merged
  17:06:06Z, relayed elsewhere as ~18:30Z).

### ⚑ Owner asks (unchanged)

Paste gen-2 Custom Instructions; create the gen-2 wake routine; optional branch
cleanup (agents 403 on branch delete); standing veto windows D-0007/D-0009;
email Part 1 answers + the final send decision.
