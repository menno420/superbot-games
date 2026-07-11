# World Games — Persistence & Save-State Contract

> **Status:** `plan` — design / contract-only. No storage backend, no I/O, no balance
> numbers ship here. This doc defines the *shape* of persisted player state and
> the *policy* for cross-server onboarding transfers so the rebuilt host
> (`menno420/superbot-next`) can implement storage against a fixed contract.

Owner: world-games seat. Consumes: [`world-inventory-resource-contract`](world-inventory-resource-contract.md)
(`Grant` / `Stack` / `ItemId` / `ProgressionDelta`).

---

## 1. Scope and host seam

This repo owns the **contract**: the versioned schema of persisted player state,
the deterministic (de)serialization rules, and the migration registry. All are
pure, stdlib-only, deterministic functions — no database, no filesystem, no
network.

`superbot-next` owns the **storage**: which KV/DB backend holds the bytes, how
keys are sharded per guild/server, transaction boundaries, and durability. The
host reads a `PlayerState` blob, hands it to pure domain code, receives an
updated `PlayerState`, and writes it back. The seam is a byte string (canonical
JSON, §3) plus the migration entry point (§4).

```
  host (superbot-next)                 contract (this repo)
  ---------------------                ---------------------
  load bytes  --------------------->   deserialize(bytes) -> PlayerState
                                       migrate(PlayerState) -> PlayerState @ current version
  run domain turn  <---------------    pure domain code mutates a copy
  store bytes <---------------------   serialize(PlayerState) -> bytes
```

The host never inspects domain-internal fields; the contract never learns where
the bytes live. This mirrors mining's existing energy/capacity posture
(ADR-001/002: no external state, effective values computed from stored scalars +
elapsed time).

## 2. PlayerState schema

`PlayerState` is a versioned envelope over per-domain namespaces. Each namespace
is owned by exactly one domain; no domain reads another's namespace.

| Field | Type | Notes |
|---|---|---|
| `schema_version` | `int` | Monotonic. Bumped only by a migration (§4). |
| `player_id` | `str` | Host-issued stable id. Opaque to the contract. |
| `namespaces` | `map<str, DomainState>` | Keyed by namespace id (below). |

**Namespace ids (fixed vocabulary):**

| Namespace | Owner domain | Holds |
|---|---|---|
| `shared-inventory` | `games/shared/inventory` | `Stack[]` keyed by `ItemId`; capacity/vault scalars |
| `mining` | `games/mining` | energy scalar + `updated_at`, grid position, workshop/vault levels, titles |
| `exploration` | `games/exploration` | quest progress, survival state, leverage counters |
| `fishing` | `games/fishing` | per-spot cooldowns, species-seen set, rod/loadout refs |
| `dnd` | `games/dnd` | scene/beat cursor, effect flags, menu-history for anti-repeat |

Each `DomainState` is itself `{ "v": <int>, ... }` — a domain carries its own
inner version so a domain can migrate independently of the envelope when its
change is domain-local (see §4 two-tier rule).

**Wealth is not double-stored.** Currency and XP live once, in
`shared-inventory` (currency as a reserved `Stack`/scalar) and progression
totals; domains reference, never copy, so `TRANSFER_CONSERVATION` (§5) has a
single source of truth.

## 3. Deterministic serialization

Serialization MUST be canonical so equal state produces byte-identical output
(needed for content-hash dedup, migration idempotence tests, and the balance
freshness check downstream):

- Encoding: UTF-8 JSON.
- Object keys sorted lexicographically (`sort_keys=True`).
- No insignificant whitespace (`separators=(",", ":")`).
- Integers as integers; no floats in persisted economy fields (coins/xp/qty are
  integer — matches `Stack.qty: int`, `ProgressionDelta.currency: int`).
- `Stack[]` serialized in ascending `ItemId` order; `attrs` keys sorted.
- Absent optional fields are omitted, never written as `null` (a migration adds
  a field with a default rather than persisting `null`).

`serialize`/`deserialize` are inverses on any migrated-to-current `PlayerState`.

## 4. Migration story

Forward-only, deterministic, idempotent. No down-migrations (a restore uses an
older backup, not a reverse migration).

- **Two tiers.** Envelope migrations bump `schema_version` and may add/rename
  namespaces. Domain migrations bump a namespace's inner `v` and touch only that
  namespace. The host calls one entry point, `migrate(state) -> state`, which
  runs envelope migrators then per-namespace migrators until every version is
  current.
- **Registry.** Each migrator is a pure `(old) -> new` function registered under
  the version it upgrades FROM. Gaps are a hard error (missing step, not a
  silent skip).
- **Idempotence.** `migrate(migrate(x)) == migrate(x)`. An already-current state
  passes through untouched. This is a required test at implementation time.
