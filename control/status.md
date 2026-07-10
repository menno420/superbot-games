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
