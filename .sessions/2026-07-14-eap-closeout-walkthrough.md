# 2026-07-14 · EAP closeout walkthrough — ORDER 009 (b) (docs)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable-class · 2026-07-14T11:35:35Z · eap-closeout-walkthrough

ORDER 009 (`control/inbox.md` @ `ed2fabb`, landed via #136) served across
two PRs, split per bus rules:

- **(a) control PR #138** (`claude/eap-closeout-restamp`, control-only fast
  lane, no card): wholesale heartbeat truth-stamp at main HEAD `ed2fabb` —
  77 squash-merges (#59…#136) recorded since the stale 2026-07-12T10:16:22Z
  stamp (the order's "~35 PRs #87–#135" premise re-verified per Q-0120:
  understated); orders line `acked=001-009 done=001-007` with dispositions;
  fishing full-roster + cook-leg SIM-REQUESTs flipped `open` → `routed`
  (sim-lab's ORDER 008, per ORDER 009 / fm PR #193; one cross-repo verify
  attempt denied, verbatim recorded); exploration band import + rung-3
  packaging + persistence/transfer/D2 parked with citations; the ≤40-line
  EAP close-out summary with the OWNER ACTIONS checklist verbatim appended
  to `control/outbox.md`. The brief-vs-order ARCHIVE conflict is flagged
  explicitly in the PR body (order wins; #84 precedent).
- **(b) this PR #139**: `docs/eap-closeout-walkthrough-2026-07-14.md`,
  sections A–E exactly as ordered — A EAP shipped (PR-cited, depth links) ·
  B run/verify commands · C OWNER ACTIONS (deep links, bolded
  recommendations, VERIFY steps; block-of-record copied verbatim to the
  outbox summary) · D 5-minute tour · E handoff batons. `owner-guidance`
  badge in the first 12 lines; linked from `docs/retro/README.md` for
  reachability. Born-red card + telemetry row were this branch's FIRST
  commit (`5d29434`).

Verified at flip time on this head: `python3 -m pytest -q` = **810 passed**
(exit 0) · `python3 tools/preflight.py` = GREEN, all three gates ·
`python3 bootstrap.py check --strict` = exit 0 with this card complete.
This flip commit also releases the work claim
(`control/claims/eap-order-009-closeout.md`, landed via #137) per the
same-branch-delete precedent (#106/#107, night-wave cards).

## 💡 Session idea

The OWNER ACTIONS checklist now lives in TWO committed places by design —
the walkthrough §C (the block of record) and the `control/outbox.md`
close-out summary ("copied verbatim") — and nothing but review discipline
keeps them identical; the first later edit to one silently forks the
owner's to-do list. Add a tiny `tools/check_block_sync.py` (or a
`check` finding class): a `<!-- block-sync: <id> -->` marker pair pins that
two fenced/quoted blocks in different files must be byte-identical, red
when they diverge. Dedupe check against used card ideas (stamp_scaffold
generator; ledger-drift KIT-ASK; telemetry backfill; coverage ratchet;
detector-trip / display-table / sim-smoke / quest-completability
registries; registry-derived CI pytest paths; preflight --flip): nearest
neighbors are the ledger-drift KIT-ASK (detects current-state vs merge-log
drift — different surface, advisory) and stamp_scaffold (generates
citations — authoring aid); neither pins cross-file block identity. This is
the `gen_balance --check` freshness idea generalized from generated-vs-source
to prose-vs-prose.

## ⟲ Previous-session review

Previous seat session: the #135 truth-stamp
(`.sessions/2026-07-14-night-truth-stamp-closeout.md`, squash `34c5b98`),
re-verified against origin/main this wake: the "Recently shipped" bullets it
added for #120–#134 match the git log SHAs one-for-one (spot-checked #134
`4330559`, #133 `bc85689`, #128 `1d38230` — all correct); its "suite
695 → 810" claim reproduces exactly (`python3 -m pytest -q` = 810 passed
this session, twice); and its `<!-- truth-stamped-at: 4330559… -->` anchor
points at the true pre-#135 HEAD. Nothing overstated. One honest gap,
inherited forward: the ledger's "In flight" still calls #102 an OPEN PR —
true when #135 merged (05:13:35Z), falsified two hours later when #102
merged (`1c323c1`, 07:20:35Z) — recorded as baton E.5 in the walkthrough
rather than fixed here (out of this order's scope).
