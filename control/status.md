# superbot-games · status (pointer)

updated: 2026-07-09T20:15Z

This repo uses lane-specific status files per the fleet protocol:
`control/status-exploration.md` and `control/status-mining.md`
(see `docs/lanes.md` and `control/README.md`). This generic file is a pointer only.

## Gen-1 wind-down (2026-07-09)
Both resident Projects are executing the owner's gen-1 → gen-2 succession.
- mining lane: WIND-DOWN COMPLETE — see `control/status-mining.md` + PR #14 succession package.
- exploration lane: winding down — see `control/status-exploration.md` + PR #13.
Each lane writes only its own status file (one-writer-per-file); this pointer is edited additively.

## Mining heartbeat (2026-07-10)
- **timestamp:** 2026-07-10 · **phase:** gen-1 mining complete · **health:** green (main strict-GREEN; 73 mining tests pass; `bootstrap.py check --strict` exit 0).
- **routine:** NOT ARMED — webhook/owner-driven (no scheduler tool this session; no timed self-wake scheduled).
- **orders:** 001, 004 DONE · 002, 003 ACKED · 005 historical/stale · gen-1 close-out DONE. All mining PRs (#5, #11, #14, #15) MERGED; none open.
- **⚑ asks:** none new. Standing owner-only item unchanged: the aggregate `control/status.md` two-writer question (kit hardcodes one status file vs this repo's per-lane files) — see `control/status-mining.md`.
- Detail: `control/status-mining.md`. Gen-2 boot: `docs/retro/next-boot-mining-2026-07-09.md`.
