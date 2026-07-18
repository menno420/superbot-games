# 2026-07-18 · mining-build-level — fix(mining): build_structure derives its level from state, not the caller's claim

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus 4.x · high · runtime bugfix

⚑ Self-initiated: a DEEP bug-hunt on the game LOGIC reached via the audit-log
completeness angle (owner night order 2026-07-18 — land ONE contained, tested,
independently-landable game-improvement slice as a PR on green via auto-merge).
Reading the mining WORKFLOW seam for audit truthfulness (does every recorded
`prev_value` match reality?) surfaced that `build_structure`'s `prev_value` is
whatever integer the CALLER passed — never the structure's real stored level —
and the shipped standalone CLI (`build <structure> [level]`) forwards a
player-typed trailing integer straight into that argument. So the audit gap is
also a live player exploit. Executed at branch base `8bd5da4` (#165, main HEAD).

**The bug (real, player-reachable, verified).** `services/mining_workflow.py`
`build_structure(state, structure, level, …)` trusts the caller-supplied `level`
for THREE things at once: the cost lookup (`structures.build_cost(key, level)`),
the level write (`state.structures[key] = level + 1`), and the audit record's
`prev_value` (`str(level)`). It never reads the authoritative current level from
`state.structures` — unlike `vault_upgrade` (~line 736: `level = state.vault_level`)
and `allocate_skill`, which derive from state. `games/mining/cli.py::_do_build`
forwards a player-typed trailing integer as that `level`, so two exploits are
reachable from the shipped CLI (both reproduced before the fix):

- **Downgrade.** Forge at max level 2, player types `build forge 0` → forge is
  written DOWN to level 1 while being charged only the cheap level-0 cost, and
  the audit row records `prev='0' new='1'` (the real prior level was 2).
- **Tier-skip.** Fresh forge at level 0, player types `build forge 1` → forge
  jumps straight to level 2, never paying the level-0→1 cost, and the audit row
  records `prev='1' new='2'` (the real prior level was 0).

**The fix (surgical, mirrors `vault_upgrade`, no balance change).** Right after
normalising `key`, derive the level from state and ignore the caller's claim:
`level = state.structures.get(key, 0)`, then price / write / record from that.
The `level` parameter is kept in the signature (advisory/ignored) so no caller
breaks. With the real level driving `build_cost`, a maxed structure now returns
a clean rejected no-op (`build_cost` is `None` at max → `ok=False`, no mutation,
no audit row), a fresh forge builds exactly one tier, and the audit `prev_value`
is always the true prior level. No build cost, structure ladder, or any balance
number is touched; `target` / `mutation_type` / message strings are untouched.

Scope: one derived-level line in `services/mining_workflow.py::build_structure`
+ one new regression test (`test_build_structure_uses_state_level_not_caller_claim`
in `services/tests/test_mining_workflow.py`, fails before / passes after), plus
the corrected CLI pin (`test_build_negative_level_is_honest_noop` →
`test_build_negative_level_is_ignored_and_builds_from_state` in
`tests/mining/test_cli.py`, which had encoded the old caller-claimed-level
behaviour). `services/tests` `EXPECTED_MIN_TESTS.txt` floor 217 → 218 +
`docs/balance.md` regenerated (its Test-suite-floors section pins that count).

## 💡 Session idea

⚑ Self-initiated. The angle that found this was AUDIT-LOG COMPLETENESS, not the
player surface: instead of asking "can a player cheat?", ask "does every audit
row tell the truth about the state transition it claims?" `build_structure`'s
`prev_value = str(level)` is the one mutation-recording call in the mining seam
that sources its `prev_value` from an ARGUMENT rather than from `state` — every
sibling (`vault_upgrade`, `allocate_skill`, `ascend`, `_apply_wear`) reads the
prior value out of `state` first. That single asymmetry is both the audit lie
and the exploit: an audit row whose `prev_value` can be dictated by the caller
is, by construction, a row that can disagree with reality. The durable lesson: a
mutation seam's audit `prev_value` should be derived from the same authoritative
state the write reads — never accepted from the caller — and grepping a seam for
"which recorded field comes from a parameter" is a fast, high-yield way to find
both correctness bugs and audit-integrity gaps in one pass.

## ⟲ Previous-session review

Target: games PR #165 (`8bd5da4`, "docs: correct stale human-gated merge claim
in NEXT-TASKS") — this branch's base and main's current HEAD (`git fetch origin
main && git checkout -B … origin/main` → `8bd5da4`, confirmed; the merge commit
is titled `…(#165)` and `git log --oneline` lists #158–#165 as the eight most
recent squashes). Its load-bearing claim — that `docs/NEXT-TASKS.md` carried a
STALE "Merges are human-gated: open a PR ready and stop" line contradicting the
live state, and the fix rewrote it to "Merges are not human-gated: a green
`claude/*` PR auto-lands via the live auto-merge apparatus once CI passes; the
owner reviews already-merged PRs asynchronously" — re-checks TRUE from this
session's own reading: `docs/NEXT-TASKS.md` now reads "not human-gated … auto-
lands via the live auto-merge apparatus", matching the standing wind-down facts
the #164 truth-refresh card preserved (auto-merge apparatus LIVE, routines
un-armed pending the owner's per-seat go). #165 was docs-only and touched no
code, so this slice's edit to `build_structure` is on virgin ground relative to
it. This slice also RESOLVES the deferred finding #3 the #163
(`mining-broke-report-once`) card logged as owner-input backlog
(`build_structure` trusts caller `level`): the CLI-reachability + audit-lie angle
makes it a clear no-balance correctness fix (derive from state, exactly as
`vault_upgrade` does), not a contract-judgment call. Green baseline this HEAD:
`849 passed, 1 xfailed` (re-run this session before any edit).

## ✅ Landed (PR #pending)

Pending the born-red flip. On the flip-to-complete commit this section records
the merged PR number, the one-line fix, both commit SHAs, and the final suite
count. The first (born-red) commit carries the fix + the two tests + the
`EXPECTED_MIN_TESTS.txt` 217→218 floor bump + `docs/balance.md` regen + this card
at Status `in-progress`; `bootstrap.py check --strict` pre-flip reds SOLELY on
this card's designed born-red hold, and the flip-to-complete commit clears it so
the live auto-merge apparatus lands the squash on green.
