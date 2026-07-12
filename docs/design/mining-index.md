# Mining — design index

> **Status:** `reference`
>
> Per-domain design index for the mining lane. Linked once from
> `docs/current-state.md` so adding a mining design doc edits only THIS file, not the
> shared current-state ledger. The docs-gate reachability BFS follows the links below,
> so every doc listed here stays reachable through this index.

- [`mining-grid-encounters.md`](mining-grid-encounters.md) — grid-encounter first slice
  (loot/flavour v1), full design + sim-pin table + evidence.
- [`mining-plugin-layout.md`](mining-plugin-layout.md) — superbot-next plugin contract
  mapping for the pure mining domain port.
- [`mining-workflow-seam.md`](mining-workflow-seam.md) — rung-2 scoping doc for the
  WORKFLOW audited seam (`services/mining_workflow.py`); captures the oracle's two
  audit mechanisms and raises the ⚑ audit-schema owner/lab decision (D1 / D2).
- [`theme-readiness.md`](theme-readiness.md) — Q-0267 delta supplement to the merged
  theme-slot audit (#28): three additional player-visible mining surfaces
  (`capacity.py` warnings, `world.py` descent hints / biome tables, `skills.py` branch
  labels) classified DATA / MIXED / CODE, so the Q-0267 inventory is complete.
