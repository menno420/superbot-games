# superbot-games — Next Tasks

> **Status:** `reference`
>
> Truth-stamped 2026-07-17 (fresh-start cleanup). Successor to the retired
> `control/` message-bus backlog (inbox/outbox). Top next steps for the games
> program when the recreated Project resumes work. Sources: the fleet recon
> digest (2026-07-17), `docs/design/`, and `docs/planning/`. Each item cites
> where its detail lives.

## Context

The four games — mining · fishing · dnd · exploration — are playable and
production-hardened (~97% coverage, sim-pinned) behind one hub
(`python3 -m games`). What remains is **content depth**, the **shared
inventory unification**, and **wiring the games into `superbot-next`** as a
game plugin. The autonomy apparatus (auto-merge bus, per-seat heartbeats,
self-arm wake routines) has been wound down — see `CONSTITUTION.md` and
`current-state.md`. Merges are **not human-gated**: a green `claude/*` PR
auto-lands via the live auto-merge apparatus once CI (`substrate-gate`) passes;
the owner reviews already-merged PRs asynchronously.

## Headline feature — D&D story game (P4)

**Ship the D&D story game P4:** build the `dungeon_master` orchestration
profile + Story Action menu toolset over the already-built, sim-pinned
deterministic quest/engine. Full design + spec:
[`planning/dnd-story-game-plan.md`](planning/dnd-story-game-plan.md) — a
complete P3→P4 plan and the single largest buildable feature. Gated only on
the one-line ⚑ Q-0040 bounded-authority owner sign-off (the plan recommends
**APPROVE**).

## Top next steps

