# 2026-07-14 · night coverage — games/mining/cli.py (tests)

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T01:07:58Z · night-coverage-mining-cli

Coverage slice, re-confirmed this session at main `6de5666` (the
646-test HEAD, #112's merge) before acting: `games/mining/cli.py` sat
at **75%** (179 stmts, 44 missed: 82–85, 88–90, 189, 193, 199, 207,
212, 215–220, 224, 226, 276, 321, 355–380). The existing
`tests/mining/test_cli.py` drives scripted sessions through
`run_commands` (economy legs, blocked actions, help/quit ergonomics)
but left the status gear-line fallback branches, the
harvest/ascend/build dispatch legs, the malformed-command usage paths,
`run_commands`' default state, and the whole interactive `main()` REPL
dark.

Shipped **13 focused tests** in `tests/mining/test_cli_repl.py`
(tests/mining floor bumped 164 → 177 and `docs/balance.md` regenerated
in the SAME commit — the #111 lesson applied preemptively): the
gear-line durability-without-cap and no-durability-entry fallbacks plus
the equipped-light suffix (with and without tracked durability);
harvest committing wood with one audit row; the at-Surface ascend
block; build with an explicit level, with the default level read from
`state.structures`, and a funded build committing at the seam's
verbatim `structures.build_cost` (coins to 0, campfire → level 1, one
audit row); the five argless usage paths (sell/buy/repair/build/skill);
`_dispatch_action`'s off-table None tail; `run_commands`' fresh default
player; and `main()` driven TTY-free via monkeypatched `builtins.input`
+ capsys (banner, committed-action counter, quit and EOF closes, exit
code 0). Module coverage 75% → **100%** (179/179 stmts); suite
646 → **659 passed**; `gen_balance.py --check` green locally.
Tests-only: zero gameplay-constant changes, every asserted string an
existing seam/core constant. **No latent bug found** — every blocked
action returns the seam's honest message without recording, and both
REPL close paths print the full summary. This flip commit also deletes
its own claim file (`control/claims/night-coverage-mining-cli.md`),
following the #106–#112 precedent that strict accepts the same-branch
claim delete.

## 💡 Session idea

Pinning line 226 (`_dispatch_action`'s defensive None tail) exposed
that every game CLI keeps THREE hand-synced enumerations of its verbs:
the `_ACTION_VERBS` frozenset (step's gate), the if-ladder in
`_dispatch_action` (the routing), and the `help_lines()` text (the
player contract). They can drift silently: add a verb to
`_ACTION_VERBS` but forget the ladder and the CLI prints a misleading
"Usage" for a well-formed command; forget `help_lines()` and the verb
is undiscoverable. Collapse to ONE source: a module-level dispatch
TABLE (`_ACTIONS: dict[str, handler]`) from which
`_ACTION_VERBS = frozenset(_ACTIONS)` is derived by construction, plus
one shared parity test (`tests/shared/`) that walks every game CLI and
asserts its help text names exactly its action-verb set — so the
gate/route/help triple cannot drift in any CLI again. Dedupe check
against used card ideas (telemetry outcome backfill; CI coverage
ratchet; detector-trip registry; display-table completeness registry;
sim-harness smoke registry; pinned-bug marker ledger; registry-derived
CI pytest paths; truth-stamp scaffold generator; guarded-rate seam +
division grep-pin; #111's shared REPL seam; #112's gate-parity
`tools/preflight.py`): the REPL seam unifies the input LOOP mechanics,
this unifies the verb DISPATCH surface and its help contract —
different seam, and no card idea to date touches verb-table/help
parity.

## ⟲ Previous-session review

The previous slice is B of the prior night run — **#112**
(`claude/night-coverage-mining-items`, head `ae7cb4d`), verified MERGED
via the PR API this session: merged by github-actions[bot] at
2026-07-14T00:34:30Z (squash `6de5666`, this session's baseline HEAD).
Its born-red commit `891a322` held the designed substrate-gate HOLD
(gate run 29295938766 failure; tests run 29295938763 success) and its
flip head `ae7cb4d` went fully green (gate run 29296270104, tests run
29296270069, both success) — green FIRST flip-push, unlike #111,
because it regenerated `docs/balance.md` alongside its floor bump
before pushing. Its claims re-checked against this session's own runs
rather than trusting the card: `games/mining/core/items.py` measures
**100%** (79/79 stmts) under tests/mining today, matching its
"76% → 100%"; its "618 → 632 on this branch" reconciles with today's
646-test main baseline (618 + 14 hub tests from #111 + 14 items tests
from #112 = 646, which is exactly what my pre-slice run collected). Its
claim-file self-delete held: `control/claims/` contained only README.md
at this session's start. One honest note: #112's card wrote its review
of #111 while `031f763`'s CI was still in flight and explicitly
declined to claim #111 green — that verification is now closable:
#111's fix head `031f763` finished green (gate run 29296068505, tests
run 29296068498) and #111 merged as `0efb7ac`.
