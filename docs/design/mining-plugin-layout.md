# Mining plugin — package layout & port design

> **Status:** `plan` · lane: game-mining · 2026-07-09
>
> Home for the mining plugin's package shape, its mapping onto the superbot-next
> host contract, the port-order DAG, the severed couplings, and the grid-encounters
> extension seam. Companion to the brief (`docs/founding-plan-mining.md`) and the
> research reference (`docs/research/buildability-map-mining.md`). Where this doc
> and the shipped oracle disagree, **the oracle wins** (shipped behaviour is the spec).

## 1. What ships this session

The **pure-domain core** only: `games/mining/core/` — all 18 pure oracle modules
(`menno420/superbot` `disbot/utils/mining/*` + `disbot/utils/equipment.py`) ported
**verbatim** (every formula and balance constant unchanged), Discord/DB/IO-free, unit
tested. The workflow and host-adapter layers are **named-next**, not built here.

## 2. Three-layer package shape

The mining plugin mirrors the oracle's clean decomposition (pure domain → audited
write boundary → thin Discord shell) as three layers:

```
games/mining/
  core/           # LAYER 1 — pure domain (THIS SESSION). stdlib only; no Discord/DB/IO.
    equipment.py      # cross-game gear→stats model (EffectiveStats, tiers, set bonus)
    items.py          # item taxonomy (kinds, tiers, values, tool ladders) [fish coupling severed]
    rewards.py        # mining/harvest loot tables (injectable RNG)
    world.py          # depth↔biome model + descent gating (z axis)
    exploration.py    # loadout-aware exploration outcome engine (injectable RNG)
    grid.py           # seed-deterministic procedural grid (x/y at a depth) ← grid-encounter seam
    energy.py         # passive-regen energy "fuel" model
    capacity.py       # pack soft-cap + vault capacity/upgrade math
    skills.py         # 4-branch capped skill tree → stats (forced specialization)
    character.py      # gear + skills merge point
    titles.py         # earned-title catalogue (derived from progression)
    market.py         # pure pricing (sell values, the gear shop)
    recipes.py        # crafting recipes (in-code defaults + injection) [file IO severed]
    workshop.py       # durability / repair / craft helpers
    structures.py     # buildable structures (forge / home / campfire) [4 fishing structures severed]
    taxonomy.py       # 3-layer menu grouping (Category→Type→Variant)
    loadout.py        # best-loadout ("Equip Best") set-aware picker
    names.py          # fuzzy item-name resolver
  workflow/       # LAYER 2 — named-next. Audited op seam (mirrors services/mining_workflow.py).
  # host-adapter # LAYER 3 — named-next. superbot-next SubsystemManifest binding.
```

**Mapping onto the oracle:**

| superbot-games layer | oracle equivalent | role |
|---|---|---|
| `games/mining/core/` | `disbot/utils/mining/*` + `utils/equipment.py` | pure domain — decides *what* happens |
| `games/mining/workflow/` (next) | `services/mining_workflow.py` | audited op: read state → call core → **one** transaction to commit |
| host-adapter (next) | `cogs/mining_cog.py` + `views/mining/*` | Discord/host surface — thin; delegates to workflow |

**Why `equipment.py` sits under `core/` (not `games/shared/`):** the oracle keeps it
in `utils/` because it is genuinely cross-game (deathmatch/fishing also read
`EffectiveStats`). It is a **promotion candidate for `games/shared/`** — but that move
is the claim-first moment (`docs/lanes.md`), and no second game has ported yet. To stay
in-lane and unblocked, the pure mining port vendors it under `core/`; when
deathmatch/fishing port, promote it to `games/shared/` under a claim and have both games
import the shared copy. _Self-initiated decision (reversible); flagged on the run report._

## 3. The superbot-next host contract (resolves OPEN QUESTION #1)

The contract is **not in flight / absent** — it exists concretely in `menno420/superbot-next`
and mining already has a **partial** domain there (core loop live; deep systems pending on
the **D-0043** named successor port). The pure core this session ships is exactly the
material that D-0043 port will consume. Captured contract shape:

> **Shape finalized since capture (2026-07-09).** The contract's *shape* has since been
> finalized as **binding** at `menno420/superbot-next docs/game-plugin-contract.md@d3dba9b`
> (ledger D-0056) and differs from the shape captured below: the binding contract makes
> plugins installable Python packages on the `sb.plugins` entry-point group exporting
> `MANIFEST`/`MANIFESTS`, adds a `@provider` ref (alongside `@handler`/`@panel`/`@workflow`),
> and defines a `plugin_pin` → `plugins.lock.json` → boot-time-verify pin lifecycle (drift
> ⇒ `FAILED_STARTUP(plugin_gate)`). Treat `docs/game-plugin-contract.md@d3dba9b` as the
> authoritative shape; the capture below records this doc's earlier reading.

