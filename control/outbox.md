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

---

## OWNER-QUEUE · DECISION · standalone-CLI persistence (save/load) · 2026-07-13

**Raised by:** games seat (standalone-CLI polish — scoping pass, no code)
**For:** owner ratification
**Status:** `open` (no code shipped; this is a decision request)

Both standalone CLIs now drive their audited seams end to end
(`python3 -m games.mining` / `python3 -m games.fishing`), but neither can SAVE —
close the terminal and the run is gone. Save/load is the last standalone-polish
item. A scoping pass shows the blocker is **not the data shape** but **format
governance**: PR #53 just merged the canonical persistence contract, and this
seat will not silently ship a second, contract-divergent serialization on top of
it. Flagging the coupled decisions before the build, per the six-field ⚑
OWNER-ACTION grammar:

- **⚑ WHAT:** decide how session persistence (save/load) for the mining +
  fishing standalone CLIs should work — three coupled sub-decisions.
  **(1) Format ownership.** Implement PR #53's prescribed namespaced/versioned
  `PlayerState` contract (`docs/design/persistence-design.md` §2/§3/§4) in this
  repo, OR ship a CLI-local flat JSON that diverges from the just-merged
  contract — noting §1 assigns filesystem/storage to the host
  (`menno420/superbot-next`), **not** this repo, so raw CLI file I/O may not
  belong here at all (this repo owns the *contract*; the host owns the *bytes*).
  **(2) Field→namespace mapping.** The contract leaves the mapping unspecified
  for the actual state shapes: per §2 ("wealth is not double-stored") `coins` +
  `inventory` must land in the `shared-inventory` namespace, while
  `haul`/`depth`/`structures`/`seed` have **no** assigned namespace — the owner
  must place them (or ratify a `mining`/`fishing` domain-namespace home).
  **(3) load-vs-audit rule.** Confirm that `load` reconstructs state **without**
  emitting audit rows — which depends on the still-open **D2** audit-boundary
  ratification in this same file (a `load` that re-plays actions through the
  seam would forge audit history).
- **⚑ WHERE:** `services/mining_workflow.py` `MiningState` /
  `services/fishing_workflow.py` `FishingState` (the state the seams mutate);
  the contract `docs/design/persistence-design.md`; the drivers
  `games/mining/cli.py` and `games/fishing/cli.py`.
- **⚑ HOW:** the state dataclasses are cleanly JSON-serializable — plain
  `int`/`str`/`dict` plus two all-int nested dataclasses (`EnergyState`:
  `current`/`updated_at`, in `MiningState`; `EffectiveStats`, the optional stat
  block in `FishingState`) — no RNG handles, no live instances held. So the
  blocker is **format governance, not data shape**: once the owner picks
  contract-impl vs flat-local (plus the namespace mapping and the load/audit
  rule), it is a mechanical build with nothing to invent.
- **⚑ RISK:** ↩️ reversible — no code has shipped; this is a decision request,
  reversible by choosing either format before any serializer exists.
- **⚑ WHY-IT-MATTERS:** a game you cannot save is thin — but shipping a second,
  contract-divergent serialization days after PR #53 merged the canonical
  contract would **fragment** persistence into two rival on-disk formats. Owner
  governance before the build is cheaper than a later reconciliation.
- **⚑ UNBLOCKS:** save/load for both standalone CLIs — the last standalone-polish
  item.
- **⚑ VERIFIED-NEEDED:** the **D2** audit-boundary ratification (same file)
  gates sub-decision (3); the persistence-design contract is `status: plan`
  (docs-only — zero implementing `serialize`/`deserialize`/`PlayerState` code,
  grep-confirmed), so there is no in-repo serializer to reuse yet. **No balance
  number is invented here** — the state field shapes are quoted from the seams
  VERBATIM.

---

## SIM-REQUEST · dnd-escort-double-mint · 2026-07-13

**Requested by:** games seat (D&D finalization — audited `choose` seam + CLI)
**For:** owner / lab balance sim
**Status:** `open`

The D&D finalization wired the audited `choose` write boundary
(`services/dnd_workflow.py`) over the pure bounded-menu resolver and ran a
play-review while driving it. One economy finding surfaced that the seam
**cannot** resolve without inventing a balance number (which it does not do) — it
is a balance/owner call, so it is filed here rather than patched or capped:

- **Escort-bundle DOUBLE-MINT — one traversal mints `safe_passage` 2×.** The
  `escort_step` effect completes the single-objective `safe_passage` ESCORT
  bundle and mints the tier-capped reward in ONE step
  (`games/dnd/core/effects.py` `_escort_step`: `offer → accept → apply_event →
  grant_rewards`, minting `catalog.TIER_CAPS[RewardTier.I]`). But the scene
  catalog wires `escort_step` to **two** different options on a single arc
  (`games/dnd/data/scenes.py`): `advance_escort` on `waystation_road`
  (`next_scene_id="waystation_gate"`) AND `signal_escort` on `treeline_watch`
  (`next_scene_id=None`). A single traversal — `waystation_road ·
  advance_escort` (mint #1 → gate) → `waystation_gate · circle_to_treeline`
  (narrate → treeline) → `treeline_watch · signal_escort` (mint #2 → end) —
  therefore completes the `safe_passage` bundle **twice** and mints its reward
  **2×** in one escort. (The seam folds each mint honestly — the running totals
  double — and the two mints are visible as two `reward:*` audit rows.)

**Ask:** decide whether one escort completing `safe_passage` twice (and minting
2×) is intended, or whether the arc should mint the escort bundle at most once.
This is a balance/design question — a sim/owner call, NOT a seam fix. **Meanwhile
every D&D value stays VERBATIM** — no number was invented tonight; the seam folds
exactly the engine's tier-capped bundle and the two effect wirings are the
catalog's, unchanged. The seam does **not** cap the second mint (capping would be
an invented balance number).
