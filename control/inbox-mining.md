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
