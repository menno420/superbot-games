# Mining WORKFLOW audited seam — scoping (rung 2)

> **Status:** `plan` · lane: game-mining · 2026-07-12
>
> Scoping doc for **rung 2** of the mining ladder — the WORKFLOW audited seam
> (`services/mining_workflow.py`). It captures the oracle's audit pattern
> (studied from the `menno420/superbot` read-only clone on 2026-07-12), names the
> design decisions the oracle does **not** answer, and raises a **⚑ owner/lab
> decision** (D1 + D2 below) that must be ratified before the seam is built.
> This doc contains **no code** and invents **no balance numbers**. Where a
> balance constant is ever referenced it is copied verbatim from the oracle.

---

## ⚑ OWNER / LAB DECISION REQUIRED (read this first)

Two questions gate the rung-2 build. They are **not** balance numbers — they
define the mining **audit contract**, so they need an owner/lab call, not a
self-initiated default:

- **⚑ D1 — which audit schema does the sbg seam adopt?** The oracle carries
  **two** audit mechanisms (§3). The recommendation (§5) is the **11-field
  structural `audit.action_recorded`** contract, but the alternative is the
  6-column `economy_audit_log` row. One must be ratified as *the* seam record.
- **⚑ D2 — do state-changing item-grant actions get audited at all?** In the
  oracle, `mine` / `harvest` / `explore` write **no audit record** — they are
  UNAUDITED. The coordinator's done-when requires "an audit record for **every**
  state-changing action". Adopting that is a **deliberate DIVERGENCE from the
  oracle** and is the crux of the flag: it *defines* the audit contract's reach.

Everything below §5 (the concrete next slice) is **blocked on this decision.**
Until D1 + D2 are ratified, rung 2 is *scoped-and-flagged, not built.*

---

## 1. Status / provenance

This is a scoping doc for **rung 2 (the WORKFLOW audited seam)** of the mining
ladder. The ladder is three rungs, per `games/mining/__init__.py` and
`docs/design/mining-plugin-layout.md`:

```
PURE CORE  →  WORKFLOW (audited seam)  →  HOST adapter
(shipped)     (this doc scopes it)        (plugin-contract binding)
```

- **PURE CORE** — shipped: `games/mining/core/`, 19 stdlib-only modules (§2).
- **WORKFLOW (audited seam)** — rung 2, intended at `services/mining_workflow.py`,
  mirroring the oracle's `disbot/services/mining_workflow.py`: read host state →
  call core to decide → **one** transaction to commit → emit after commit.
- **HOST adapter** — rung 3, the superbot-next `SubsystemManifest` binding
  against the plugin contract now **defined and binding** at
  `menno420/superbot-next` `docs/game-plugin-contract.md@d3dba9b` (ledger D-0056,
  owner decision 2026-07-09; see PR that corrected the earlier "in flight"
  framing).

The oracle pattern below was studied from the **read-only** clone of
`menno420/superbot` on **2026-07-12**. `menno420/superbot` is never written to.

## 2. Where mining stands

- Mining's shipped surface is **PURE CORE ONLY**: `games/mining/core/` is **19
  stdlib-only modules**, purity-guarded by `tests/mining/test_purity.py`, which
  forbids the core importing `discord` / `asyncpg` / `aiohttp` / `requests` /
  `sqlalchemy` / `psycopg` and any `services.` / `cogs.` / `views.` / `utils.` /
  `disbot` prefix, and **hard-asserts exactly 19 core modules**.
- There is **no** `services/` directory, **no** DB, **no** EventBus, and **no**
  audit sink anywhere in sbg. Rung 2 is where all of that would first appear —
  outside `core/`, so the purity guard stays intact.
- The seam is **intended** at `services/mining_workflow.py` — `games/mining/__init__.py`
  names `workflow` "(named-next) the audited op seam mirroring the oracle's
  `services/mining_workflow.py`: read host state → call `core` to decide → one
  transaction to commit."
- The **smallest pure decision** a seam would wrap is
  `rewards.roll_mine_loot(*, has_pickaxe, depth=0, multiplier=None, rng=None) -> tuple[str, int]`
  (`games/mining/core/rewards.py:90`) — it reads no host state and mutates
  nothing; it just rolls `(ore_name, amount)` for one dig. That makes it the
  cleanest first thing to wrap in an audited seam.

## 3. The oracle pattern (verbatim copy-source)

