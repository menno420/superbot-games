# 2026-07-11 · Mining lane — archive-prep (VERIFY + TOP-UP)

> **Status:** `complete`
>
> 📊 Model: Opus 4.8 · 2026-07-11 · mining gen-1 archive-prep — verify + top-up, no new feature work

## Goal

Archive-prep the mining lane: VERIFY (not redo) that mining gen-1 is complete on
`main`, capture any chat-only knowledge durably, run the kit's full session enders,
and leave a single reachable ARCHIVE-READY note — because this session's chat is
being archived and anything not committed is lost.

## What I did

- **Hard-synced** to `origin/main` HEAD `5d38593` (#49 merged; substrate-kit v1.12.0).
  Clean tree. `bootstrap.py check --strict` = exit 0 on clean main (baseline).
- **Verified state.** Mining gen-1 is complete and already archived on `main`
  (`games/mining/core/**` + `games/mining/sim/` shipped via gen-1 #5/#9/#11/#14/#15/#20).
  No mining PR/branch/claim dangles: `control/claims/` holds only its README (no stale
  mining claim to release); the open PRs (#50/#52/#53/#54/#55) are all world-games /
  dnd / economy / persistence work, none mining-lane.
- **Drift found + reported (did NOT silently "fix" by resurrecting old structure):** the
  two-lane mining/exploration split is archived; `control/status.md` is now the active
  **single-writer world-games heartbeat**, not a shared aggregate with an "exploration
  section." The task's Step-5 instruction to edit a mining section of `status.md` while
  preserving an exploration section is premised on a superseded structure — following it
  would resurrect the archived split AND re-dirty ~6 open PRs (the shared-bookkeeping
  churn #34 root-caused). **Deliberately did NOT touch `control/status.md`.** Recorded
  the mining archive-ready heartbeat in mining's OWN file (`control/status-mining.md`) +
  the archive note instead — achieving the heartbeat goal without the harm.
- **Model-line conflict** recorded as an explicit `⚑ OWNER-DECISION` in
  `control/status-mining.md` and the archive note (six fields). It was already captured
  on main (status.md ⚑ item 2, ORDER 003 / #46); recorded honestly as "captured, working
  resolution in force, only the formal ruling pending" — not as a fresh undiscovered delta.
- **Archive note** `docs/retro/archive-ready-2026-07-10-mining.md` written and linked from
  `docs/retro/README.md`: verified true state, every ⚑ owner-action, resume read-order,
  gen-2 next 1–3 with block status, and the cross-project D-0043 wait.

## Documentation audit

`bootstrap.py check --strict` = exit 0 (only the pre-existing never-exit-affecting
owner-action-fields advisory on `control/status.md`, which is the world-games seat's
file, untouched by me). New archive note reachable via `docs/retro/README.md`. No test
floors touched (no tests added). Nothing left chat-only — confirmed in the archive note.

## Grooming

Confirmed the gen-2 queue (`docs/retro/queue-state-mining-2026-07-09.md`) is groomed and
ordered; annotated block status in the archive note (items 1–2 unblocked pure-domain work
in this repo; item 3 cross-project-blocked on superbot-next D-0043). No feature work
started — archive-prep is VERIFY + TOP-UP only.

## 💡 Session idea

**A machine-checkable `ARCHIVE-READY` badge gate.** The repo already gates session cards
(Status / 📊 Model / 💡 / review) via `substrate.config.json` `session_markers`. An
archive-ready note has a stronger, checkable contract: it should assert (and a checker
could verify) that every ⚑ in the lane's status file is either resolved or restated in the
note, that every "next 1–3" item carries a block-status annotation, and that the note names
its verified HEAD SHA. That turns "nothing is chat-only" from a hand-waved closing sentence
into a lint — the same enforce-don't-exhort move the kit already makes for session cards.
(Dedup-checked: no existing idea covers an archive-note lint; the closest is the session-card
gate, which this extends rather than duplicates.)

## ⟲ Previous-session review

The prior mining close-out (#20 heartbeat, 2026-07-10) did the important thing right: it
left mining gen-1 in a clean terminal state (all PRs merged, main green, resume docs +
queue-state committed), so this archive-prep found the substance already durable and only
needed a consolidation note — the mark of a good close-out. What it (understandably) could
not anticipate: the fleet then collapsed the two-lane split into a single world-games seat,
which silently invalidated the "status.md is a two-writer aggregate" mental model that this
very archive-prep task inherited. **Concrete system improvement it surfaces:** a close-out
note should record the *structural assumptions* it was written under (here: "status.md is
per-lane / two-writer"), so the next session can detect when the ground has shifted instead
of acting on a stale structural premise. The kit could bake a one-line "structural
assumptions at close" field into the archive-note template — cheap, and it would have flagged
this exact drift on read.
