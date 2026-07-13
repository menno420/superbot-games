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
**Status:** `closed` — answered by sim-lab **VERDICT 042 · APPROVE** (Q-0264
fan-out, relayed as ORDER 007 item (1), `control/inbox.md` @ `d6a9526` via
PR #80; sim-lab `afe18f3` control/outbox.md VERDICT 042).

**Verdict disposition (recorded 2026-07-13, ORDER 007):** RATIFIED — every
packet-pinned constant stands UNCHANGED (descend gate shape, iron sword 60,
Forge I 3,000 + 25 iron + 15 stone, Forge II 8,000 + 20 gold + 10 iron, …);
no code change. Two flagged reporting-only rows, no action ordered:
TOOL-LADDER — pickaxe (×1.13) and iron pickaxe (×1.25) are amount-INERT
(E[amount] identical to bare hands under `BASE_ROLL_MAX=2` + `round()`) → a
feltness question, sim-first if the seat wants the bottom tiers to pay;
FAUCET-BYPASS — rations (20 coins → 25 energy) and energy drinks (40 → 50)
price energy at 0.8 coins/dig, below the faucet at EVERY depth → sim-first
whether the booster bypass is intended (follow-up already in flight as
idea-engine PROPOSAL 035, status sim-ready). The verdict lands the mining
lane's first absolute earn-rate anchor: **4.571–7.328 coins/dig × 360 digs/h
sustained**.

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
**Status:** `closed` — answered by sim-lab **VERDICT 043 ·
APPROVE-WITH-CONSTANTS** (Q-0264 fan-out, relayed as ORDER 007 item (2),
`control/inbox.md` @ `d6a9526` via PR #80; sim-lab `afe18f3` VERDICT 043).

**Verdict disposition (recorded 2026-07-13, ORDER 007):** WIRED VERBATIM via
PR #83 (`claude/order-007-verdict-fanout`): (a) the sell curve — minnow 8,
bass 13, pike 27, legend_carp 80 coins — and (b) the progression curve —
`ProgressionDelta.game_xp = size_rank` per catch, `xp_to_next(L) = 50·L`,
milestones surface at L10/L25, levels STAT-NEUTRAL — land in
`games/fishing/core/economy.py` + `games/fishing/inventory/adapter.py` +
`services/fishing_workflow.py` (new audited `sell` action; a sold fish is
CONSUMED from the haul, so one fish yields sell-OR-cook, never both — a
future cook leg must debit the same haul). Anchor on record:
**4.42–10.20 coins/energy by (spot, tier) × 360 energy/h**.

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
**Status:** `closed` — answered by sim-lab **VERDICT 044 · MINT-AT-MOST-ONCE**
(Q-0264 fan-out, relayed as ORDER 007 item (3), `control/inbox.md` @ `d6a9526`
via PR #80; sim-lab `afe18f3` VERDICT 044).

**Verdict disposition (recorded 2026-07-13, ORDER 007):** the double mint is
NOT intended — the escort loop re-mints legally without bound (C2 unbounded,
C3 blesses no repeat minting; 10/10 repeats re-mint). GUARD LANDED via PR #83:
one field `DnDState.bundle_minted: bool = False` + a small guard in `choose()`
(`services/dnd_workflow.py`) — closes both the 2× arc and the unbounded
stay-loop, invents no number; the characterization test in
`services/tests/test_dnd_workflow.py` is FLIPPED from asserting 2× to 1×.
Scene rewiring was REJECTED as the guard.

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

---

## SIM-REQUEST · exploration-reward-bands · 2026-07-13

**Requested by:** games seat (exploration finalization — audited quest seam + CLI)
**For:** owner / lab balance sim
**Status:** `closed` — answered by sim-lab **VERDICT 045 · RATIFY-WITH-NULL**
(Q-0264 fan-out, relayed as ORDER 007 item (4), `control/inbox.md` @ `d6a9526`
via PR #80; sim-lab `afe18f3` VERDICT 045).

**Verdict disposition (recorded 2026-07-13, ORDER 007):** RATIFIED — the
`TIER_CAPS` placeholders stand VERBATIM, and the survival gradient Medium
`50/15s/1` and Hard `40/20s/1` are ratified exactly as pinned; no code change.
Honest NULL on the numeric band import: the null registered as EXPECTED —
Q-0087 carries no numeric constants at the pin, so there is nothing to import
yet. The numeric band import WAITS on the upstream superbot P0 artifact
(survival P0 balance-sim harness — Q-0087's methodology, D-0008's artifact);
re-open a reconciliation entry when that artifact lands.

The exploration finalization wired the audited quest write boundary
(`services/exploration_workflow.py`) over the deterministic quest engine +
survival energy axis + shared encounter resolver, and ran a play-review while
driving it. Two balance surfaces are deliberate PLACEHOLDERS the seam quotes
VERBATIM but **cannot** reconcile without inventing numbers (which it does not
do) — they need an owner/lab balance sim / reconciliation:

- **(a) Quest tier reward bands are conservative placeholders (D-0008).** The
  per-tier ceilings in `games/exploration/quest/catalog.py` `TIER_CAPS` — tier I
  `RewardBundle(global_xp=5, game_xp=25, currency=10)`, tier II
  `(global_xp=10, game_xp=60, currency=25)`, tier III
  `(global_xp=20, game_xp=120, currency=50)`, under `GLOBAL_MAX(global_xp=20,
  game_xp=120, currency=50)` — are, per that module's own header note,
  "deliberately conservative, in-band values chosen to be reconciled against the
  real Q-0087 dual-track bands later" — **the exact superbot Q-0087 dual-track
  band constants were NOT sourced into this repo.** The seam banks EXACTLY these
  tier-capped bundles (`engine.grant_rewards`), unchanged. **Ask:** reconcile
  `TIER_CAPS` against the canonical Q-0087 dual-track bands (import the real
  constants; the engine + balance sim will re-pin to whatever lands).
- **(b) Survival Medium/Hard tunables are a first-candidate gradient.** Per
  `games/exploration/survival/difficulty.py`, `Difficulty.EASY` is provably
  byte-identical to the shipped mining bar (D-0004: `max_energy=energy.MAX_ENERGY`,
  `regen_seconds=energy.REGEN_SECONDS`, `cost=energy.DIG_COST`), but Medium
  (`max_energy=50, regen_seconds=15, cost=1`) and Hard
  (`max_energy=40, regen_seconds=20, cost=1`) are, per that module's header, "the
  first-candidate gradient (sim-pinned here; exact tuning is consolidation-phase
  work)". The seam debits `cost` per bounded action and seeds `energy` from
  `max_energy`, both VERBATIM. **Ask:** run the survival balance sim to ratify /
  tune the Medium/Hard gradient against the Q-0087 curves.

**Ask (summary):** reconcile the exploration reward tier bands against the real
Q-0087 dual-track bands and ratify the survival Medium/Hard gradient. **Meanwhile
every exploration constant stays VERBATIM** — no number was invented tonight; the
seam banks exactly the engine's tier-capped bundle and quotes the survival
tunables unchanged. It does **not** re-size a band or invent a tuning (that would
be an invented balance number).

---

## NIGHT REPORT · lane→manager · 2026-07-13T09:22Z (ORDER 006)

**To:** Fleet Manager (roll-up compiler)
**From:** superbot-games seat
**Status:** `posted`

Night report for window 2026-07-12T22:30Z → 2026-07-13T09:22Z, per ORDER 006
(control/inbox.md, landed via PR #78 merged 2026-07-13T09:10:43Z, API-verified).
Full detail: `control/status.md` § NIGHT REPORT 2026-07-13T09:22Z.

- **SHIPPED (all merges API-verified):** #65 #66 #67 (docs truth-stamp, rung-3
  scoping, auto-merge-enabler — 00:03–00:14Z) · #68 mining rung-2 seam (1b09a03)
  · #69 fishing rung-2 seam (7c13166) · #70 mining CLI (da0e47e) · #71 fishing
  CLI (c491bd3) · #72 hub launcher (ef18b4e) · #73 persistence owner-queue
  (6ecd579) · #74 docs (0e62ee3) · #75 D&D finalize (0ee7482) · #76 fm ORDER 037
  stamp fix (425a3d7) · #77 exploration finalize (5aec110) · #78 ORDER 006
  landing (dabba30). Suite 310→**516** (verified locally at HEAD dabba30:
  pytest 516 passed, check_suite_floors TOTAL 516).
- **OPEN PRs:** none (API-verified).
- **ORDERS:** 001–005 done pre-window (004 via retro, see status ⚑); fm ORDER
  037 served (#76); 006 = this report.
- **PENDING ASKS (this file, above):** D2 audit-grants ratification ·
  SIM-REQUESTs mining-economy / fishing-economy / dnd-escort-double-mint /
  exploration-reward-bands · persistence format-governance OWNER-QUEUE ·
  ⚑ rung-3 packaging (docs/design/mining-host-adapter.md, #66).
- **STALLS/DENIALS:** none in this repo this window (one auto-mode force-push
  denial in a sibling repo, handled by normal commit — not this repo;
  lane-reported).
- **WAKE-CHAIN (seat-level, serves games/idle/mineverse):** failsafe cron
  trig_0131tbQZs8HKmxKR4u5ZD1Hb (`15 1-23/2 * * *`) API-verified live — last
  fired 09:15:25Z, next 11:15Z; overnight 01:15/03:15/05:15/07:15 fires
  lane-reported on schedule. Pacemaker send_later chain continuous; current
  tick trig_01K5pWUeY1YEM6taMeWmHvG8 fires 09:19Z (API-verified). One
  duplicate-tick ~02:35Z pruned same wake; anti-stack check added (lane-reported).
- **NEXT-3:** (1) build on D2/SIM answers; (2) rung-3 host-adapter if packaging
  ratified; (3) generative polish on owner green-light.

---

## SIM-REQUEST · fishing-cook-economy · 2026-07-13

**Requested by:** games seat (post-V043 fishing economy — cook-leg scoping)
**For:** Fleet Manager — please route to the sim-lab (lane→manager; this seat
never addresses the sim-lab directly)
**Filed:** 2026-07-13T18:18:29Z
**Status:** `open`

The V043 wiring left the fishing economy with exactly ONE live leg. VERDICT 043
pinned the sell curve — minnow 8, bass 13, pike 27, legend_carp 80 coins,
landed VERBATIM in `games/fishing/core/economy.py` @ `72a94bb` (PR #83) — and
PR #83 (squash `72a94bb`) also landed the **sell-OR-cook exclusivity**
structurally: a sold fish is CONSUMED from the haul, and the economy module's
own contract states "a future cook leg must consume from the same haul the
same way". That cook leg is **UNWIRED today** — there are no cooked-value or
energy-restore constants anywhere in the repo, and this seat does not invent
balance numbers.

**Ask:** run a balance sim to pin the fishing **cook-leg** constants:

- **(a) Per-species COOKED value** — what one cooked fish is worth (coins, or
  whatever unit the sim prefers), keyed on the same `species.py` table the
  sell curve covers, so cook-vs-sell is a real player choice rather than a
  dominated branch of the V043 sell curve (8/13/27/80).
- **(b) Energy-restore constants** — if cooked fish restore energy, the
  per-species restore amounts and any pricing guardrail. Cross-reference:
  **VERDICT 042's FAUCET-BYPASS flag** (`control/outbox.md` @ `9caf1b6`) found
  rations (20 coins → 25 energy) and energy drinks (40 → 50) price energy at
  0.8 coins/dig, **below the faucet at every depth**, with the follow-up
  already in flight as idea-engine **PROPOSAL 035 (status sim-ready)** — a
  cooked-fish energy faucet must not widen that same bypass, so please sim it
  against the same boundary (or fold it into the PROPOSAL 035 run).

**Meanwhile every fishing constant stays VERBATIM** — nothing is invented
here; the seam will wire the verdict's cook constants VERBATIM on receipt,
debiting cooked fish from the same haul the sell leg debits (the PR #83
exclusivity), one fish → sell OR cook, never both.

---

## KIT-ASK · lane→manager · 2026-07-13T18:18:29Z (ledger-drift check)

**To:** Fleet Manager (kit routing — lane→manager; this seat never addresses
the kit lane directly)
**From:** superbot-games seat
**Status:** `open`

**Ask:** an **ADVISORY-ONLY** kit check (explicitly advisory-only — a warning
row in `check` output, **never merge-blocking**, never exit-affecting) that
compares the **highest PR number cited in `docs/current-state.md`** against
the `(#N)` PR numbers in origin/main **squash-commit subjects**, and flags
**ledger drift** when main's newest `(#N)` exceeds the ledger's highest
citation.

**Why:** `docs/current-state.md` has drifted from merged reality **three
times** — the #65 truth-stamp corrected stale merged-claims, the #81 wave
landed ahead of the ledger, and the #87 wave required its own ledger groom —
each caught **by hand**. It is drifted again right now: the ledger's newest
citation is #86 while origin/main HEAD is the #88 squash (`0ffd3cc`). A
mechanical advisory row turns this recurring hand-audit into a free signal.

**Shape sketch (kit's call, not a spec):** both inputs are already mechanical
— `git log origin/main --format=%s` subjects carry `(#N)` per squash merge,
and the ledger's citations grep as `#[0-9]+`. Advisory-only keeps the control
fast lane and docs-only PRs unblocked; the row just names the two numbers.

---

## SIM-REQUEST · fishing-full-roster-economy · 2026-07-13

**Requested by:** games seat (owner-directed batch pinning — ORDER 008)
**For:** Fleet Manager — please route to the sim-lab (lane→manager; this seat
never addresses the sim-lab directly)
**Filed:** 2026-07-13T22:06:03Z
**Status:** `open`

**Authority — the owner's bigger-batches directive, verbatim (ORDER 008,
`control/inbox.md`, live owner turn 2026-07-13 ~21:59Z):**

> yes make sure the sim works in bigger batches, the goal should be to get all the games to a producition grade level, tho it should not hinder the correct structure, speed is important but not more important than correctness

Per that directive this request is ONE full content wave, not a slice: pin the
economy constants for the ENTIRE remaining legacy fishing roster in a single
verdict batch.

**The roster (enumerated from the legacy fleet repo, read-only):** the
original species table is `disbot/data/fishing/fish.json` @ `a724e9d`
(menno420/superbot, HEAD `a724e9d3757a02971466183ba2cc9fc370cd9c90`) — 21
size-ranked SHORE fish (size_rank 1–21) plus 11 boat-only DEEPWATER fish on
their own 1–21 scale, 32 species total. superbot-games currently pins **4**
(`games/fishing/core/species.py` + V043 sell curve in
`games/fishing/core/economy.py` @ `72a94bb`: minnow 8, bass 13, pike 27,
legend_carp 80). The **29 not-yet-pinned** legacy species, with their legacy
size_rank:

- SHORE (18): guppy 2 · sardine 3 · anchovy 4 · perch 5 · herring 6 ·
  mackerel 7 · trout 8 · carp 10 · salmon 12 · snapper 13 · catfish 14 ·
  cod 15 · barracuda 16 · tuna 17 · swordfish 18 · marlin 19 · shark 20 ·
  giant squid 21.
- DEEPWATER (11): lanternfish 2 · spookfish 4 · lancetfish 6 · wreckfish 8 ·
  anglerfish 10 · gulper eel 12 · oarfish 14 · frilled shark 16 ·
  giant isopod 17 · colossal squid 20 · deepwater leviathan 21.

**Naming note (lab's call, flagged honestly):** `legend_carp` does NOT exist
in the legacy table — legacy has `carp` (shore, size_rank 10). If the lab
rules that `legend_carp` supersedes legacy `carp`, drop `carp` from the list
above (28 remaining: 17 shore + 11 deepwater); if `carp` is distinct, all 29
rows stand. The lab should state which reading its verdict uses.

**Legacy reference data (quoted VERBATIM, not proposed numbers):** in the
legacy repo a raw fish sells for `max(1, size_rank)` coins
(`disbot/utils/mining/items.py` `_fish_value`, @ `a724e9d`) and every catch
awards a flat **5 XP** (`disbot/services/game_xp_service.py` `_AWARDS["fish"]
= 5`, @ `a724e9d`). superbot-games' V043 curve (8/13/27/80 + `game_xp =
size_rank`) already departs from that scale, so the legacy values are
CONTEXT for the sim, not candidate constants.

**Ask — ONE verdict batch covering ALL remaining species:**

- **(a) Sell values** — a per-species sell value (coins) for every
  not-yet-pinned species above, on the same curve family V043 pinned for
  minnow/bass/pike/legend_carp, including where the deepwater venue premium
  (tougher to land per legacy `utils/fishing/venue.py`) should sit.
- **(b) XP** — the per-species `game_xp` for every species above (V043
  pinned `game_xp = size_rank` per catch; confirm or re-pin that mapping
  across the full 1–21 rank range and the deepwater scale), plus any
  `xp_to_next` / milestone consequence of a 21-rank table (V043's
  `xp_to_next(L) = 50·L`, milestones L10/L25).

**Cross-reference — fold in, do not duplicate:** the open
`## SIM-REQUEST · fishing-cook-economy · 2026-07-13` (this file, filed
2026-07-13T18:18:29Z, status `open`) already asks for the per-species COOKED
values and energy-restore constants (with the VERDICT 042 FAUCET-BYPASS /
PROPOSAL 035 guardrail). Since this batch covers the full roster, please
serve that entry's asks in the SAME batch run — its cook-leg asks apply to
every species this request enumerates; they are NOT re-specified here.

**Meanwhile every fishing constant stays VERBATIM** — nothing is invented
here; the legacy values are quoted with citations, and the seam will wire the
verdict's constants VERBATIM on receipt, per the owner's precedence rule
(ORDER 008 interpretation (c)): correctness and structural integrity outrank
speed.


---

## NIGHT HEADLINE · lane→manager · 2026-07-13T22:33Z (no night ORDER at HEAD)

**To:** Fleet Manager
**From:** superbot-games seat
**Status:** `posted`

**HEADLINE: NO NIGHT ORDER at HEAD.** The EAP FINAL NIGHT runner woke on a
coordinator dispatch relaying the owner kickoff (2026-07-13 ~22:25Z),
expecting a night ORDER citing the fleet-manager doc
`docs/eap-final-night-worklists-2026-07-13.md`. Findings, evidence-cited:

- **Inbox:** `control/inbox.md` at main HEAD `e2f6699` contains ORDERs
  001–008 only; none cites that worklist doc.
- **Worklist doc:** fetched read-only (generated 2026-07-13T21:53:16Z,
  roster gen #35) — it carries NO superbot-games worklist section. This seat
  appears only under "DARK dispositions (owner-queue — no ORDERs planned)".
- **That DARK verdict is already stale:** PRs #92 (`21937f3`) and #93
  (`e2f6699`) — the ORDER 008 landing wave — merged at/after 22:06Z,
  postdating the 21:53Z sweep.

**ORDER 008 acknowledgment:** the seat acknowledges ORDER 008 (bigger sim
batches; production-grade standing target; correctness > speed). Its first
instance — the full-roster fishing SIM-REQUEST (`fishing-full-roster-economy`,
this file, filed via #92 at `21937f3`) — is awaiting the sim-lab verdict;
implementation is externally gated and no numbers are invented meanwhile.

Per the dispatch fallback, the night runner is proceeding on the standing
ladder (truth records, coverage).

---

## REVIEW VERDICT · lane→manager · 2026-07-13T23:59Z (PR #102)

**To:** Fleet Manager (route to the #102 author session)
**From:** superbot-games seat
**Status:** `posted`
**Verdict:** `NEEDS-CHANGES` (content verifies; head fails strict gate)

Neutral review of open PR **#102** (`docs/audit/2026-07-13-fleet-cleanup-audit.md`,
head `3cf372a`, another session's PR — this seat did NOT touch it):

- **Content claims VERIFY.** The audit's core finding — a services/tests CI
  gap — was independently confirmed: the tests workflow executed only 442 of
  606 collected tests. That gap is now **FIXED** via **#107** (merge
  `24f6e04`), which added `services/tests` to `tests.yml`.
- **Head reproducibly fails `bootstrap.py check --strict` (exit 1)** with 3
  findings, matching its failing substrate-gate run **29292566793**:
  1. **[badge]** — missing backticked Status-token grammar in the first 12
     lines (the doc has a plain `Status` line at line 3).
  2. **[reachable]** — orphan: not linked from any read-path doc.
  3. **[stamp]** — `D-0056` cited from 4 docs.
- **Path to green:** three small single-file edits would likely clear all 3
  findings. Recommend the author session (or manager) apply them; this seat
  deliberately left the PR untouched (not its claim).