- **Manifest root:** `sb/spec/manifest.py` → `@dataclass(frozen=True) SubsystemManifest`
  with facet slots: `key, version, commands, panels, settings, stores, events,
  capabilities, data_invariants, wizard_sections`. The compiler is **duck-typed** over
  facet objects (reads declared fields), so facets grow without compiler edits.
- **Per-subsystem module:** `sb/manifest/<x>.py` declares `MANIFEST = SubsystemManifest(...)`
  (pure declarations) and binds callables with `@handler`/`@panel`/`@engine`/`@workflow`
  decorators from `sb.spec.refs`; exposes an `ENSURE_REFS` lifecycle callback that
  (re)registers refs/ops idempotently. (`sb/manifest/mining.py` is the live example.)
- **Facet specs:** `CommandSpec` (name/kind/route/aliases/capability), `PanelSpec`
  (panel_id/actions/handlers/`ResultRender`), `StoreSpec` (`register_store(...)` with
  `sole_writer`, `retention`, `forward_map_kind`, `reader_domains`, `erasure_ref`).
- **Handlers/ops:** a handler (`handler("mining.mine_route")`) wraps a workflow op run via
  `engine.run(WorkflowRef("mining.mine"), ctx)`; the op returns an outcome the handler
  renders. **The pure core is never imported by the host directly — the workflow op is the
  seam.** (`sb/domain/mining/rewards.py` in next is already a pure port with the SAME
  injectable-`rng` convention this port uses — independent confirmation the shape is right.)

**Adapter = swappable boundary.** The pure core has **zero** knowledge of `SubsystemManifest`.
Layer 3 (host-adapter) is the only place that imports `sb.spec.*`; it declares the manifest
facets and routes each command/panel action into a Layer-2 workflow op, which calls Layer-1
core. If the contract shifts, only Layer 3 changes — the pure core is **contract-independent**,
so it is safe to ship ahead of any contract churn (the founding-plan requirement).

Grid navigator → a **g1 dynamic session** keyed `(guild, user, 0, "mining_grid")` (D-0042),
text/emoji map first (image `ResultRender` deferred). Persistent stores
(`mining_inventory`, `mining_player_state`, +`guild_id`, TEXT ids) are owned by next's
audited write lanes once docked — Layer 2's job, not Layer 1's.

## 4. Port-order DAG (dependency order)

Ports respect the oracle dependency graph (all landed this session):

```
equipment ─┬─> items ──> rewards ──> grid
           │      │          │
           │      └──> market ──> workshop
           │      └──> taxonomy
           ├──> exploration ──> world
           ├──> skills ──> character
           │        └──> titles
           ├──> structures
           └──> loadout
recipes (standalone)   names (standalone)   energy (standalone)   capacity (standalone)
```

Load-bearing correctness properties preserved (see §6): **additive-safety** (zero-state =
baseline) and **seed-deterministic RNG** in `grid.py`.

## 5. Severed couplings (the two fishing leaks + purity)

The oracle's pure mining package depends only on `utils/equipment.py`; fishing leaks into
two spots, and one module does file IO. All three are severed for the pure, mining-only port:

1. **`items.py` → `utils.fishing.fish.SPECIES`** (import-time fold of fish rows). *Severed:*
   the import is removed; fish rows fold in through a documented **injection point**
   `items.register_fish_species(species)` (accepts any `name`+`size_rank` rows via a
   structural `FishLike` Protocol). The mining catalog is byte-identical to the oracle's
   **minus** the fish rows — mining items are unaffected (additive-safety). A host wires the
   fishing plugin's `SPECIES` in once fishing ports; the shared-inventory/shared-market
   behaviour is preserved without a fishing dependency.
2. **`structures.py` → 4 fishing structures** (`TIDE_POOL`, `DOCK`, `BOATHOUSE`, `FISHERY`
   + their ladders/level-names/step-constants/`_DEFS` rows/`MAX_*`/multiplier helpers).
   *Severed:* dropped entirely, leaving `FORGE` / `HOME` / `CAMPFIRE`. The generic
   `BuildCost` / `StructureDef` / registry shape is **unchanged**, so the fishing port
   re-adds them as registry rows (one entry each). Flagged in-code at each removal site.
3. **`recipes.py` → filesystem IO** (`open(RECIPES_FILE)` + `json.load`). *Severed for
   purity:* `load_recipes()` returns the in-code `DEFAULT_RECIPES` (verbatim); an optional
   `overrides` argument is the injection point a host uses to feed JSON/DB-loaded recipes,
   normalised through the oracle's exact cleaning rules (`normalise_recipes`).

