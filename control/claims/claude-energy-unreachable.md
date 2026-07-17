# claim · claude/energy-unreachable-target

- `claude/energy-unreachable-target` · `games/mining/core/energy.py`
  seconds_until unreachable-target fix (+ tests / floor / balance / card) ·
  2026-07-17

- **Branch:** `claude/energy-unreachable-target`
- **Scope:** `games/mining/core/energy.py` (`seconds_until` unreachable-target
  fix) + `tests/mining/test_energy_capacity.py` (regression pins) +
  `tests/mining/EXPECTED_MIN_TESTS.txt` (floor 193 → 196) +
  `docs/balance.md` (regenerated floor table) +
  `.sessions/2026-07-17-energy-unreachable.md`.
- **Slice:** ⚑ Self-initiated bugfix — `energy.seconds_until` returned `0`
  ("already reached") for a target ABOVE `max_energy`; now returns `math.inf`
  to signal the target is unreachable by passive regen.
- **Date:** 2026-07-17T23:40:59Z
- Deleted by the flip-to-complete commit on this branch (same-branch claim
  delete, per the #106–#112 precedent strict accepts).
