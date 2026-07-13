# 2026-07-14 · night coverage — pin the set-aware Equip Best picker (tests)

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-13T22:48:34Z · night-coverage-mining-loadout

Coverage slice under the ORDER 008(b) production-grade standing directive:
`games/mining/core/loadout.py` — the "Equip Best" picker behind the Gear
panel button — sits at **28% coverage with zero direct tests**, the worst
meaningful number among core engine modules in the 2026-07-13 scope scan
(`pytest --cov`, 556 tests, main `511fa91`). Yet it carries the subtlest
behavior in the gear model: a complete same-tier set (set bonus included)
can beat the naive strongest-piece-per-slot greedy, and the module's whole
reason to exist is choosing correctly between those two candidates.

Plan: add `tests/mining/test_loadout.py` (~10 focused tests) pinning, at
the EXISTING gear constants: empty/zero-qty/unequippable inventories, the
greedy per-slot pick, set-beats-greedy and greedy-beats-set crossovers,
non-set slots preserved alongside a set candidate, multi-tier set choice,
and case-insensitivity. Tests-only — no gameplay constants change, no new
features, nothing needing a sim-lab verdict.
