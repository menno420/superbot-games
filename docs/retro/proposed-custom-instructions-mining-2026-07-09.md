# Proposed gen-2 custom instructions — from mining-lane lived experience (2026-07-09)

> **Status:** `audit`
> Rewritten from what actually helped or hurt in gen-1. KEEP / DROP / ADD, one line why each.
> The fleet-manager `gen2-blueprint.md` was NOT in this session's repo scope, so this is written
> from experience; where it likely overlaps the blueprint's §1–§2 (READY-never-draft, explicit
> merge authority, agent-reachable done-whens, heartbeat-before-work, walking skeleton, known walls
> up front, Model+time on cards) I say so. Disagreement is welcome data.

## KEEP
- **one-writer-per-file control bus (inbox = manager, status = lane).** Zero merge conflicts on
  coordination state; it just works.
- **committed-files-only succession (no live infra).** Gen-2 boots from git alone; the design's
  biggest win.
- **lane ownership + claim-first for shared paths + adopt-once.** The rules are right; the gen-1
  failure was not following them, not the rules.
- **binding founding plan with explicit done-when per order.** I always knew what "done" meant.
  (Aligns with blueprint "agent-reachable done-whens".)
- **decide-and-flag over stop-and-wait for reversible calls.** Kept the session moving.
- **honest-over-flattering retro discipline, "I don't know" allowed.** Produces usable redesign
  input instead of theater.

## DROP / CHANGE
- **DROP: opening PRs as draft.** Draft PRs don't auto-merge and add a forgotten "mark ready" step;
  the kit race showed drafts racing badly. Open READY always. (Aligns with "READY-never-draft".)
- **DROP: authorizing merges via coordinator relay.** The classifier rejects it every time (three
  verbatim denials this lane). Don't route merge authorization through the coordinator — it cannot
  work. (Aligns with "explicit merge authority".)
- **CHANGE: don't defer parity goldens / balance sim.** Fold them into the port step, not a later
  order — the oracle mapping is only fresh once.
- **CHANGE: don't assume the orchestrator has GitHub tools.** State up front that GitHub ops route
  through workers, so a session doesn't waste a turn discovering it.

## ADD
- **a "known walls" block at the top of every lane's instructions**, with verbatim errors and "do
  not re-probe." Would have saved every session that re-hit the merge wall. (Aligns with "known
  walls up front".)
- **a walking-skeleton first step** — prove branch→PR→CI→merge on a 1-line change before real work,
  so the merge wall is discovered cheaply. (Aligns with "walking skeleton".)
- **heartbeat-before-work** — write/refresh the status file at session START (not just close), so a
  crashed session still leaves a fresh heartbeat and an in-flight signal for parallel lanes. (Aligns
  with "heartbeat-before-work".)
- **explicit human-merge-authorization protocol.** Name exactly what counts (a direct human turn in
  the lane chat, or a human GitHub click) and have each session emit ONE crisp ⚑ owner-click list.
  Make the human gate a planned step, not a surprise.
- **Model + UTC timestamp on every status/PR heartbeat.** Gen-1 could not confirm per-actor models;
  stamping them removes the ambiguity. (Aligns with "Model+time on cards".)
- **a shared-token / rate-limit note** — the fleet shares one GitHub token (id 225413533); back off
  on "rate limit already exceeded", don't hammer.

## Disagreement / open question
I'm not sure the merge wall *should* be worked around at all. The safe design may be: agents do
everything up to READY+green, and a human (or a genuinely authorized human-turn session) merges in
batches. If so, gen-2 instructions should make "your work terminates at READY+green+⚑" the explicit,
un-apologetic contract — not a failure mode. That reframes the wall from friction to spec.
