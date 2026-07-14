# 2026-07-14 · night coverage — games/mining/core/items.py (tests)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T00:26:10Z · night-coverage-mining-items

Coverage slice, re-confirmed this session at main `a51c5d5` (the 618-test
HEAD; re-measured with slice A's 14 hub tests present — the numbers were
unchanged) before acting: `games/mining/core/items.py` sat at **76%**
(79 stmts, 19 missed: 340, 344, 355–356, 367, 381, 391–406, 419–427).
The existing suites exercise the catalog itself (lookup, classify, the
fish injection point, the set-family rows) but left the helper layer
dark.

Shipped **14 focused tests** in `tests/mining/test_items_display.py`
(tests/mining floor bumped 103 → 164 in the same commit, and
`docs/balance.md` regenerated in a follow-up commit — see the review
below for why): the `is_tool` / `is_consumable` predicates (incl.
catalog case-insensitivity), `tool_tier` with its unknown → 0 guard,
`total_value` (value × qty sum, zero/negative quantities skipped,
unknown items at the documented default 1), `next_tool_upgrade`'s
off-every-ladder None tail, `sort_inventory` (kind order
resources→tools→consumables→structures→treasure, value-desc then
name-asc tiebreak, zero-qty rows dropped), and `summarize_inventory`
(one section per kind in display order, empty → no sections). Module
coverage 76% → **100%** (79/79 stmts); suite 618 → **632 passed** on
this branch. Tests-only: zero gameplay-constant changes, every asserted
number an existing catalog constant. **No latent bug found** — the
display helpers behave exactly as their docstrings promise on every
edge tried. This flip commit also deletes its own claim file
(`control/claims/night-coverage-mining-items.md`), following the
#106/#107/#109/#110 precedent that strict accepts the same-branch claim
delete.

## 💡 Session idea

Slice A of this run went red on a gate no local check covered: the
tests workflow runs `tools/gen_balance.py --check` after pytest, and a
suite-floor bump makes the committed `docs/balance.md` stale — a trip
you only discover post-push, one CI round-trip per newly-met gate.
Extract a gate-parity preflight: `tools/preflight.py` that runs, in
order, exactly the gates the tests workflow runs (floor guard →
pytest → `gen_balance.py --check`), and refactor
`.github/workflows/tests.yml` to invoke that same script — so the
workflow and the local check cannot drift apart by construction, and a
slice runs ONE command locally to know it will be green. Dedupe check
against used card ideas (telemetry outcome backfill; CI coverage
ratchet; detector-trip registry; display-table completeness registry;
sim-harness smoke registry; pinned-bug marker ledger; registry-derived
CI pytest paths; truth-stamp scaffold generator; guarded-rate seam +
division grep-pin; slice A's shared-REPL seam): registry-derived CI
pytest paths is the nearest — it derives one workflow ARG from a
registry; this instead makes the whole gate SEQUENCE a single shared
executable that CI itself runs. No card idea to date does that.

## ⟲ Previous-session review

The previous slice is A of this same night run — **#111**
(`claude/night-coverage-games-hub`, the games-hub loop coverage card),
reviewed honestly: it was **not green first push**. Its born-red commit
`a6487b6` held the designed substrate-gate HOLD (run 29295636342
failure; tests run 29295636328 success). Its flip push (`25a84b4` tests
+ `79dea5d` flip) went half-green: substrate-gate run 29295826223
success, but tests run 29295826252 **failure** — not the pytest suite
(632 passed in that very log, floor table green at services/tests
178/178) but the downstream `tools/gen_balance.py --check` step:
`docs/balance.md` embeds the per-suite floor table, so the 164 → 178
floor bump left the committed page stale ("ERROR: docs/balance.md is
stale — regenerate"). A real miss in slice A's local verification (it
ran the floor guard and the suite, not the balance freshness gate); the
one-push fix `031f763` regenerates the page and was pushed with strict
exit 0 locally. Its coverage claims re-checked from this session's own
runs: `games/__main__.py` 72% → 100% and 618 → 632 both reproduce. At
the time this flip was written, `031f763`'s CI was still in flight —
this card does not claim #111 green or merged; that verification
belongs to the next card.
