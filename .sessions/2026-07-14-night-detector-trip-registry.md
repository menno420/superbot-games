# 2026-07-14 · night test — detector-trip registry: every sim invariant predicate has a proven violation witness

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T02:40:40Z · night-detector-trip-registry

Test slice implementing the detector-trip registry card idea from
`.sessions/2026-07-14-night-coverage-economy-sim.md`, verified
unimplemented at main `fefe16c`: no registry module exists;
`tests/shared/sim/test_economy_sim.py` (#99) constructs violations for
economy_sim's three named invariants individually, but nothing
ENUMERATES the invariant predicates across all sims or structurally
REQUIRES a False-returning violation witness per predicate — so a new
predicate that can never trip (dead detector) would land green today.

Plan: `tests/shared/sim/test_detector_trips.py` in the registered
`tests/shared/sim/` suite. Enumerate bool-returning module-level
predicates FROM the sim modules themselves (functions defined in the
module whose return annotation is `bool` — derived, not hand-listed);
keep a witness registry mapping each enumerated predicate to a
constructed violating input (dataclasses.replace / targeted
monkeypatch, no shipped constant edited); assert registry keys ==
enumerated predicate set both ways; assert each witness makes its
predicate return False (and the shipped state keeps it True). ≤12
tests; floor bump to collected + `docs/balance.md` regen before flip
(gen-balance gate).
