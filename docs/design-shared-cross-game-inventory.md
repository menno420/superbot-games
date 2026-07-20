# Shared cross-game inventory — fishing catches into the mining market

> **Status:** `plan` · 2026-07-19
>
> A ONE-PAGE planning/design doc (NOT a build). Reads the real fishing and
> mining seams, names where they meet or fail to meet, lays out options, and
> recommends one. Every genuine product-intent fork is marked
> `⚠️ OWNER PRODUCT CALL:` and is **left for the owner** — this doc does not
> decide them. Companion to `docs/design/world-inventory-resource-contract.md`
> (the pure contract already stood up at `games/shared/inventory/`) and
> `docs/NEXT-TASKS.md` § "Next session" item 2 (the latent fork this scopes).

---

## 1. Problem

A player who fishes and a player who mines keep two unrelated piles of stuff.
There is no way for a fish caught in the fishing game to be **sold at the mining
market**, and no shared place a reward from one game can be spent in the other.
A "shared cross-game inventory" would give the world one hold: catch a fish,
walk it to the mining market, sell it at a price both games agree on — and, more
broadly, make cross-game economy loops (fish-to-buy-a-pickaxe) reachable.

It isn't trivial today for three reasons, all visible in the code:

1. **The two games represent an item completely differently.** Mining keys
   everything on a **lowercased display string** that is simultaneously the
   catalog key, the inventory key, and the player-facing noun
   (`games/mining/core/items.py` — `_CATALOG` is keyed on `name.lower()`, rows
   literally are `"diamond"`, `"iron"`, `"lucky charm"`). Fishing keys on a
   **neutral `species_id`** with the nouns in a data table, and its adapter
   already emits neutral shared ids like `fish.legend_carp`
   (`games/fishing/inventory/adapter.py`, `FISH_NAMESPACE = "fish"`). These two
   id schemes do not interoperate without a translation.

2. **The store shapes differ.** Mining's hold is a live, **mutated
   `dict[str, int]`** (`state.inventory[name] = held - qty` in
   `services/mining_workflow.py::sell`, line ~409). The shared contract's hold
   (`games/shared/inventory/`) is a **pure, immutable** `InventoryView` /
   `ReferenceInventory` that returns a new hold on every grant. Fishing has no
   persistent hold at all — a `Catch` becomes a `Grant` and is sold or cooked in
   the same breath.

3. **The valuation is already "canonical" but unreachable.** PR #174 made the
   fishing **V043** curve canonical for a fish's mining-market price (see §2),
   but the wiring that would exercise it does not exist — so the canonical
   decision silently assumes a shared-inventory *shape* nobody has chosen yet.

## 2. Current seams — where they meet, and where they don't

**Fishing inventory model.** A landed fish is `Catch(species_id, size)`
(`games/fishing/core/catch.py`). The fishing→shared adapter
(`games/fishing/inventory/adapter.py`) maps it onto the shared §2 contract:
`item_id_for_species("legend_carp") → "fish.legend_carp"`, `catch_to_stack`
carries `size` in `Stack.attrs`, and `catch_to_grant` attaches a
`ProgressionDelta(game_xp=size_rank)`. Fishing is **already on the shared
contract** — neutral ids, nouns in data, pure.

**Fishing valuation (the V043 curve).** `games/fishing/core/economy.py` holds
the sim-pinned **V043** sell curve verbatim (VERDICT 043, landed via PR #80):
`SELL_VALUES = {minnow: 8, bass: 13, pike: 27, legend_carp: 80}`, exposed as
`sell_value()` / `is_sellable()`.

**Mining market / valuation.** Mining sells only explicitly-catalogued
`RESOURCE` items at their catalog `value` (`games/mining/core/market.py::sell_price`
→ `items.item_value`; ore values live in `_CATALOG`, e.g. diamond 12, gold 6).
The gear shop (`GEAR_SHOP`) is the coin sink. Selling mutates the live
`dict[str,int]` hold in `services/mining_workflow.py::sell`.

**Where they meet — the one interop point that already exists.** Mining's
`games/mining/core/items.py::register_fish_species` folds fish rows into the
mining catalog as sellable `RESOURCE`s, and **PR #174 (`e0b8123`, decision #7)
made the fishing V043 curve canonical** for their price: `_fish_value` lazily
imports `games.fishing.core.economy.sell_value` at host-wiring time, so a
registered `legend_carp` is worth **80** in the mining market (not the old
`max(1, size_rank)` ≈ 4 — closing a ~20× gap). The lazy import preserves the
mining core's import-time severance from fishing.

**Where they fail to meet — the missing seam.** `register_fish_species` is
called **only from a test**, and **no seam moves a caught fish into
`MiningState.inventory`** (`docs/NEXT-TASKS.md` § "Next session" item 2). So the
canonical valuation is correct-by-construction but **unreachable**: two id
schemes (`fish.legend_carp` vs the lowercased `"legend_carp"` catalog key), two
store shapes (pure immutable vs live mutated dict), and no bridge between them.
The shared pure contract at `games/shared/inventory/` exists (migration PR-1)
but **nothing in a command path consumes it** — fishing has an adapter, mining
does not.

## 3. Options

### Option A — Shared inventory *core* both games depend on
Both games adopt `games/shared/inventory/` as their real hold: write a mining
adapter (the twin of the fishing one) mapping mining's string keys ↔ neutral
`ore.*` ids, migrate `MiningState.inventory` onto the pure `InventoryView`, and
give the world **one hold** keyed on neutral ids. A fish and an ore are the same
`Stack` type in the same store.
- **Upside:** the "one hold" the problem asks for; one price per species by
  construction; cross-game loops (fish → buy gear) fall out for free.
- **Downside / blast radius:** **large.** Touches every mining call site that
  reads/writes `state.inventory` (workflow sell/buy/cook, `loadout.py`,
  `exploration.py`, `cli.py` rendering), and the persisted key format changes
  `"diamond"` → `ore.diamond` — a **data migration** the contract doc already
  flags as an owner call (`world-inventory-resource-contract.md` §6, ⚑
  neutral-id namespace + mining rename).
- **Reversibility:** low once persisted keys change; the mining rename is the
  hard-to-undo part.

### Option B — An exchange / bridge service that converts between per-game inventories
Leave each game's inventory as-is. Add a thin **bridge** in `services/` (e.g.
`services/inventory_bridge.py`) that takes a fishing `Grant` (via the existing
fishing adapter) and *deposits* it into `MiningState.inventory` by resolving the
neutral `fish.<id>` back to the mining catalog key and calling
`register_fish_species` + a normal mining `sell`. One-directional to start
(fishing → mining), an explicit "walk your catch to the market" action.
- **Upside:** **small blast radius** — no store rewrite, no key migration; each
  game keeps its own model; reuses the fishing adapter and #174's canonical
  valuation directly. The bridge is one file with one seam.
