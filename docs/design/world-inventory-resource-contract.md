# World inventory / resource contract — unified item · quantity · reward · inventory

> **Status:** `plan` · 2026-07-11
>
> A PLAN/reference doc (not an implementation). The world games each grew their own
> shape for "an item", "an amount", "a reward", and "inventory" — four incompatible
> vocabularies that already have to interoperate (fishing lands fish into mining's
> inventory; encounters hand back rewards; quests grant progression). This doc reads
> the ACTUAL current representations out of the code, shows where they disagree, and
> proposes ONE pure-domain contract (frozen dataclasses + Protocols, plugin-package
> friendly, Q-0267 nouns-in-data) that lives at `games/shared/inventory/` and is
> adopted per-system by a thin adapter — extend, never duplicate. Companion to
> `docs/design/mining-grid-encounters.md` (the `Reward`/`EncounterOutcome` shape),
> `docs/design/fishing-catch-skeleton.md` (the `Catch`/neutral-id shape),
> `games/exploration/quest/README.md` (the `RewardBundle` shape), and
> `games/shared/encounter/README.md` (the claim-first shared-seam precedent this doc
> mirrors). Advisory claim: `docs/claims/world-games-inventory-contract.md`.

---

## 1. Problem

Four systems, four vocabularies. Every "current representation" below is quoted from
code read this session, with file:line citations. Nothing here is invented.

### 1a. What each system calls an ITEM

- **Mining** — an item is a **lowercased display string** that doubles as the catalog
  key, the inventory key, *and* the player-facing noun. `_CATALOG` is keyed on
  `name.lower()` (`games/mining/core/items.py:66`, `:327` `lookup` lowercases), and the
  rows literally are the nouns: `"diamond"`, `"iron"`, `"lucky charm"`, `"stone hut"`
  (`items.py:70-224`). The mechanic key *is* the theme noun — this **violates Q-0267**
  (nouns should live in data, not be the code key).
- **Fishing** — an item (a caught fish) is a **neutral `species_id`** with the nouns in
  a data table: `Catch(species_id: str, size: int)` (`games/fishing/core/catch.py:90-95`)
  where `species_id` is `"minnow"`/`"bass"`/`"pike"`/`"legend_carp"` and every visible
  noun (`name`/`emoji`/`flavor`) lives in `games/fishing/core/species.py:46-79`. This is
  the **Q-0267-correct** shape — and it is *incompatible* with mining's string keys.
- **Exploration/quest** — has **no item concept at all**. A quest reward is XP + currency
  + an optional `capability: Optional[str]` (`games/exploration/quest/models.py:56-63`);
  the only string identity is the capability name.
- **Shared/encounter** — an item is **not modelled**; the outcome carries an untyped
  `payload: Mapping[str, object]` (`games/shared/encounter/interface.py:38-45`) and the
  reference resolver fills it with `{"trigger": ..., "intensity": int}`
  (`games/shared/encounter/reference.py:44-47`) — no item/amount structure.

**The fish→mining bridge already loses the neutral id.** `register_fish_species`
folds fishing species into the mining catalog keyed on `s.name` — the *display* name,
not the neutral `species_id` (`games/mining/core/items.py:282-304`). So a fish that was
`species_id="legend_carp"` in fishing becomes inventory key `"Legendary Carp"` in
mining. The one place the two systems already touch is exactly where the identity model
breaks.

### 1b. What each system calls a QUANTITY / STACK

- **Mining** — a plain `int` amount, and inventories are bare `dict[str, int]` /
  `Mapping[str, int]` of `{item_name: qty}` (`items.py:365` `total_value`,
  `capacity.py:40` `distinct_types(store: Mapping[str, int])`). There is **no typed
  stack** — just a dict entry.
- **Fishing** — a catch has **no count**; it has `size: int`, a per-instance *magnitude*
  (`catch.py:92-95`, sized `size_rank * SIZE_PER_RANK + jitter`, `catch.py:145-147`).
  One cast = one fish. Fishing has no notion of "3 of an item".
- **Quest** — quantity is spread across **named int fields**: `global_xp`, `game_xp`,
  `currency` (`models.py:57-63`). No item stacks.