- **Unknown-namespace policy.** An unknown namespace id is preserved verbatim
  (forward-compat: an older host must not delete a newer domain's data). An
  unknown *field* inside a known namespace is likewise preserved.
- **New domain onboarding** (e.g. fishing -> a future domain): ships as a new
  namespace at inner `v=1` with an envelope migrator that inserts it empty; old
  saves get the empty namespace on first load.

## 5. Owner directive — cross-server transfer policy

> Recorded verbatim intent (owner, 2026-07-11). Persistence is decided at
> superbot root level but not fully implemented. This section fixes the
> *invariants*; the numbers are OWNER-DECIDES and get sim-pinned at
> implementation, NOT invented here.

**Intent.** When a player joins a new server, they may **opt in** to move over a
bounded percentage of their *other-server* account's items / coins / XP. This is
a **TRANSFER, not a gain** — no duplication, no bonus, no minting. Purpose: a new
player is never hopelessly behind, but the catch-up gap stays bounded. Hard
guard: a transfer can **never** make someone the richest player in the target
server on arrival.

### Named invariants

- **`TRANSFER_CONSERVATION`** — Nothing is minted by a transfer. Across the
  `{source, target}` pair the total of each conserved quantity (coins, per-item
  qty, XP) after the transfer is `<=` the total before. The credit applied to
  the target is `<=` the debit taken from the source; any shortfall (fraction
  cap, rounding, wealth cap) is burned, never rounded up. Source-debit semantics
  (does the source account actually lose it? is a cross-server debit even
  reachable?) is an OWNER-DECIDES item below.
- **`TRANSFER_FRACTION_CAP`** — The credited amount is `<= F` of the source
  holding for that quantity, where `F` in `(0, 1)` is a single configured
  fraction. `F` is OWNER-DECIDES (sim-pinned). A transfer moves *at most* a
  fraction, so no single hop is a full account clone.
- **`NO_INSTANT_RICHEST`** — After credit, the player's target-server wealth
  (for each ranked quantity) is **strictly less than** the current target-server
  maximum, or below a configured percentile `P` of the target distribution,
  whichever is lower. If honoring `TRANSFER_FRACTION_CAP` would still land the
  player at/above that ceiling, the credit is clamped further down (burning the
  remainder under `TRANSFER_CONSERVATION`). The transfer can shrink the gap; it
  can never top the leaderboard.

Precedence when caps conflict: `NO_INSTANT_RICHEST` clamps hardest, then
`TRANSFER_FRACTION_CAP`, all under `TRANSFER_CONSERVATION` (the burn absorbs the
difference). No pay-to-win: a transfer moves *earned* holdings within bounds and
can only ever reduce total system wealth (Q-0039 / Q-0190 posture preserved).

### OWNER-DECIDES (do not invent — sim-pin at implementation)

1. Exact `F` (fraction cap) — one global value, or per-quantity (coins vs XP vs items)?
2. Which resources are transferable — all items, or a whitelist (e.g. currency + XP only, no rare gear)?
3. One-time (first join) vs repeatable — and if repeatable, a cooldown / lifetime cap so hops don't compound past `TRANSFER_FRACTION_CAP`.
4. Source-debit semantics — is the source account truly debited (requires cross-server write), or is this a one-way seeded credit bounded by a *read* of the source? `TRANSFER_CONSERVATION` holds either way for the target credit; the source side is the open question.
5. `NO_INSTANT_RICHEST` ceiling — server maximum vs a percentile `P`, and whether it is measured live at transfer time or against a snapshot.

## 6. Forward-looking — player-to-player markets / trading (NOT COMMITTED)

> "maybe, if a proven method keeps it fair and fun" — owner, 2026-07-11.
> This section is a sketch of what a fairness proof would require. **Nothing
> here is committed**; no trading surface is designed or scheduled.

For player-to-player trading to be admissible under the integrity floor, a
proposal would have to demonstrate, with a sim-pinned harness (the same
deterministic style as the economy sim):

- **Emission vs sink balance** — total currency/XP emission rate (all reward
  sources) and sink rate (upgrades, costs) are measured and bounded; trading
  must not create a net emission channel (it only *moves* existing wealth, like
  transfers).
- **No pay-to-win under trading** — no tradeable path lets currency buy raw
  combat/economic power faster than earning it; trades move fungible/earned
  holdings, never capability that was gated behind play.
- **Anti-hoarding bounds** — provable ceilings preventing a small number of
  accounts from cornering a resource (per-account holding caps, decay, or
  market-depth limits), with the bound stated and sim-checked.

Absent a proof meeting all three, trading stays out. This is a research note,
not a roadmap item.

## 7. Open questions (owner queue)

The OWNER-DECIDES items in §5 and the whole of §6 are the open decisions. None
are invented here; all balance numbers are sim-pinned at implementation time.