1. **Fishing full-roster economy.** Pin + wire the ~29 unpinned legacy fish
   species (fishing ships 4 vs the original's ~21) — the biggest
   player-visible gap and the standing target of the (retired) ORDER 008
   "production-grade all games". The full-roster SIM-REQUEST content is
   captured in the retired `control/outbox.md`
   (`SIM-REQUEST · fishing-full-roster-economy`); supply the constants and
   wire them verbatim — no numbers invented until pinned.
2. **Wire `games/shared/inventory/` into mining/fishing/exploration.** The
   pure-domain foundation exists (migration PR-1) but nothing consumes it —
   build PRs 2–6 of the world-inventory-resource-contract to unify
   item / quantity / reward handling across all four games. Detail:
   `docs/design/world-inventory-resource-contract.md`.
3. **Build the rung-3 host-adapter** so these games actually run inside
   `superbot-next`, against `docs/game-plugin-contract.md`. Blocked on the
   owner packaging/hermeticity + persistence-format decisions — surface those
   as a single decision set. Detail: `docs/design/mining-host-adapter.md`.
4. **Standalone-CLI save/load persistence.** Resolve the persistence
   format-governance decision (`docs/design/persistence-design.md`) and
   implement save/load so the CLIs are replayable across sessions.
5. **Clear the 4 standing owner decisions** into `docs/decisions.md` so future
   work is unblocked without the message-bus (see below).

## Owner decisions to unblock the above

Extracted from the retired `control/outbox.md` (all ↩️ reversible replies, no
destructive click owed):

- **Q-0040** — D&D bounded-authority sign-off → unblocks the headline feature
  (plan recommends **APPROVE**).
- **D2 audit-grants ratification** — ratify (or reverse) auditing item grants
  through the mining seam (`control/outbox.md` § DECISION-NOTE · D1/D2;
  recommendation: **ratify as built**, reversal stays a one-line toggle).
- **Rung-3 packaging / hermeticity** — approve packaging sbg as an installable
  distribution → unblocks the host-adapter (item 3).
- **Persistence format-governance** (3 sub-decisions: contract-impl vs
  flat-local · field→namespace mapping · load-vs-audit rule) → unblocks
  save/load (item 4).
- **Transfer-policy source model** — true source-debit vs seeded-credit
  (`docs/design/persistence-design.md` §5).

_Deeper backlog: `docs/planning/2026-07-16-overnight-menu.md` is an unfiltered
60-idea owner-triage menu (candidates, not approved work)._

## Owner-input decisions queued (2026-07-18 overnight loop)

Surfaced by the deep hunt behind tonight's six-PR improvement loop
(#158–#163). Each is a real finding that is a **balance / design / contract
judgment call**, not a clear no-balance correctness fix — so it is an owner
decision, not an agent slice. None duplicates an entry in "Owner decisions to
unblock the above" (those are Q-0040, D2 audit-grants, rung-3 packaging,
persistence format-governance, transfer-policy). All ↩️ reversible; nothing is
blocked on a destructive click.

1. **[balance] Exploration ore-scaling still uses the retired runaway curve.**
   `games/mining/core/exploration.py::_scale_amount` (~line 272) scales ore
   gains by the pre-2026-06-22 steep curve `1 + mining_power // 2` (×5 at
   diamond) — the exact formula the sim-pinned rebalance flattened to
   `1 + power * 0.0625` (×1.5 at diamond) in `rewards.mine_multiplier` for the
   live dig faucet. The rebalance was never propagated to the (still-unwired)
   exploration engine. **Decide:** propagate the flattened curve, or
   intentionally keep exploration divergent? (Player impact only once
   exploration is on a live command path.)

2. **[design] Broken gear stays equipped and fully effective at durability 0.**
   The mining seam never clears a broken item, so a tool/light at durability 0
   keeps contributing its full `EffectiveStats` (mine multiplier, depth access,
   light radius) indefinitely — the durability sink is toothless. The equipment
   docstring says gear is "consumed on break," but no layer does it. **Decide:**
   should a break unequip the item, consume it from inventory, or block the
   action?

3. **[contract] `build_structure` trusts a caller-supplied `level` instead of
   reading state.** `services/mining_workflow.py::build_structure(state,
   structure, level)` prices and writes `state.structures[key] = level + 1` from
   the `level` **argument**, never validating it against
   `state.structures.get(key, 0)` — unlike `vault_upgrade` / `allocate_skill`,
   which read the current value from `state`. A stale/wrong `level` silently
   corrupts the stored level (downgrade / double-charge). **Decide:** tighten
   the contract to read the level from `state` (may change the established
   caller interface)?
   — ✅ **RESOLVED (2026-07-18, PR #171): owner-default applied — read the
   level from `state`.** Verified the default was ALREADY landed by #167
   (`ba78870`): `build_structure` derives `level = state.structures.get(key, 0)`,
   and `test_build_structure_uses_state_level_not_caller_claim` pins that a wrong
   `level` arg cannot change the stored-level outcome. Reversible; flagged for
   owner review.

4. **[product] dnd CLI clamps a capitalised option id to the safe default.**
   The dnd CLI treats a capitalised option id as off-menu and clamps to the
   current safe default (behaviour currently `xfail`'d in the case-normalisation
   sweep). **Decide:** case-fold option ids first, or is "capitalised stays
   safe" the intended guardrail?

5. **[product] CLIs address items/species by single-token neutral id only.**
   All game CLIs resolve items/species by a single-token neutral id; a
   multi-word display name (e.g. "Legendary Carp") honestly no-ops rather than
   resolving. **Decide:** should CLIs resolve display names → ids (a fuzzy /
   multi-token resolver), or keep the id-only contract?

6. **[UX] Mining CLI has no "Quantity must be a number" diagnostic.** Unlike the
   fishing CLI, a non-integer qty in the mining CLI folds into the multi-word
   item name and is rejected as an unknown item rather than flagged as a bad
   quantity. Adding a diagnostic is ambiguous because mining's multi-word-name
   grammar overlaps the qty slot. **Decide:** add the diagnostic, and if so,
   what grammar rule disambiguates a trailing non-int token (qty vs part of the
   name)?
   — ✅ **RESOLVED (2026-07-18, PR #172): owner-default applied — added the
   diagnostic to the `sell` path with a catalog-aware disambiguation rule.** A
   trailing non-int token is flagged "Quantity must be a number, got X" only when
   the tokens BEFORE it already name a known catalogued item (`items.lookup`) AND
   the whole phrase does not — so `sell iron abc` flags the bad quantity, while a
   genuine multi-word item name (`sell iron pickaxe`) still resolves as the item
   (no false quantity error) and a truly unknown name still reports "cannot be
   sold". `build` / `skill` fold behavior is unchanged. Reversible; flagged for
   owner review.

_Added by the 2026-07-18 overnight **fresh-angle** bug-hunt (economy-conservation
+ audit-log angles — a separate pass from the #158–#163 loop above). That hunt's
genuine auto-fixable finds already shipped as PRs #166 (quest Objective /
QuestTemplate hashable invariant) and #167 (`build_structure` caller-level
exploit); the two below are latent / design-level and need the owner's
balance / design judgment, so they are queued here rather than fixed._

7. **[balance] Cross-game fish valuation gap (latent, unreachable today).**
   `games/mining/core/items.py::register_fish_species` (~lines 282–304) folds
   each fish into the mining market as a sellable RESOURCE worth
   `max(1, size_rank)` = 1–4 coins, while
   `games/fishing/core/economy.py` (~line 35) sells the same species on the
   V043 curve at 8 / 13 / 27 / 80 — a ~20× gap. Not reachable today:
   `register_fish_species` is called only from a test, and no seam routes a
   caught fish into `MiningState.inventory`. If a future host rung ever wires
   both games onto a shared inventory, the same fish would sell for two very
   different prices. **Decide:** which valuation is canonical (or should the
   mining-market fish registration be removed)? — a balance / design call, out
   of scope for an autonomous fix.

8. **[design] `economy_audit_log` is not a complete coin ledger.** In
   `services/mining_workflow.py`, `sell` / `buy` / `repair` write audit rows
   with `target="coins"` and the coin balance in `prev_value` / `new_value`,
   but `build_structure` and `vault_upgrade` write rows whose `target` is
   `structure:<key>` / `vault` with LEVELS (not coins) — even though those ops
   also move coins (tagged `mining:*_build` / `mining:vault_upgrade`, which
   `market.py` documents as money-flow events). So reconstructing a wallet
   purely from `economy_audit_log` under-counts build / vault coin sinks
   (observed: a 500-coin vault upgrade invisible to a log-derived balance). The
   live wallet is correct; only an audit-log-derived ledger is incomplete.
   Arguably by-design (each op audits one primary target). **Decide:** is
   `economy_audit_log` meant to be a complete coin ledger (if so, build / vault
   should emit a coin-target row too), or is one-primary-target-per-op intended?
   — a design call, out of scope for an autonomous fix.
   — ✅ **RESOLVED (2026-07-18, PR #171): owner-default applied — complete coin
   ledger.** `build_structure` and `vault_upgrade` now ALSO emit a
   `target="coins"` row (same money-flow reason token, prev/new = coin balance
   before/after the sink), IN ADDITION TO the existing LEVEL row, matching the
   sell / buy / repair row shape.
   `test_economy_audit_log_coin_rows_reconstruct_the_wallet_after_build_and_vault`
   pins that a wallet rebuilt from the log's coin rows equals the live wallet.
   No balance number changed; only a structural audit row added. Reversible;
   flagged for owner review.
