# 2026-07-14 · night test — pin tools/gen_balance: generation, sections, helpers, stale detection

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T02:34:09Z · night-cover-gen-balance

Test slice. Provenance stated honestly: this partially implements the
"gen_balance generator pins" card idea from #120's session card
(`.sessions/2026-07-14-night-truth-stamp-anchor.md`) — not novel scope
invented here. Verified unimplemented at main `51590c6`: no test
imports `gen_balance`; `tools/gen_balance.py` sits at 227 statements /
0% coverage while its `--check` step in `.github/workflows/tests.yml`
gates every merge, so a regression in the generator itself (a crash, a
non-deterministic render, a broken diff path) would today surface only
as an opaque CI failure with no unit pin naming the seam.

Plan: `tests/tools/test_gen_balance.py` in the already-registered
`tests/tools/` suite (no new suite registration, no overlapping-suite
trap): run generation in-memory and to tmp paths, assert `check()`
returns 0 against the committed `docs/balance.md` at HEAD, assert every
expected section header is present in document order, pin the `_num` /
`_table` / `_read_floor` helpers, and pin stale detection (mutated copy
→ `check()` == 1 + unified diff + "stale" message). ≤14 tests; floor
bump to collected + `docs/balance.md` regen before flip (gen-balance
gate).