- **Capacity** is measured in **distinct item-types, never total quantity**
  (`capacity.py:8-9`, `:40-42`) — so the one capacity model in the repo counts *kinds*,
  a third notion of "quantity" again keyed on the bare dict.

### 1c. What each system calls a REWARD / GRANT — the sharpest divergence

| System | Reward type | Citation | Shape |
|---|---|---|---|
| Mining (encounters) | `Reward(item: str, amount: int)`, carried as `rewards: tuple[Reward, ...]` on `EncounterOutcome` | `games/mining/core/encounters.py:129-134`, `:148` | items only |
| Mining (dig) | `tuple[str, int]` = `(ore_name, amount)` | `games/mining/core/rewards.py:90-96` | items only, untyped tuple |
| Mining (explore) | `tuple[str, str \| None, int]` = `(description, item_or_None, delta)`, **delta can be negative** | `games/mining/core/rewards.py:137-155` | item *or* loss |
| Fishing | `Catch(species_id: str, size: int)` | `games/fishing/core/catch.py:90-95` | one neutral-id item + magnitude, no count |
| Quest | `RewardBundle(global_xp, game_xp, currency, capability: Optional[str])` | `games/exploration/quest/models.py:56-63` | XP + currency + capability, **no items** |
| Encounter (shared) | `payload: Mapping[str, object]` | `games/shared/encounter/interface.py:38-45` | free-form dict, **no reward structure** |

Six reward shapes across four systems. Three of them are mining's own. None can be
handed to another system without a bespoke translation, and the shared seam
(`EncounterOutcome.payload`) carries no reward structure at all — so an encounter that
wants to grant loot has no typed way to say so.

### 1d. What each system calls INVENTORY / CAPACITY

- The **only** inventory model is mining's: a bare `dict[str, int]` keyed on display
  strings, with a pure capacity layer (`games/mining/core/capacity.py`) that measures a
  **soft cap in distinct item-types** (`PACK_SOFT_CAP = 40`, `capacity.py:27`;
  `distinct_types`, `:40-42`; `pack_status`/`vault_status`, `:93-100`). Enforcement is
  **gentle/additive — warn, never block** (`capacity.py:11-16`).
- Fishing, quest, and the shared encounter seam have **no inventory model** — fishing's
  `CastOutcome` says "the workflow layer adds the `catch` to the player's haul"
  (`catch.py:98-110`) but never names a hold type; quest grants XP/currency to some host
  ledger; the encounter payload is opaque.

**Net:** the systems already interoperate (fishing → mining inventory, encounters →
loot, quests → progression) but share zero types. The bridge that exists
(`register_fish_species`) drops the neutral id. Any new cross-system feature re-invents
one of six reward shapes.

---

## 2. Proposed unified contract

One small pure-domain vocabulary — frozen dataclasses + Protocols, stdlib only, no
Discord/DB/IO — so it drops cleanly into a superbot-next plugin package. It **carries**
values; it **never computes** them (each system stays the source of its own sim-pinned
amounts — §6). Nouns live in data (Q-0267); mechanics key on neutral ids.

### 2a. Item identity — neutral id + data-side theme lookup

```python
ItemId = str  # a NewType-style neutral id: "ore.diamond", "fish.legend_carp",
              # "curio.coral_idol". NEVER a player-facing noun. Mechanics key on this.

@dataclass(frozen=True)
class ItemMeta:
    """The theme + economy data for one item id — the ONLY re-theme surface (Q-0267)."""
    item_id: ItemId
    name: str                       # display noun (swappable without touching mechanics)
    kind: str                       # "resource" | "tool" | "consumable" | ...
    stackable: bool = True
    value: int = 1                  # economy/display value, carried not computed
    emoji: str = ""
    tags: frozenset[str] = frozenset()

@runtime_checkable
class ItemCatalog(Protocol):
    """A theme-data lookup. Each system supplies one (or shares one); mechanics read
    nouns off it and never hard-code a name in a logic branch."""
    def lookup(self, item_id: ItemId) -> ItemMeta | None: ...
    def ids(self) -> tuple[ItemId, ...]: ...
```

