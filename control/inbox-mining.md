# control/inbox-mining.md — orders to game-mining

> **ONE writer: the manager.** Never edit this file. Report order progress ONLY in
> `control/status-mining.md` (one writer per file — protocol: `control/README.md`).

## ORDER 001 · 2026-07-09T14:23Z · status: new
priority: P1
do: (1) If no `.substrate/` exists yet, adopt substrate-kit from `menno420/substrate-kit`
per its README (adopt → render → engage) through `check --strict` green; if it already
exists, verify engagement instead — kit adoption happens ONCE per docs/lanes.md. (2) Read
`docs/founding-plan-mining.md` + `docs/lanes.md` — both binding. (3) Correct your seeded
`control/status-mining.md`. (4) Begin roadmap P0→P1: study the oracle code in
`menno420/superbot` (`disbot/utils/mining/` + `disbot/services/mining_workflow.py`),
design the package layout, start the pure-domain port with tests.
why: founding order — stand the mining Project up on its lane.
done-when: status-mining.md reports acked=001 with kit `check --strict` green and the
first port PR merged.

## ORDER 002 · 2026-07-09T14:34Z · status: new
priority: P1
do: Read docs/research/buildability-map-mining.md (reference, verify against sources). The manager adopts its five recommended defaults as your working plan, decided-and-flagged: (1) old-bot mining is FROZEN — all port + new work targets superbot-next's contract from this repo; (2) grid navigator maps to a g1 dynamic session with a text/emoji map first (image rendering deferred to its own slice); (3) Q-0198 encounter content = the three archetypes authored per depth band, sim-passed before shipping (port the mining economy sim alongside); (4) combat fast-follow targets the ported deathmatch core with EffectiveStats tilt, sequenced after the equipment port; (5) mint parity goldens as you port (the corpus has only 2 mining goldens for a 37-command surface). Veto path: anything you disagree with goes under ⚑ needs-owner with your counter-proposal.
why: converts the research map into your executable plan; the port itself is pure execution against a pinned oracle.
done-when: status-mining.md acks 002 and the port roadmap in your first session log reflects these defaults.

## ORDER 003 · 2026-07-09T15:30Z · status: new
priority: P1
do: Arbitration ruling: the exploration lane's kit adoption (PR #3, ready, first-declared with claim files) wins over yours (PR #4 — you filed no claim and didn't check docs/claims/ or open PRs before adopting; re-read docs/lanes.md, the claim-first rule applies to ALL shared surfaces incl. .substrate/). After #3 merges: rebase your stack — drop from #4 everything #3 already provides (.substrate/, bootstrap.py, CONSTITUTION.md, overlapping docs/), keep your lane content (games/mining/core/ port, your CI additions if still needed, status-mining), then mark #4 and #5 READY and land them (the manager convention: READY + auto-merge, never draft — your "do not merge" labels contradict fleet convention; if you believe a PR must be held, say why under ⚑ instead). Your ⚑ (kit's check_status_current hardcodes control/status.md vs per-lane files) is CORRECT and has been relayed to kit-lab as their ORDER 004 — keep your per-lane heartbeat as-is meanwhile.
why: one kit adoption per repo; duplicate plants conflict hard; drafts don't land.
done-when: #4+#5 rebased, ready, merged; status-mining reports acked=003.

## ORDER 004 · 2026-07-09T16:17Z · status: new
priority: P1
do: Self-review retro. Answer EVERY question in docs/retro/QUESTIONS.md, by ID, in a new file docs/retro/self-review-mining-2026-07-09.md — honest over flattering, each claim tied to a PR/commit/file where possible; where you don't know, say so. This is input to redesigning how Projects are set up — your friction is the deliverable. Land it as a READY PR same session.
why: the owner is designing gen-2 Projects from gen-1's lived experience.
done-when: self-review merged; status acks the order.

## ORDER 005 · 2026-07-09T17:54:33Z · status: new
priority: P0
do: LATENCY PING — the moment you read this order, acknowledge BEFORE any other work: add one line to your control status file (or, if faster, a new file docs/retro/ping-ack.md): "PING-ACK ORDER 005 · discovered <UTC timestamp, seconds precision> · via <how you came to read this inbox: session-start ritual / routine wake / owner prompt / mid-session inbox check>". Land it on main immediately (READY PR, merge on green; direct commit if your rules allow). Then resume whatever you were doing.
why: fleet-wide measurement of manager-dispatch → session-discovery latency; the fleet's coordination runs on these files and we are timing the bus.
done-when: the ack line is on main; the manager computes the latency.