- **Downside:** two holds still exist; the bridge is a translation layer to
  maintain, and "which id maps to which key" lives in it (a second mapping
  surface next to the fishing adapter's). Not "one hold" — a *pipe* between two.
- **Reversibility:** **high** — delete the file and the two games are exactly as
  they are today. Nothing persisted changes shape.

### Option C — Canonical valuation table as the single interop point (items stay per-game)
Do **not** share the inventory at all. Keep fish in fishing's hold and ore in
mining's; share only the **price**. #174 already did the substantive half:
fishing's V043 curve is the single source of truth for a fish's value. Formalize
that a fish is "sold at the mining market" as a **valuation lookup, not a
transfer** — the fish never enters `MiningState.inventory`; the market just
quotes the V043 price and credits coins.
- **Upside:** **smallest possible** change; the interop point already exists and
  is tested; no id scheme or store has to converge; the "same species never
  sells for two prices" guarantee is kept by the shared curve.
- **Downside:** it doesn't deliver a *shared inventory* — it delivers shared
  *pricing*. A player can't hold a fish "in the mining world" or spend a fish
  toward gear; only sell-for-coins at a shared price is reachable. If the owner
  actually wants a unified hold, this under-delivers.
- **Reversibility:** **highest** — it's essentially the status quo made
  reachable; a thin sell-path that reads the V043 price.

## 4. Recommendation

**Start with Option B (the bridge), designed so it can graduate to Option A.**
The problem the owner queued is reachability — a caught fish that can actually be
sold at the mining market — and B delivers exactly that with a small, fully
reversible blast radius: one `services/` file, reusing the fishing adapter and
#174's already-canonical V043 valuation, no persisted-key migration, no rewrite
of mining's live `dict` store. Option A is the "right" long-term shape (one hold,
one id scheme) but it drags in the mining neutral-id rename — a data migration
the contract doc already flags for the owner — so it should not be the *first*
step. Option C is too little if the owner wants a real shared hold. Building B
first makes decision #7 reachable and testable, surfaces the real product
questions (below) against working code, and leaves the door to A open: the bridge
is written against the shared contract, so "promote the bridge into a shared
core" is a later, deliberate PR, not a rewrite forced up front.

## 5. Owner product calls (do NOT decide these — flagged for the owner)

These are genuine product-intent forks, not engineering calls. Each is left open.

- ⚠️ **OWNER PRODUCT CALL: Should a fish be sellable at the mining market at
  all?** The whole feature assumes yes. If fishing is meant to be its own
  self-contained economy, the answer might be "no — keep the two economies
  separate," which retires this work entirely.
- ⚠️ **OWNER PRODUCT CALL: One unified hold, or two bridged holds?** Option A
  unifies inventories (one pile, one id scheme, the mining rename); Option B
  keeps two and pipes between them. This is the architecture fork
  `docs/NEXT-TASKS.md` item 2 explicitly leaves to the owner ("shared ledger" vs
  "one-directional").
- ⚠️ **OWNER PRODUCT CALL: One-directional (fishing → mining) or bidirectional?**
  Can ore/gear also flow into the fishing world, or only fish → mining market?
  The recommendation starts one-directional; bidirectional is a bigger surface.