This is fishing's already-correct `species.py` pattern (neutral id + data row)
generalised to every item. Mining's `ItemDef` (`items.py:53-63`) becomes an `ItemMeta`
row behind an `ItemCatalog`, keyed on a neutral id (`"ore.diamond"`) instead of the
display string `"diamond"` — closing the Q-0267 gap noted in §1a.

### 2b. Quantity / stack

```python
@dataclass(frozen=True)
class Stack:
    """A quantity of one item. `qty` >= 1. `attrs` carries per-instance magnitudes
    (e.g. a fish's `size`) for non-fungible items without a parallel type."""
    item: ItemId
    qty: int = 1
    attrs: Mapping[str, object] = MappingProxyType({})  # e.g. {"size": 74}
```

A fungible ore stack is `Stack("ore.diamond", 3)`; a caught fish is
`Stack("fish.legend_carp", 1, {"size": 74})` — subsuming fishing's `Catch.size`
(`catch.py:92-95`) as an attr rather than a fifth reward type.

### 2c. Reward / grant

```python
@dataclass(frozen=True)
class ProgressionDelta:
    """Non-item grants — XP / currency / an earned capability. Subsumes quest's
    RewardBundle. Amounts are CARRIED (set by the granting system), never computed here."""
    global_xp: int = 0
    game_xp: int = 0
    currency: int = 0
    capability: str | None = None

@dataclass(frozen=True)
class Grant:
    """The ONE reward shape: item stacks + a progression delta. A stack's qty may be
    negative to express a loss (mining's explore `delta<0`, rewards.py:137-155)."""
    items: tuple[Stack, ...] = ()
    progression: ProgressionDelta = ProgressionDelta()
```

One `Grant` expresses all six current shapes:
- mining `Reward(item, amount)` → `Grant(items=(Stack(id, amount),))`
- mining dig `(ore, amount)` → same
- mining explore `(desc, item|None, delta)` → `Grant(items=(Stack(id, delta),))` (desc
  stays narration, outside the reward)
- fishing `Catch(species_id, size)` → `Grant(items=(Stack(id, 1, {"size": size}),))`
- quest `RewardBundle(...)` → `Grant(progression=ProgressionDelta(...))`
- encounter `payload` loot → a real `Grant` instead of an opaque dict.

### 2d. Inventory capacity / hold — interface with the host seam left open

```python
@runtime_checkable
class InventoryView(Protocol):
    """Read-only view of a player's hold. The BACKING STORE is the host's — the
    contract is a pure interface, no persistence/IO here."""
    def held(self, item: ItemId) -> int: ...
    def distinct_types(self) -> int: ...

@dataclass(frozen=True)
class CapStatus:
    """A hold's fill against a (soft) cap, in distinct item-types — mining's
    capacity.py:70-91 shape, promoted verbatim so its warn-not-block policy is preserved."""
    used: int
    cap: int
    @property
    def remaining(self) -> int: return max(0, self.cap - self.used)
    @property
    def at_cap(self) -> bool: return self.used >= self.cap

@runtime_checkable
class CapacityPolicy(Protocol):
    """How a host measures a hold against a cap. Default = distinct-types soft cap
    (mining's chosen model); a host may supply its own without changing the contract."""
    def status(self, view: InventoryView) -> CapStatus: ...
```

The contract stays **pure interface**: no store, no DB, no ticker. A host binds a
concrete `InventoryView` over whatever it persists (a dict today, a DB row in
superbot-next). This mirrors the encounter seam, which is a `Protocol` with a reference
impl and no host coupling (`games/shared/encounter/interface.py:48-54`).

---

## 3. Where it lives — `games/shared/inventory/`

**Home:** a new `games/shared/inventory/` package, a **claim-first shared surface** per
`docs/lanes.md:22-32`. This is the established pattern: `games/shared/encounter/` is
exactly this — a public `interface.py` (Protocol + frozen payloads) plus a `reference.py`
impl, claimed first, with interface changes announced in status
(`games/shared/encounter/README.md`, `interface.py:1-11`).

Proposed layout (mirrors the encounter seam):