The oracle has **two separate audit mechanisms**. They are not interchangeable,
and mining does **not** use the one whose name suggests it would.

### 3a. `emit_audit_action` — the config/admin structural seam (11 fields)

`disbot/services/audit_events.py:52` defines `emit_audit_action`, a shared
publisher that emits the `audit.action_recorded` EventBus event. It is the
audit seam for **config/admin** mutations (settings, logging rollout, bindings —
not economy or mining loot). Its payload is an **11-field keyword-only
contract**:

| # | field | type | how populated |
|---|---|---|---|
| 1 | `mutation_id` | `str` (UUID) | pipeline-issued UUID linking the bus event to the audit DB row |
| 2 | `subsystem` | `str` | high-level area token (`"logging"`, `"settings"`, …) |
| 3 | `mutation_type` | `str` (verb) | pipeline verb token (`"set_flag_state"`, `"upsert_binding"`, …) |
| 4 | `target` | `str` | human-resolvable id of the thing changed (`"flag:bindings.primary"`) |
| 5 | `scope` | `"global"` \| `"guild"` | string; type kept open so future scopes need no refactor |
| 6 | `guild_id` | `int` \| `None` | discord guild id, or `None` for global scope |
| 7 | `prev_value` | `str` \| `None` | string-rendered prior value, or `None` for first-time writes |
| 8 | `new_value` | `str` \| `None` | string-rendered new value, or `None` for deletes / clears |
| 9 | `actor_id` | `int` \| `None` | discord user id, or `None` for system / backfill |
| 10 | `actor_type` | `str` | capability-resolver actor-type token |
| 11 | `occurred_at` | `datetime` | ISO-8601 timestamp serialized from the DB commit `datetime`, at emit |

Two load-bearing properties:

- **Failure-safe.** If the bus raises, the exception is logged with
  `exc_info=True` and the helper returns `False`. "DB state is authoritative; a
  dropped audit event is non-fatal." Callers need not check the return.
- **Fires after commit**, never inside the transaction (the
  `economy_service.transfer` precedent).

### 3b. `economy_audit_log` — the in-txn economy money-trail (6 columns)

Mining **coin** actions do **not** call `emit_audit_action`. They write a
**6-column DB row** to `economy_audit_log`:

```
economy_audit_log (guild_id, user_id, actor_id, delta, new_balance, reason)
```

written via `economy_service.debit_in_txn` / `credit_in_txn`
(`disbot/services/economy_service.py`) — **inside** the transaction, **before**
commit. After commit, the owning workflow emits `EVT_BALANCE_CHANGED`
(`"economy.balance_changed"`) on the bus so subscribers don't block the commit.
This is mining's real money trail (market buy/sell, vault upgrade, workshop
repair — every coin leg lands a signed row here).

### 3c. KEY FINDING (state it plainly)

- **Mining's real audit is `economy_audit_log`, NOT `emit_audit_action`.** The
  structurally-rich 11-field seam never touches mining.
- **Item-grant actions are UNAUDITED in the oracle.** `mine`, `harvest`, and
  `explore` (`disbot/services/mining_workflow.py`) grant items via
  `db.update_mining_item(...)` inside the txn and fire XP award events after
  commit — but write **no audit row at all** (no `economy_audit_log` row, no
  `emit_audit_action` call). The same holds for `vault_*` grants. Only the
  **coin** legs and **config/admin** mutations are audited in the oracle.

### 3d. Seam shape (the structure to mirror)

Every oracle mining op in `disbot/services/mining_workflow.py` has the same shape:

```
read host state  →  call PURE CORE to decide (rewards.roll_mine_loot,
                     market.buy_price, …)  →  open ONE db.transaction()  →
all legs commit together  →  emit events AFTER commit  →
return a frozen dataclass result (MineResult, HarvestResult, …)
```

### 3e. Balance constants that stay VERBATIM

If the seam ever references these, they are copied byte-for-byte from the oracle,
**never re-derived**: the reason tokens (`market.BUY_REASON`, `SELL_REASON`,
`VAULT_UPGRADE_REASON`, `workshop.REPAIR_REASON`, `structure_build_reason`), the
price/cost tables, and the loot weights. **Structural** fields — the UUID,
timestamps, ids, `scope`, and `target` strings — are safe to *construct* (they
carry no balance meaning).

## 4. The design decisions the oracle does NOT answer (⚑)

The oracle gives a pattern but not a ruling for sbg. Four open decisions:

