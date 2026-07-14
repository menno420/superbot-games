# 2026-07-14 · night build — refactor: single-source CLI verb tables + shared help-parity test

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T03:11:13Z · night-verb-table-help-parity

Build slice implementing the verb-table single-source idea from
`.sessions/2026-07-14-night-coverage-mining-cli.md` (verified
unimplemented at branch base `91ee62f`: no `_ACTIONS` table existed in
any CLI; mining's `_ACTION_VERBS` frozenset, `_dispatch_action`
if-ladder, and `help_lines()` were three hand-synced verb lists, and
fishing/exploration carried the same triple inline in `step()`).

All four CLIs were read first. Shipped, with minimal blast radius:

- **mining** (`games/mining/cli.py`): the ten-branch if-ladder became
  ten tiny `_do_<verb>` handlers + one `_ACTIONS` dict;
  `_ACTION_VERBS = frozenset(_ACTIONS)`. `_dispatch_action` keeps its
  exact signature and its pinned defensive None tail
  (`tests/mining/test_cli_repl.py::test_dispatch_action_returns_none_for_a_verb_off_the_table`
  still passes — the off-table behavior is now the dict's `.get` miss).
- **fishing** (`games/fishing/cli.py`): the inline sell/cast branches
  became `_do_sell` / `_do_cast` returning `StepResult`;
  `_ACTIONS = {"cast": …, "sell": …}`, `_ACTION_VERBS` derived.
- **exploration** (`games/exploration/cli.py`): offer/accept/act became
  `_do_offer` / `_do_accept` / `_do_act`; step() routes through
  `_ACTIONS.get`, `_ACTION_VERBS` derived (new — this CLI previously
  had no action frozenset at all, just the ladder).
- **dnd**: structure honestly left alone — it has NO action-verb
  surface to table-ize (every non-reserved token IS the story pick,
  and its control surface is already single-sourced as the derived
  union `_RESERVED = _QUIT | _LOOK | _STATUS | _HELP`); it gets the
  help-parity pins only.

**Byte-identity evidence**: before touching anything, scripted
transcripts were captured per game — `run_commands()` over help / a
happy-path action / an unknown command / quit with injected
`rng=random.Random(20260714)` + fixed `now`, PLUS a stdin-piped
`help\nquit\n` run of each `cli.main()`. After the refactor all eight
transcripts match byte-for-byte (identical SHA-256 per game; e.g.
mining `1ebcb112…`, fishing `faac33b4…`, dnd `4f63df55…`, exploration
`2bb76485…`).

**Help-parity tests** (8 new): `tests/<game>/test_help_parity.py` in
each registered game suite, sharing one extractor via a
`tests/conftest.py` fixture (deliberately NOT a new suite dir —
`tests/` root contains no `test_*.py`, so the floor guard discovers
nothing new). Each pins the actual relation: help names exactly
`_ACTION_VERBS ∪ documented-control` (mining, fishing, exploration —
plus `_ACTION_VERBS == frozenset(_ACTIONS)` derivation pins), and for
dnd help names exactly one spelling per reserved group ⊆ `_RESERVED`
with no group undocumented. The accepted-but-undocumented aliases
(`q`, `inventory`, `?`, `menu`, `state`, `l`) are pinned as
deliberately absent from help.

Floors (floor==collected): `tests/mining` 186→188, `tests/fishing`
119→121, `tests/dnd` 61→63, `tests/exploration` 15→17;
`docs/balance.md` regenerated BEFORE flip (gen-balance gate) and
`--check` green. Full suite **736 → 744 passed** locally; strict check
exit 0 post-flip. Claim `control/claims/night-verb-table-help-parity.md`
self-released in this flip commit (established precedent).

## 💡 Session idea

The `_ACTIONS` tables now single-source the gate+routing, but a
MALFORMED action still prints mining's generic
`"Usage — see 'help' for how to use '<verb>'."` while the real usage
string lives only in that verb's help row — two places, one truth.
Extend each `_ACTIONS` value to a small `(handler, usage)` row (or a
tiny dataclass): `help_lines()` renders the usage column FROM the
table, and the malformed-command path echoes the same row
(`Usage: sell <item> [qty]`), so per-verb usage text exists exactly
once and bad commands become self-documenting. Dedupe check against
the used-idea list: verb-table single source (this slice) unified the
verb SET, not the usage COPY; composed-narration grammar lint and
scripted-transcript golden corpus target narration/output stability,
not usage metadata; registry-to-README parity is docs-side. No card
idea to date derives help rows and usage errors from one table.

## ⟲ Previous-session review

The previous slice is this run's #124
(`claude/night-fix-gen-balance-relpath`, born-red `1b76d69`, fix
`86120e8`, flip `05cfeec`, squash-merged to main as `91ee62f` by
github-actions[bot]). Verified against live CI: at the flip SHA both
tests (run 29302477342) and substrate-gate (run 29302477340) completed
success; the born-red SHA's substrate-gate failure (run 29302299027,
tests run 29302298993 green) was exactly the designed pre-flip HOLD.
Verified against this branch's base (which includes `91ee62f`):
`tools/gen_balance.py` `check()` now wraps `relative_to(_REPO_ROOT)`
in try/except with the absolute-path fallback, and the #121 pin is
`test_check_stale_path_outside_repo_returns_1` asserting exit 1 + the
absolute path — running it locally passes, and suite count held at 736
(honest 1:1 pin replacement, no floor bump owed). One honest nit
carried forward from its own card: the fix left `check()`'s
missing-vs-stale conflation in place (a missing file still prints "is
stale" plus a full-page diff) — that follow-up is #124's session idea,
not silently absorbed here.
