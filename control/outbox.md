# game-mining · outbox — SIM-REQUEST + design-decision channel

> **Status:** `living-ledger`
>
> The games seat's **outbox**: SIM-REQUESTs (play-review findings that need an
> owner/lab balance sim) and DECISION-NOTEs (reversible design defaults flagged
> for ratification). The owner / lab **consumes** this file; the games seat is
> its sole writer (one-writer-per-file, per `control/README.md`). This is NOT a
> status heartbeat (`control/status*.md`) or an order inbox (`control/inbox*.md`)
> — it is the request/decision lane the owner named for the night run.
>
> Entries are dated and evidence-cited. No balance numbers are invented here:
> every value quoted below is copied VERBATIM from the pinned core modules.

---

## SIM-REQUEST · mining-economy-tuning · 2026-07-13

**Requested by:** games seat (rung-2 mining workflow-seam build)
**For:** owner / lab balance sim
**Status:** `open`

The rung-2 seam build ran a play-review over the pure mining core while wiring
the audited write boundary. Two economy findings surfaced that the seam
**cannot** fix without inventing balance numbers (which it does not do) — they
need an owner/lab balance sim:

- **(a) Surface lock-in / descend gate.** A fresh player equipped with only an
  iron pickaxe has `world.max_accessible_depth(stats) == 0` and therefore
  **cannot descend** off the Surface until a light/torch is equipped — depth
  access comes solely from the `depth_access` stat, which the pickaxe does not
  carry (`games/mining/core/world.py`: `max_accessible_depth` /
  `can_descend`; a torch grants `depth_access=1` → Cavern, a lantern `=2` →
  Deep, per `equipment.py` `_GEAR`). The seam correctly BLOCKS the gated
  descend (returns `ok=False`, records nothing), so the gate is enforced —
  the question is whether the *magnitude/shape* of the gate is intended.
- **(b) Source/sink gap.** The faucet is steep against the sinks: mining rolls
  a base `1–2` ore/dig (`rewards.BASE_ROLL_MAX = 2`) at surface ore values
  ~1–2 coins (`items.py` catalog: stone 1, bronze 2, iron 3) — on the order of
  ~22 coins per 8 digs — while the sinks include an iron sword at **60** coins
  (`market.GEAR_SHOP`) and a Forge I at **8 000 coins + 20 gold + 10 iron**
  … correction: **3 000 coins + 25 iron + 15 stone** for Forge I, **8 000
  coins + 20 gold + 10 iron** for Forge II (`structures._FORGE_BUILD_LADDER`).
  The gap between the passive faucet and the structure sinks looks steep.

**Ask:** run a balance sim to tune the faucet/sink magnitudes and the descend
gate. **Meanwhile every oracle-pinned value stays VERBATIM** — no numbers were
invented tonight; the seam quotes the core constants unchanged.

---

## DECISION-NOTE · D1/D2 (rung-2 audit schema) · 2026-07-13

**Raised by:** games seat (rung-2 mining workflow-seam build)
**For:** owner / lab ratification
**Status:** `flagged` (built on the sanctioned §5 default; reversible)

The seam was built on the **§5 default** of
`docs/design/mining-workflow-seam.md` (the sanctioned reversible default, not a
self-initiated contract):

- **D1 — audit schema.** Adopted the **11-field structural
  `audit.action_recorded`** schema VERBATIM as the seam's audit record
  (`services/audit.py` `AuditRecord`): `mutation_id`, `subsystem`,
  `mutation_type`, `target`, `scope`, `guild_id`, `prev_value`, `new_value`,
  `actor_id`, `actor_type`, `occurred_at`. Chosen over the 6-column
  `economy_audit_log` row because it describes item grants as naturally as coin
  moves (it is not welded to a `delta`/`new_balance`).
- **D2 — item-grant coverage (⚑ the flag).** The seam audits **every**
  state-changing action routed through it, **including item grants**
  (`mine` / `harvest`). This is a deliberate, **REVERSIBLE DIVERGENCE** from
  the oracle, whose `mine` / `harvest` write **no** audit row at all (only the
  coin legs and config/admin mutations are audited there). Flagging D2 for
  owner/lab ratification: the seam's audit coverage is a **one-line policy
  toggle** if reversed (drop the `sink.record(...)` call from the two grant
  actions). Failed / no-op actions already record nothing.

**Ask:** ratify (or reverse) D2. D1 is a clean verbatim adoption; D2 is the
contract-reach decision the scoping doc raised as the crux.

---

## SIM-REQUEST · fishing-economy-tuning · 2026-07-13

**Requested by:** games seat (rung-2 fishing workflow-seam build)
**For:** owner / lab balance sim
**Status:** `open`

The rung-2 fishing seam build (`services/fishing_workflow.py`) wired the audited
`cast` write boundary over the pure fishing core and ran a play-review while
doing so. Two economy gaps surfaced that the seam **cannot** close without
inventing balance numbers (which it does not do) — they need an owner/lab sim.
Note fishing's balance is **IN-REPO sim-pinned** (its constants are justified by
`games/fishing/sim/catch_sim.py`, whose bounds live in
`docs/design/fishing-catch-skeleton.md` §5) — it is **not** oracle-preserved. So
tuning here is a **SIM-REQUEST** (re-run the pinned sim under new targets), never
a hand-edited weight, and never a number invented at the seam:

- **(a) Empty economy — a catch grants no XP/currency.** A landed fish maps
  through the shared inventory adapter to a `Grant` whose `ProgressionDelta` is
  **empty** (`games/fishing/inventory/adapter.py` `catch_to_grant`: "Progression
  is left EMPTY: fishing's resolver defines no XP/currency for a catch today").
  The frozen `Catch` carries only `species_id` + `size`
  (`games/fishing/core/catch.py`) — there is no sell price or per-species reward.
  The seam therefore has **no sell/buy leg** to audit (unlike mining's coin
  legs): the one audited action is `cast`. **Ask:** run a balance sim to pin a
  per-species sell/reward curve (keyed on the existing `species.py`
  `size_rank` / `rarity_weight` data), so a future economy leg has sim-backed
  numbers to quote — the seam will wire it VERBATIM when it exists.
- **(b) No in-domain progression — no fishing skill/level.** Fishing has no
  progression axis of its own: there is no fishing skill branch, no level, no
  catch-count milestone (mining, by contrast, has `skills.py` branches the seam
  audits via `allocate_skill`). The gear levers `fishing_power` / `bite_luck`
  come solely from earned gear stats (`games.mining.core.equipment`), with no
  fishing-owned way to grow them. **Ask:** run a balance sim to pin a fishing
  progression curve (what a session earns toward those levers, and any per-catch
  milestone), so a later progression action has sim-backed numbers.

**Ask (summary):** run a balance sim to pin (a) a per-species sell/reward curve
and (b) a fishing progression curve. **Meanwhile every fishing constant stays
VERBATIM** — no numbers were invented tonight; the seam quotes the core
constants unchanged and audits only the one action the core actually defines.
