# game-exploration · status
updated: 2026-07-09T16:42Z
phase: P1 shipped — deterministic quest/encounter engine live; D&D plan + survival re-baseline drafted
health: green
last-shipped: #3 — quest/encounter engine (Lane C) + v1 bounded-menu catalog + shared encounter seam + kit adoption
blockers: none
orders: acked=001,002 done=001,002
kit: substrate-kit v1.2.0 — adopted (first-mover); engagement scaffold rendered; CI gate left STAGED (not installed, cross-lane — see flag)
⚑ needs-owner: |
  (1) Q-0040 bounded-authority sign-off for the D&D story game — approve "Story Actions as the sole AI-emitted
      component; engine owns all amounts + mutation; menus hard-capped." Recommend APPROVE. This is the P3→P4 ship-gate.
      See docs/planning/dnd-story-game-plan.md.
  (2) Survival D1 re-baseline: recommend option (a) "byte-identical = today's shipped per-game energy bars; survival
      only modifies them for Medium/Hard." See docs/design/survival-d1-rebaseline.md.
  (3) Q-0087 reward caps in the catalog are conservative in-band placeholders — reconcile with superbot's real Q-0087
      constants when available (numbers are sim-pinned meanwhile).
  (4) Cross-lane CI enforcement gate (substrate-gate.yml) left STAGED under .substrate/ci/ — installing it would gate
      BOTH lanes' PRs on session-log discipline; flagged for coordination with the mining lane rather than imposed unilaterally.
notes: |
  SHARED INTERFACE ANNOUNCEMENT (docs/lanes.md): exploration defined the public shared encounter-resolution seam
  games/shared/encounter/interface.py (EncounterResolver Protocol + EncounterRequest/Outcome + EncounterTrigger:
  GRID_ROAM/EXPLORE_ACTION/CHAT_ACTIVITY) with a deterministic reference resolver. Mining owns the PRODUCTION encounter
  core and replaces the reference impl via this Protocol — coordinate before changing the interface. (Cannot write
  control/status-mining.md under the one-writer rule; announced here + flagged for the manager to relay to mining.)
  Engine is pure/seedable, 48 tests green incl. the balance-pin sim. No pay-to-win; all reward numbers sim-pinned.