**Deliberately retained verbatim (inert data, no fishing dependency):** `equipment.py`'s
fishing-charm gear rows + `fishing_power`/`bite_luck` stat fields, and `market.py`'s
fishing-charm shop rows + fishing-structure `*_BUILD_REASON` string constants. These pull
in **no** fishing code (they are pure ints/strings), and preserving them keeps the port
byte-faithful and additive-safe (they no-op for mining). Dropping them would deviate from
"verbatim" for zero purity gain.

**One behaviour-preserving enhancement:** an optional injectable `rng: random.Random | None`
was threaded through `rewards.roll_mine_loot` / `roll_harvest_amount` / `roll_explore_outcome`.
`rng=None` uses the global `random` module → **byte-identical to the oracle** (same formulas,
same constants); it only enables deterministic tests, mirroring the oracle's own
`exploration.resolve(rng=...)` convention **and** superbot-next's already-shipped mining port.

## 6. Sim-pinned balance statement

Per no-pay-to-win (Q-0039/Q-0190) and the sim-pinned discipline: **this is a pure port that
preserves every oracle balance number verbatim.** No number was invented or tweaked. The
pin is therefore **"preserved-from-oracle, unchanged"** — the oracle's own
`tools/sim`-pinned economy numbers (ore weights, `TOOL_POWER_GAIN`, `BASE_ROLL_MAX`, feature
weights 70/10/18/2, energy 60/1/10, vault 30/15/6 + 2000/1500 ladder, forge 3000/8000,
skill caps 10/20, luck rarity boosts, etc.) carry over exactly. Any future tuning must cite a
fresh simulated playthrough committed alongside the change (the mining economy sim ports as
part of the workflow slice, per ORDER 002 default #3).

## 7. Grid-encounters extension seam (first slice IMPLEMENTED)

The **first named-next extension** (Q-0198: depth-gated sparse encounters, loot/flavour-first,
combat a fast-follow reusing the creature/deathmatch engine). **The first slice has shipped** —
full design, sim-pin table, and evidence live in **`docs/design/mining-grid-encounters.md`**;
this section is the seam summary.

- `grid.py` models each `(x, y, z)` cell as a pure function of world seed + coordinates:
  `cell_at(seed, x, y, z) -> Cell(feature: CellFeature, featured_resource, richness)`, where
  `CellFeature ∈ {NORMAL, RICH, BARREN, TREASURE}`. The grid itself stays **seed-deterministic**
  (splitmix64 hash, process-independent — unit-tested including a subprocess check).
- **The seam (shipped):** `games/mining/core/encounters.py` layers an encounter resolver
  *on top of* the deterministic grid — `resolve(seed, cell, stats, energy, rng)` →
  `EncounterOutcome`. Encounter *kind* is keyed on `CellFeature` (NORMAL→hazard, RICH→rich
  vein, TREASURE→loot cache, BARREN→none); it is **sparse** (a per-action trigger, hazard
  chance depth-scaled ~7%→cap 25%). It reuses `equipment.EffectiveStats`
  `damage`/`defense`/`max_health` for single-exchange hazard combat and draws rewards from the
  existing ore/depth tables (no parallel economy), returning a pure result the workflow commits.
- **Live-roll vs deterministic — reconciled.** Q-0198 wants encounters to differ between two
  players' runs (live-roll). The resolver honours that *and* stays testable: `rng=None` derives a
  deterministic stream from the grid's `(seed,x,y,z)` splitmix64 convention (reproducible), while
  a host injects its **own** `rng` (seeded with player/action entropy) for the live-roll variance.
  Determinism is the default's property, not a constraint on the host.
- **Sim-pinned (new design, not oracle-ported).** Every balance number is justified by
  `games/mining/sim/encounters_sim.py` (276k-action sweep): ~11.6% encounter rate, a depth×gear
  danger gradient (bare miner clears the surface, is overwhelmed in the deep; earned gear never
  loses), no pay-to-win. Table + evidence: `mining-grid-encounters.md` §5.
- **Deferred to later slices:** multi-turn combat depth, the stateful hard depth-gate + cooldown
  (a host/workflow concern), and host wiring (navigator button / `ResultRender` + the audited
  apply-op). See `mining-grid-encounters.md` §7.

## 8. Verification

- `python3 bootstrap.py check --strict` → green (session card flipped from born-red last).
- `python3 -m pytest tests/mining/` → 62 passed. Covers: ore-weight/depth reweighting,
  mine-roll math, energy/capacity/vault formulas, skill caps + forced specialization, forge
  tier gating, the additive-safety invariant (zero skill/luck/depth_access/unbuilt/level-0 →
  byte-identical baseline), grid `cell_at` seed-determinism (incl. process-independence +
  negative-coord wrap), the fish-severance + injection point, recipes purity + injection, and
  a purity guard asserting the core imports zero discord/DB/host-layer deps.