```
games/shared/inventory/
  __init__.py
  interface.py     # ItemId, ItemMeta, Stack, ProgressionDelta, Grant,
                   # ItemCatalog / InventoryView / CapacityPolicy Protocols, CapStatus
  reference.py     # a dict-backed InventoryView + distinct-types CapacityPolicy
                   # (mining's capacity.py math, promoted) — unblocks consumers now
  conformance.py   # the shared conformance test helpers (§7)
  README.md        # public-surface note + the claim/announce requirement
```

**Adoption — one thin adapter per system, extend-not-duplicate:**

- **Mining** keeps `items.py`/`capacity.py`/`encounters.py` as-is; adds an adapter that
  (a) exposes its `_CATALOG` as an `ItemCatalog` keyed on neutral ids, and (b) maps
  `Reward → Grant`. No sim numbers move.
- **Fishing** maps `Catch → Stack(..., {"size": size})` and exposes `species.py` as an
  `ItemCatalog` (it already keys on neutral ids — near-zero work).
- **Quest** maps `RewardBundle → Grant(progression=...)`; `grant_rewards`
  (`engine.py:141-164`) is untouched, the adapter wraps its return.
- **Shared/encounter** gains a typed `Grant` option instead of stuffing loot into the
  opaque `payload` — the one change that removes an actual footgun.

**Interface-change requirement:** creating `games/shared/inventory/` and any later change
to its public surface is an INTERFACE CHANGE and must be announced in `control/status.md`
in the same session it ships (`docs/lanes.md:28-30`; single-seat repo now, so the one
status file). This doc's claim file is **advisory only** — design, no code change yet.

---

## 4. Migration path — incremental, per-system, each its own merged-on-green PR

No big-bang. Each step is an isolated PR that stays green on its own and leaves every
other system working. Order (dependency-first):

1. **PR-1 — stand up the seam (additive only).** Create `games/shared/inventory/`
   (`interface.py` + `reference.py` + `conformance.py` + `README.md`) + a claim file +
   the status announcement. Nothing imports it yet; the suite grows by the new module's
   own tests. Proves the contract compiles and the reference impl is conformant.
2. **PR-2 — fishing adapter** (smallest, already neutral-id). `Catch → Stack`;
   `species.py` exposed as an `ItemCatalog`. Fishing's existing tests unchanged; adds
   adapter + conformance tests.
3. **PR-3 — mining catalog adapter.** Expose `_CATALOG` as an `ItemCatalog` on neutral
   ids and map `Reward → Grant`. This is where the Q-0267 gap (§1a) is closed. Mining's
   73 tests stay green (the display-string keys keep working behind the adapter until a
   later, separate rename PR if the owner wants one — §6 flag).
4. **PR-4 — quest adapter.** `RewardBundle → Grant(progression=...)`; `grant_rewards`
   untouched.
5. **PR-5 — encounter typed grant.** Add a typed `Grant` field to the shared encounter
   outcome (an interface change → announced), migrate the reference resolver off the
   free-form `payload` for loot.
6. **PR-6 — fish→mining bridge fix (optional).** Re-point `register_fish_species`
   (`items.py:282-304`) at the neutral `species_id` so the one existing cross-system
   bridge stops dropping the id (§1a). Sequenced last because it depends on PR-2 + PR-3.

Each PR is reversible on its own and none rewrites a system's economy.

---

## 5. Integrity floor

Non-negotiable properties the contract must preserve (they are why every system is pure
and sim-pinned today):

- **Determinism preserved.** The contract is inert data + interfaces — no RNG, no
  wall-clock, no IO. It cannot perturb a resolver's determinism (mining's
  `encounter_seed`, fishing's `fishing_seed`, quest's `DetRng`). Adapters are pure
  translations, so `(seed, …) → same outcome` is untouched.
- **No pay-to-win (Q-0039 / Q-0190).** `Grant` **carries** amounts; it never derives
  them. Every reward number stays where it is sim-pinned today — mining's
  `ore_weights_for_depth`/loot rolls, fishing's `_pick_species`/`_roll_size`, quest's
  `TIER_CAPS` (`catalog.py:22-29`, code-owned per Q-0040). The contract exposes no
  coin/purchase/spend lever (the `ProgressionDelta.currency` field is a *carried grant
  amount*, never an input that buys a better outcome). Amounts stay sim-pinned in each
  system; the contract is a transport, not a balance engine.
