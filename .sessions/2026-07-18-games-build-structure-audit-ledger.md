# 2026-07-18 · games-build-structure-audit-ledger — fix(mining): build_structure derives level from state + complete coin ledger in economy_audit_log

> **Status:** `complete`
>
> 📊 Model: Claude Opus 4.x · high · runtime bugfix

⚑ Owner-authorized code slice (menno420, live 2026-07-18): resolve TWO queued
owner-input decisions from `docs/NEXT-TASKS.md` in one small, tested,
autonomous PR, applying each decision's stated default and FLAGGING it in the PR
body for the owner's asynchronous review. Both changes live in
`services/mining_workflow.py`; both are reversible. Executed at branch base
`1039e8a` (#170, main HEAD).

**What this slice ships (both verified on main before citing).**

- **Decision #3 [contract] — `build_structure` derives level from state.**
  `build_structure(state, structure, level)` must price / write / audit off the
  authoritative current level from `state.structures.get(key, 0)` (like
  `vault_upgrade` reads `state.vault_level` and `allocate_skill` reads
  `state.skills`), never the caller-typed `level` argument — else a stale / wrong
  `level` corrupts the stored level or double-charges. Verified this is ALREADY
  LANDED on main by **#167** (`ba78870`, "build_structure derives its level from
  state, not the caller's claim") — the line `level = state.structures.get(key,
  0)` is present, and the regression test
  `test_build_structure_uses_state_level_not_caller_claim`
  (`services/tests/test_mining_workflow.py`) already asserts a wrong `level` arg
  cannot change the stored-level outcome (a maxed forge is a clean no-op; a fresh
  forge builds one tier from level 0 with `prev_value "0"`). This PR therefore
  marks decision #3 **resolved (default already applied by #167)** in
  `docs/NEXT-TASKS.md` and flags it; no re-implementation, and the existing test
  is extended to keep asserting the state-derived outcome after the #8 row change.

- **Decision #8 [design] — complete the coin ledger in `economy_audit_log`.**
  `sell` / `buy` / `repair` write a `target="coins"` audit row (prev/new = coin
  balance), but `build_structure` / `vault_upgrade` wrote only a
  `structure:<key>` / `vault` LEVEL row — so a wallet reconstructed purely from
  the audit log's coin rows under-counted build / vault coin sinks (a 500-coin
  vault upgrade was invisible to a log-derived balance). Default applied:
  `build_structure` and `vault_upgrade` now ALSO emit a `target="coins"` row
  (same money-flow reason token — `market.structure_build_reason(key)` /
  `market.VAULT_UPGRADE_REASON`, which `market.py` documents as
  `economy_audit_log` money-flow events — with `prev_value` / `new_value` = the
  coin balance before / after the sink), IN ADDITION TO the existing level row.
  The level row stays the primary `result.record` (index 0); the coin row is
  appended. No balance NUMBER changes — only a structural audit row is added.

**Tests.** New `test_economy_audit_log_coin_rows_reconstruct_the_wallet_after_
build_and_vault` asserts a wallet rebuilt from the log's `target="coins"` rows
equals the live wallet after a build and a vault upgrade. The
records-per-action invariants are updated for the now-two-row build / vault ops
(seam parametrized test + the mining CLI / repl committed-build count asserts),
and the `records[-1]` level-value assertions now select the structure row
explicitly (the coin row is last). `services/tests` floor bumped by the one new
test; no balance / economy number touched.

## 💡 Session idea

⚑ Self-initiated. When an audit log doubles as an economy ledger, "one primary
target per op" and "the log is a complete coin ledger" are in tension: the fix
is not to RETYPE the primary row but to ADD a second, coins-targeted row so the
level row and the wallet row coexist — the ledger becomes reconstructable
without losing the level history. The reusable move: a coin-sink op should emit
BOTH the domain row (what changed) and the money row (what it cost), on the same
reason token, so any downstream consumer (level history OR wallet replay) reads
a complete trace.

## ⟲ Previous-session review

The 2026-07-18 fresh-angle bug-hunt (card `2026-07-18-queue-bughunt-ownerinput`,
PR #168) is what QUEUED both decisions this slice resolves: it shipped the
auto-fixable finds as PRs (#166 quest-hashable, #167 `build_structure`
caller-level exploit) and parked the two design / contract residue items (#3
now confirmed already closed by #167, #8 the coin-ledger completeness call) in
`docs/NEXT-TASKS.md` for owner judgment. This slice is the owner-authorized
follow-through: apply both stated defaults, flag them, land on green. Green
baseline at branch base `1039e8a`: `852 passed, 1 xfailed`
(`python3 -m pytest -q`, re-confirmed this session before editing).

## ✅ Landed (PR #171)

Shipped in PR [#171](https://github.com/menno420/superbot-games/pull/171)
(`claude/games-build-structure-audit-ledger`), plus this card:

- `services/mining_workflow.py` — `build_structure` and `vault_upgrade` now emit
  a second `target="coins"` audit row (same money-flow reason token, prev/new =
  coin balance before/after the sink) alongside the existing LEVEL row (decision
  #8). The LEVEL row stays the primary `result.record` at index 0.
- Tests — new
  `test_economy_audit_log_coin_rows_reconstruct_the_wallet_after_build_and_vault`
  (`services/tests/test_mining_workflow.py`); the seam's per-action record-count
  test and the mining CLI / repl committed-build count asserts updated for the
  now-two-row build / vault ops; `records[-1]` level assertions select the
  structure row. `services/tests` floor 218 → 219; `docs/balance.md` regenerated.
- `docs/NEXT-TASKS.md` — decisions #3 (verified already landed by #167) and #8
  marked ✅ RESOLVED with the applied owner-default + PR link; the other queued
  items left untouched.

**Suite green:** `python3 -m pytest -q` = `853 passed, 1 xfailed` (+1 from the
new test). **`bootstrap.py check --strict`** pre-flip = the designed born-red
hold; this flip-to-complete commit clears it so the gate goes green and the live
auto-merge apparatus lands the squash. No balance / economy number changed.
