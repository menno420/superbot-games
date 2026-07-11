# 2026-07-11 · D&D DM-clamp fuzz suite + model addendum

> **Status:** `red`
>
> 📊 Model: Opus 4.8 · 2026-07-11T17:42:18Z · D&D DM-clamp fuzz suite + model addendum

## Goal

Turn the bounded-menu **DM-clamp law** (design §4.4) from "asserted by a handful of
curated example tests" into a **fuzz-proven property**, and record the production DM-model
decision in the design doc. Two deliverables, no product-code change:

1. **`tests/dnd/test_resolver_fuzz.py`** — a deterministic, seeded (`random.Random(1234)`,
   zero new deps — CI installs only pytest, no `hypothesis`) property-fuzzer that hammers
   `games.dnd.core.resolver.resolve` with **hundreds of adversarial / malformed DM
   outputs** and asserts, for every single case, the same invariant: resolve() **never
   raises**, and every off-menu / hallucinated / wrong-typed / injection-shaped output
   **clamps to the scene's no-op default** (chosen == `default_option_id`, reward `None`,
   event `None`, flavour length-capped ≤ `FLAVOR_CAP` and control-char sanitized).
2. **`docs/design/dnd-story-design.md` §9** — the production DM is a **Claude Haiku-class**
   model (Haiku 4.5), safe precisely because the bounded-menu contract makes the DM a
   ≤4-button classifier whose worst case is the (now fuzz-proven) no-op clamp; plus
   prompt-budget guidance (short scene prose + enumerated option ids/labels only).

## Plan

- Born-red card first; commit the fuzz suite + doc addendum + floor bump; flip to complete
  only once the code is green and pushed.
- Bump `tests/dnd/EXPECTED_MIN_TESTS.txt` by the number of new test functions (4).
- Verify: `tests/dnd/` green, `check_suite_floors.py` exit 0, full `tests/` +
  `games/exploration/tests/` green, `bootstrap.py check --strict` exit 0.

## 💡 Session idea

The clamp is a *classifier's* safety envelope: because the DM's entire authority is one id
from an enumerated ≤4-button set and every off-set answer is a deterministic no-op, the
resolver is exactly the kind of narrow choke point a **seeded property-fuzzer** can pin
_exhaustively_ rather than by example — hundreds of adversarial inputs, one invariant, sub-
second and reproducible. This is a reusable shape for every future scene and every future
game lane with a "pick-one-from-a-bounded-menu" seam: pair the curated example tests with a
seeded fuzzer that enumerates the whole catalog (so new scenes are auto-covered) and asserts
"never raises / always clamps to the no-op". The fuzzer also *doubled as a contract probe* —
it confirmed the only remaining raise path is a `DMChoice` hand-built with an **unhashable**
`option_id` (a host-side construction bug, not a DM-deserialized input), a clean follow-up.

## ⟲ Previous-session review

The D&D walking skeleton (#38 design, then the one-scene code PR) shipped the clamp with a
DM-clamp example test as its headline safety pin. This session honours the same discipline
the fishing/survival skeletons established — **a born-red card that flips to `complete` only
when the code lands** — and *extends* the skeleton's safety story rather than re-litigating
it: the example tests stay, and the seeded fuzzer is layered on top to prove the invariant
across hundreds of adversarial inputs instead of a curated handful. It touches none of the
shipped product code (resolver / models / effects / scenes unchanged) — additive test +
doc only — and rebases cleanly on the per-suite `EXPECTED_MIN_TESTS.txt` floor mechanism
(open PR #50 bumps the same file; a trivial floor rebase if it merges first).
