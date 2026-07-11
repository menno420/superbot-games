# Exploration — design index

> **Status:** `reference`
>
> Per-domain design index for the exploration lane. Linked once from
> `docs/current-state.md` so adding an exploration design doc edits only THIS file,
> not the shared current-state ledger. The docs-gate reachability BFS follows the
> links below, so every doc listed here stays reachable through this index.

- [`quest-encounter-engine.md`](quest-encounter-engine.md) — shipped v1 deterministic
  quest/encounter core + v1 bounded-menu catalog + shared encounter interface.
- [`survival-d1-rebaseline.md`](survival-d1-rebaseline.md) — resolves the factual
  contradiction in the survival plan's D1 baseline (D-0004).
- [`survival-sim-harness.md`](survival-sim-harness.md) — survival P2 sim harness: a pure
  deterministic sim driving the shipped mining energy engine per difficulty; pins the
  Q-0087 casual/grinder/gap curves as tests (Easy byte-identical to shipped bars per
  D-0004, Medium/Hard sim-pinned gradient).
