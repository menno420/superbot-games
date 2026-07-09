# game-mining · status

updated: 2026-07-09T16:45Z
phase: substrate-kit adopted + engaged (first adopter); ORDER 001 step 1 done, roadmap P0 next
health: green
last-shipped: none yet — kit-adoption PR open on branch `mining/adopt-substrate-kit`
kit: substrate-kit v1.2.0 (adopted this session; `check --strict` green)
blockers: none
orders: acked=001,002 done=
⚑ needs-owner: kit checker `check_status_current` hardcodes `control/status.md` while this
repo uses per-lane status files — kept an aggregate `control/status.md` pointer to stay
`check --strict` green; a kit-side fix (per-lane heartbeat awareness) is the durable
resolution. Also: the generic `control/inbox.md`/`control/status.md` planted by `adopt`
duplicate the per-lane bus — the manager may want to prune the generic inbox seed.
notes: |
  ORDER 001 progress:
   - step (1) adopt substrate-kit: DONE. No `.substrate/` existed, so mining is the FIRST
     adopter per docs/lanes.md ("kit adoption happens ONCE"). Adopted kit v1.2.0 via
     `bootstrap.py adopt` (bootstrap.py vendored at repo root), filled all 13 interview
     slots, `render --live`, mode=active, wired the CI gate, first session card. `check
     --strict` is GREEN.
   - step (2) read docs/founding-plan-mining.md + docs/lanes.md: DONE (binding, internalised).
   - step (3) correct control/status-mining.md: DONE (this file).
   - step (4) begin roadmap P0->P1 (oracle study of superbot disbot/utils/mining/ +
     services/mining_workflow.py, package-layout design, pure-domain port with tests):
     handed to the follow-on build worker on this lane.
  ORDER 002 (acked): the five research-map defaults are adopted as the working plan —
  (1) old-bot mining FROZEN, all work targets superbot-next's contract; (2) grid navigator
  -> g1 dynamic session, text/emoji map first (image deferred); (3) Q-0198 encounter content
  = three archetypes authored per depth band, sim-passed (port the economy sim alongside);
  (4) combat fast-follow targets the ported deathmatch core with EffectiveStats tilt, after
  the equipment port; (5) mint parity goldens as we port (corpus has only 2 mining goldens
  for a 37-command surface). No vetoes.
