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
