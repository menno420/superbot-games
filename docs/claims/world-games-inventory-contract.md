# Claim — world-games inventory/resource contract (ADVISORY, design-only)

project: superbot-games (single world-games seat) · date: 2026-07-11

paths (prospective): `games/shared/inventory/**`

what: A PLAN/reference design doc, `docs/design/world-inventory-resource-contract.md`,
proposes a unified item / quantity / reward / inventory contract to live at
`games/shared/inventory/` (a claim-first shared surface per `docs/lanes.md`).

status: **ADVISORY ONLY — no code change in this PR.** This claim reserves the
prospective `games/shared/inventory/` path and signals intent; it does not touch any
shared code. The actual seam is stood up later as its own merged-on-green PR (migration
step PR-1 in the doc §4), at which point a real claim + the `control/status.md` interface
announcement (`docs/lanes.md:28-30`) apply. Delete or supersede this advisory claim when
that implementation PR opens.