- **D1 — audit schema.** Which record does the sbg seam adopt: the **11-field**
  structural `audit.action_recorded` contract (§3a) or the **6-column**
  `economy_audit_log` row (§3b)? The two encode different things (a general
  mutation vs a signed money delta).
- **D2 — item-grant coverage.** Do state-changing item-grant actions
  (`mine` / `harvest` / `explore`) get audited **at all**? The oracle says **no**
  (§3c). The coordinator's done-when says an audit record for **every**
  state-changing action — so adopting it is a **deliberate DIVERGENCE** from the
  oracle. This is the flag that most needs sign-off: it defines the contract's
  reach.
- **D3 — timing.** In-txn-before-commit (the `economy_audit_log` discipline) vs
  event-after-commit (the `emit_audit_action` discipline)? The oracle uses each
  for its respective mechanism; sbg must pick one for its unified seam record.
- **D4 — persistence substrate.** *Where* does the record land, given sbg has
  **no** DB and **no** EventBus? There is no sink to write to yet.

## 5. Recommendation (decide-and-flag defaults — for ratification, not final)

These are **recommended** (not decided-final), precisely because they define the
audit **contract**. They are *not* balance numbers, so a recommendation is the
right altitude — but D1 + D2 still need owner/lab ratification before the build.

1. **Adopt the 11-field structural `audit.action_recorded` schema (§3a) verbatim
   as the seam's audit record.** It is cleanly specified, DB-agnostic, and
   directly copyable; unlike `economy_audit_log` it is not welded to a coin
   `delta` / `new_balance`, so it describes item grants as naturally as coin
   moves. (Resolves **⚑ D1**.)
2. **Audit *every* state-changing action routed through the seam.** This
   satisfies the done-when. It **explicitly diverges** from the oracle's
   unaudited item-grants — and *that divergence is the ⚑ that needs owner/lab
   sign-off*, because it is what defines the audit contract's reach.
   (Resolves **⚑ D2**.)
3. **Defer persistence behind an injected Sink Port.** Define a `Protocol` the
   seam calls as `sink.record(record)`. The first skeleton binds an **in-memory
   sink** for tests; real DB / bus binding is deferred to the **HOST-adapter
   rung** (rung 3), where the plugin contract's stores/events facets live.
   (Answers **D4**; **D3** collapses to "the seam calls `sink.record(...)` as the
   last step inside its logical commit, before returning the frozen result.")
4. **Seam path `services/mining_workflow.py`**, with its **own new registered
   test suite**. The purity guard stays intact because the seam lives **outside**
   `games/mining/core/` — core never imports the workflow layer.

## 6. Proposed next slice (once ⚑ ratified)

**Not built here — blocked on the ⚑ D1 + D2 decision.** When ratified, the first
slice is:

- `services/mining_workflow.py` exposing e.g. `mine(state, *, sink)` that wraps
  `rewards.roll_mine_loot`, returns a frozen `MineResult`, and calls
  `sink.record(...)` with the audit record for the grant.
- **Two tests** proving: (a) the seam emits an audit record for **every**
  state-changing action (the done-when), and (b) the core stays importable and
  pure **without** the workflow layer (the purity guard is unweakened).
- Register the new suite in `tests/EXPECTED_SUITES.txt` (add `services/tests`),
  add its `services/tests/EXPECTED_MIN_TESTS.txt`, and make **no change** to any
  existing suite floor (the new suite carries its own floor only).

## 7. Why this is a scoping doc, not a skeleton

A born-red skeleton would have to hard-code an audit record shape and decide
whether item-grants are audited — and the oracle answers **neither** (§3c). The
oracle's mining actions are audited only on their coin legs via
`economy_audit_log`, and its item grants are audited nowhere; the structural
11-field seam it *does* ship is for config/admin, not mining. Building the
skeleton now would therefore mean **inventing** the audit contract by fiat under
a born-red status — exactly the kind of self-initiated contract decision that
should instead be a ⚑ owner/lab call. So this session scopes and flags; the
build follows ratification.

---

_Ladder / provenance references: `games/mining/__init__.py`;
`docs/design/mining-plugin-layout.md`; oracle
`disbot/services/audit_events.py`, `disbot/services/economy_service.py`,
`disbot/services/mining_workflow.py` (read-only clone of `menno420/superbot`);
plugin contract `menno420/superbot-next docs/game-plugin-contract.md@d3dba9b`
(D-0056)._