- **Theme-readiness (Q-0267).** Item identity is a neutral id; every player-facing noun
  lives in `ItemMeta`/the `ItemCatalog` data, never in a mechanic. This *improves* the
  floor: it fixes mining's current violation (display strings as keys, §1a) rather than
  spreading it.

A conformance test (§7) pins each of these as an assertion an adapter must pass.

---

## 6. Open questions / decide-and-flag

**Reversible calls I'm making (no owner sign-off needed — changeable in a follow-up):**

- **D — `Grant` unifies items + progression in one type** (rather than two sibling
  types). Rationale: one reward shape is the whole point; a quest that later grants an
  item, or an encounter that grants XP, needs no new type. Reversible: split later if it
  bloats.
- **D — per-instance magnitude via `Stack.attrs`** (rather than a `FishStack` subtype).
  Keeps one stack type; fishing's `size` rides as an attr. Reversible.
- **D — negative `qty` expresses a loss** (mining explore `delta<0`). Reuses one field
  instead of a `Loss` type. Reversible.
- **D — dict-backed reference `InventoryView`** in `reference.py`, mirroring the
  encounter reference resolver, so consumers are unblocked before a host store exists.

**Genuine owner-decisions (⚑ flag — do NOT decide unilaterally):**

- **⚑ Neutral-id namespace + the mining rename.** Adopting `"ore.diamond"`-style ids
  means mining's inventory keys eventually change from `"diamond"` to a neutral id. The
  *adapter* (PR-3) hides this, but a full rename of the persisted keys is a
  data-migration the owner must approve (and superbot-next may have opinions on the id
  scheme). Until then the adapter maps old↔new; no persisted data changes.
- **⚑ Does `currency` belong in the shared contract at all,** or stay a quest-only
  concept? Folding it into `ProgressionDelta` is convenient but couples the contract to
  an economy concept mining/fishing don't use. Flagging rather than assuming.
- **⚑ One shared `ItemCatalog` vs per-system catalogs.** The doc assumes per-system
  catalogs behind a common Protocol. A single merged catalog is possible but is a bigger
  coordination surface — owner call.

---

## 7. Verification — how a future implementation slice proves conformance

The seam ships with a **shared conformance test** (`games/shared/inventory/conformance.py`)
that every adapter runs against its own mapping — the same discipline the encounter seam
uses (a Protocol + a reference impl the tests pin). A conforming adapter must satisfy:

1. **Round-trip identity.** For every reward the system can emit, `to_grant(reward)`
   produces a `Grant` whose `Stack.item` ids all resolve via the system's `ItemCatalog`
   (`lookup(id) is not None`) — no reward names an unknown item (mirrors mining's
   existing `test_rewards_only_use_the_existing_item_vocabulary`, cited
   `docs/design/mining-grid-encounters.md:186`).
2. **No-spend-lever invariant.** The mapping function's signature exposes no
   coin/purchase/spend input (mirrors mining's
   `test_resolver_exposes_no_spend_or_purchase_lever`, cited
   `mining-grid-encounters.md:184`). Amounts in the produced `Grant` equal the system's
   own sim-pinned outputs — the adapter adds nothing.
3. **Determinism pass-through.** Feeding the same seed to the system + adapter twice
   yields byte-identical `Grant`s (the adapter introduces no RNG).
4. **Theme-data-only nouns.** Every player-visible string comes from the `ItemCatalog`
   data, asserted by keying the test on neutral ids and swapping a display name to prove
   mechanics don't move (fishing's Q-0267 test pattern).
5. **Capacity semantics preserved.** The reference `CapacityPolicy` reproduces mining's
   distinct-types soft-cap numbers (`PACK_SOFT_CAP=40`, vault ladder) — a regression pin
   so promoting `capacity.py` doesn't silently change the cap.

A future implementation slice is "done" when its adapter's conformance test is green and
the system's own existing suite is unchanged (additive-safety). Collection is proven the
same way the repo already does it: `python3 -m pytest tests/ games/exploration/tests/ -q`
plus `python3 bootstrap.py check --strict`.
