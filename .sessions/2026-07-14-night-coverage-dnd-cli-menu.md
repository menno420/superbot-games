# 2026-07-14 · night coverage — games/dnd cli + menu_sim (tests)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T01:20:18Z · night-coverage-dnd-cli-menu

Coverage slice over the dnd area as ONE unit, re-confirmed this session
at main `73111d0` (the 659-test HEAD, #113's merge) before acting:
`games/dnd/cli.py` sat at **77%** (142 stmts, 33 missed: 87, 124, 196,
265, 303–336) and `games/dnd/sim/menu_sim.py` at **77%** (94 stmts,
22 missed: 138, 193, 206–208, 215–244). The existing
`tests/dnd/test_cli.py` drives the scripted arc, the off-menu clamp,
and the read-only verbs; `tests/dnd/test_menu_sim.py` pins the
happy-path economy bounds — between them they left the capability
reward suffixes, the `help` verb, `run_commands`' default state, the
whole interactive `main()` REPL, the sim's two defensive guards, and
the whole `format_report` renderer dark.

Shipped **12 focused tests** across two new files (tests/dnd floor
bumped 43 → 55 and `docs/balance.md` regenerated in the SAME commit —
the #111 lesson): `tests/dnd/test_cli_repl.py` pins the capability
suffix in both the status and summary reward lines (present when
granted, absent when fresh), the `help`/`?` dispatch returning exactly
`help_lines()` with nothing audited, `run_commands`' fresh default
state at the start scene, and `main()` driven TTY-free via
monkeypatched `builtins.input` + capsys (banner, the two-pick arc to
`🏁`, the concluded-beat refusal NOT counting as a choice —
`choices made: 2` after three picks — plus the EOF close, exit code 0);
`tests/dnd/test_menu_report.py` trips the reward-not-seed-stable
AssertionError and the over-cap `all_within_global_max` flip via a
stubbed `_resolve_option_reward` (both guards are unreachable through
the shipped resolver, which IS seed-stable and under-cap), pins both
`_fmt_reward` branches verbatim, and renders `format_report` against a
real 2-seed run (headline, GLOBAL_MAX ceiling line, every scene section
and option row, one per-scene max line per scene, the no-pay-to-win
`True` verdict). Coverage 77% → **100%** on BOTH files (142/142 and
94/94 stmts); suite 659 → **671 passed**; `gen_balance.py --check`
green locally. Tests-only: zero gameplay-constant changes. **No latent
bug found** — the CLI counts only seam-reaching picks, the sim guards
raise/flag exactly as documented, and the renderer's copy matches its
constants. This flip commit also deletes its own claim file
(`control/claims/night-coverage-dnd-cli-menu.md`), following the
#106–#113 precedent that strict accepts the same-branch claim delete.

## 💡 Session idea

Every coverage slice of this wave has re-derived its target list by
hand: run the full suite under `--cov`, read the terminal table, paste
the missed-line ranges into the card — and the "re-confirmed at current
HEAD" step exists precisely because those numbers live nowhere in the
repo. Commit the ledger instead: a generated `docs/coverage.md`
(per-module stmts / missed / percent / missed-line ranges, emitted by a
small `tools/gen_coverage.py` from `coverage.py`'s JSON) with the same
`--check` freshness-gate shape as `gen_balance.py`, so (a) a night run
picks its next <80% rung by READING a committed table instead of a
full re-scan, (b) every test PR shows its coverage motion in the diff
itself (the reviewer sees `75% → 100%` as a hunk, not a claim), and
(c) the report's "fresh rungs at final HEAD" section becomes a repo
artifact rather than session output. Dedupe check against used card
ideas (telemetry outcome backfill; CI coverage ratchet; detector-trip
registry; display-table completeness registry; sim-harness smoke
registry; pinned-bug marker ledger; registry-derived CI pytest paths;
truth-stamp scaffold generator; guarded-rate seam + division grep-pin;
#111's shared REPL seam; #112's gate-parity `tools/preflight.py`;
#113's verb-table single source + help-parity pin): the CI coverage
RATCHET is the nearest — it enforces a non-decreasing threshold as a
gate verdict; this instead commits the full per-module coverage TABLE
as a freshness-guarded planning/review artifact (a ledger, not a
threshold). No card idea to date commits coverage data itself.

## ⟲ Previous-session review

The previous slice is A of this same night run — **#113**
(`claude/night-coverage-mining-cli`, the mining-CLI coverage card),
verified MERGED via the PR API this session: merged by
github-actions[bot] at 2026-07-14T01:14:23Z (squash `73111d0`, this
slice's baseline HEAD). Its born-red commit `678be37` held the designed
substrate-gate HOLD (gate run 29297831530 failure; tests run
29297831506 success) and its flip head `0b18581` went fully green FIRST
flip-push (gate run 29298032657, tests run 29298032653, both success) —
the #111 lesson (regenerate `docs/balance.md` with the floor bump, same
commit) held for the second slice running. Its claims re-checked
against this session's own runs rather than trusting the card:
`games/mining/cli.py` measures **100%** (179/179 stmts) under
tests/mining on this tree, matching its "75% → 100%"; its "646 → 659"
reconciles exactly with this slice's own pre-work baseline (659 at
`73111d0`) and its 13-test count with the tests/mining floor diff
164 → 177. Its claim-file self-delete held: `control/claims/` contained
no mining-cli claim when this slice started. One honest note: #113's
card cites its born-red gate HOLD from run 29297831530, which I
observed directly this session BEFORE writing that card's flip — the
same one-batch poll also closed out #112's review facts; total
CI-status polls for #113 stayed at two (born-red batch + flip batch).
