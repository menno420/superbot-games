# Claim · explore-verb-wiring

- **Branch:** `claude/explore-verb-wiring`
- **Scope:** Wire the mining **exploration engine** (`games/mining/core/exploration.py`,
  previously reachable only from tests) onto a live `explore` verb. Adds an
  `explore()` seam to `services/mining_workflow.py` that threads the player's
  real depth/biome (`world.biome_for_depth`) and loadout through
  `exploration.explore_from_state`, grants/debits the resolved `(item, amount)`
  into `MiningState.inventory` (clamped at zero, one audit row on a real delta,
  an honest no-op on "found nothing"), plus a `_do_explore` handler + `_ACTIONS`
  route + help line in `games/mining/cli.py`. Behavioural tests in
  `services/tests/test_mining_workflow.py` and `tests/mining/test_cli.py`; the two
  `EXPECTED_MIN_TESTS.txt` suite floors bump (`services/tests` 221→228,
  `tests/mining` 207→209) and `docs/balance.md` regenerates to match. **The
  flattened `1 + power * TOOL_POWER_GAIN` ore curve goes live via this path.**
  No new balance numbers introduced — the wiring exposes the engine's existing
  weighted outcomes.
- **Date:** 2026-07-19
- **Self-initiated:** ⚑ coordinator-decided (owner continue directive
  2026-07-19): exploration wiring GO — one contained, tested, independently-
  landable feature-wiring slice as a DRAFT PR held born-red until owner review.