- ⚠️ **OWNER PRODUCT CALL: Is V043 the right *cross-game* price, or only the
  right fishing price?** #174 applied the owner-default (V043 canonical) as a
  reversible balance call. Selling a `legend_carp` for 80 coins in the mining
  economy is a **balance** decision about the mining coin faucet, not just a
  fishing one — confirm or override before it becomes reachable.
- ⚠️ **OWNER PRODUCT CALL: Exchange rate / parity.** If coins, XP, or currency
  ever convert across games (fishing XP ↔ mining coins, or a non-1:1 fish→coin
  rate at the mining market vs the fishing market), the rate is pure product
  intent. Default is 1:1 at the shared V043 price; anything else is an owner
  call.
- ⚠️ **OWNER PRODUCT CALL: Does a fish occupy the mining capacity cap?** Mining
  uses a distinct-types soft cap (`CapStatus`, warn-not-block). Whether deposited
  fish count against a miner's pack is a product/UX call, not an engineering one.

## 6. Decision log — the 6 owner calls, resolved (2026-07-20)

Coordinator-decided under the owner continue directive (2026-07-20), taking the
most conservative, reversible default for each §5 fork so slice 1 could ship
Option B without stalling. Every default is reversible (flip
`GAMES_INVENTORY_BRIDGE_ENABLED` off or delete `services/inventory_bridge.py`):

1. **Fish sellable at the mining market at all?** → YES in principle, but the
   entire bridge path is **CONFIG-GATED OFF BY DEFAULT** — no existing gameplay
   changes until explicitly enabled.
2. **Unified vs bridged hold?** → **BRIDGED** (Option B): two separate per-game
   inventories, a service pipes between them. No migration of mining's dict
   store, no shared id scheme.
3. **One-directional or bidirectional?** → **ONE-DIRECTIONAL** (fishing → mining
   only). No ore/gear flows into fishing.
4. **V043 as the cross-game price?** → **USE V043 CANONICAL VALUATION** (the #174
   default) as the fish's coin value at the mining market. Reversible balance call.
5. **Exchange rate / parity?** → **1:1 AT THE SHARED V043 PRICE.** No currency/XP
   conversion.
6. **Does a fish occupy the mining capacity cap?** → **N/A BY DESIGN** — the
   bridge SELLS fish for coins (fish → coins); it never deposits fish objects into
   the mining pack, so no fish occupies the mining capacity cap. Sidesteps the cap
   question.

Landed by **slice 1**: `services/inventory_bridge.py` — a pure `fish_market_value`
(reusing `games.fishing.core.economy.sell_value`, the V043 curve #174 wired into
the mining market) + a config-gated `exchange_fish_for_coins` (moves fish from a
`FishingState.haul` to coins on a `MiningState`, all-or-nothing, no-op when the
flag is OFF). Additive seam only — nothing wired into a live CLI/command path yet.

Landed by **slice 2**: the exchange is now reachable from a live, **config-gated**
`exchange` verb in the fishing CLI (`games/fishing/cli.py`, "walk your catch to the
mining market"), routed through a new audited wrapper
`services/inventory_bridge.py::exchange_fish_for_coins_audited`. It emits BOTH legs
of the money flow — the fishing-haul debit (`subsystem="fishing"`,
`target="haul:<species>"`) and the mining-coin credit (`subsystem="mining"`,
`target="coins"`), both `mutation_type="inventory:exchange"` — to the SAME
`services/audit.py` sink the sibling `fishing_workflow.sell` / `mining_workflow.sell`
legs use, so the cross-game sale is reconstructable from one ledger. Still DEFAULT
OFF and unchanged in every §6 default: with `GAMES_INVENTORY_BRIDGE_ENABLED` unset
the verb is unavailable (a clear "bridge is disabled" no-op, absent from the help
surface, records nothing), so no existing gameplay changes until the owner flips the
flag. All-or-nothing / non-destructive on error (no partial audit is ever left
behind) and one-directional (fishing → mining only).

Landed by **slice 3**: the surrounding CLI surface + discoverability for the bridge.
A NEW read-only `value <species> [qty]` verb in the fishing CLI
(`games/fishing/cli.py::_do_value`) previews what a catch would fetch at the mining
market via `services/inventory_bridge.py::fish_market_value` (the canonical V043
price) — pure information, no mutation, no audit row — so, unlike the mutating
`exchange` verb, it is **available regardless of the flag** and is always listed in
`help_lines()`. The MUTATING `exchange` verb stays **CONFIG-GATED DEFAULT OFF**: with
`GAMES_INVENTORY_BRIDGE_ENABLED` unset the mutation surface is byte-identical to
before the bridge existed. NOTE on the non-interactive/scriptable surface: the games
hub (`python3 -m games`) and the per-game entry points are pure REPLs with **no
argv/subcommand dispatch**, so slice 3 did NOT invent a one-shot CLI command — the
read-only preview is scriptable through the existing TTY-free `run_commands` driver
(the same path the tests drive), matching the codebase's real idiom. All six §6
defaults are unchanged. Next: **owner steer** on the still-open product forks
(sellable-at-all, the 1:1 V043 rate) or **slice 4** — a bidirectional flow /
promoting the bridge toward a shared inventory core.
