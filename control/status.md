# superbot-games · status (aggregate heartbeat)

updated: 2026-07-09T16:45Z
phase: substrate-kit v1.2.0 adopted + engaged (mining Project, first adopter); per-lane work begins
health: green
last-shipped: none yet — kit-adoption PR open (mining/adopt-substrate-kit)
blockers: none
orders: acked= done=
⚑ needs-owner: the substrate-kit heartbeat checker (`check_status_current`) hardcodes
`control/status.md`, but this repo's multi-Project extension (control/README.md) uses
per-lane status files. Kept this file as an aggregate pointer so `check --strict` stays
green; flagged for a kit-side follow-up (teach the checker per-lane awareness).
notes: SOURCE OF TRUTH is the per-lane status files, one writer each —
`control/status-mining.md` (mining Project) and `control/status-exploration.md`
(exploration Project). This aggregate exists only to satisfy the kit's single-file
heartbeat check; refresh it opportunistically at session close. The generic
`control/inbox.md` planted by adopt is unused — real orders live in the per-lane
`control/inbox-*.md` files (manager-owned).
