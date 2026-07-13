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
