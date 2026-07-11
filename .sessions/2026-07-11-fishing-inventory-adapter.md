# 2026-07-11 · Fishing → shared inventory adapter — contract migration PR-2

> **Status:** `complete`
>
> 📊 Model: Claude Opus · 2026-07-11T01:13:29Z · fishing→shared-inventory adapter (contract migration PR-2)

## Goal

Deliver **PR-2** of the unified inventory/resource contract migration
(`docs/design/world-inventory-resource-contract.md` §4): a thin, pure **adapter** mapping
fishing's `Catch`/`CastOutcome` output onto the already-shipped `games/shared/inventory/`
§2 contract (PR #29), exercised by the shipped §7 conformance suite — as ONE merged-on-green
PR. Additive only: NEW adapter package, no change to `games/fishing/core/` internals, none
to `games/shared/inventory/`, none to mining.

The slice must:

- Add a pure, deterministic, stdlib-only adapter package (`games/fishing/inventory/`) that
  builds a fishing `ItemCatalog` from `species.py` DATA and maps `Catch → Stack`,
  `Catch → Grant`, `CastOutcome → Grant` (no bite → `EMPTY_GRANT`).
- Map each neutral `species_id` to a namespaced `ItemId` `fish.<species_id>` at the adapter
  boundary ONLY — no rename of any fishing/mining internal id (decide-and-flag, reversible).
- Keep every player-visible noun in `species.py`; the adapter only reads that data and
  relays it (Q-0267 — introduces NO new hardcoded noun).
- Carry values, never roll/scale them by a pay lever (Q-0039/Q-0190).
- Pass the shipped §7 `run_conformance` suite against the fishing catalog + a
  `ReferenceInventory` seeded from adapter grants.
- Bump the CI collected-count floor for the net-new `tests/fishing/` tests.

## Decide-and-flag (reversible, no owner sign-off)

- **Per-system catalog for now** — a fishing-local `ItemCatalog` built from `species.py`,
  NOT a global merged catalog. The §6 "one shared vs per-system catalog" owner-decision
  stays DEFERRED; per-system is the doc's own assumption and is reversible.
- **`fish.<species_id>` namespace mapping** at the adapter boundary only — no persisted id
  changes, no internal rename. The §6 ⚑ neutral-id-namespace/mining-rename owner-decision
  stays DEFERRED; this maps old↔new at the seam and is reversible.

## What shipped

- **`games/fishing/inventory/` pure adapter package** (stdlib-only, no Discord/DB/IO/RNG),
  the first consumer of the shared inventory seam (PR #29):
  - **`adapter.py`** — the fishing ↔ shared §2 mapping:
    - `item_id_for_species` / `species_id_for_item` — the `fish.<species_id>` namespace map
      at the adapter boundary, validated through the contract's `item_id()` guard; no
      internal id renamed.
    - `fishing_catalog() -> DictItemCatalog` — a per-system `ItemCatalog` built from
      `species.all_species()`, one `ItemMeta` per row with **name/emoji relayed straight
      from `species.py` DATA** and `value` = the row's `size_rank` (a carried data number,
      never rolled); `tags={"fish"}` reuses the namespace constant (no new noun).
    - `catch_to_stack(catch) -> Stack` — `Stack(fish.<id>, qty=1, attrs={"size", "size_rank"})`;
      per-instance `size` rides in `attrs` per contract §2c.
    - `catch_to_grant(catch) -> Grant` — one-stack grant, `progression=ProgressionDelta()`
      empty (fishing defines no XP/currency today — noted; the shape is ready).
    - `cast_to_grant(outcome) -> Grant` — no bite → `EMPTY_GRANT`, a bite → the catch's grant;
      total, never raises.
    - `reachable_item_ids()` — the theme-data guard surface (exactly `fish.<key>` per species).
  - **`__init__.py`** — pure-adapter docstring (fishing ↔ shared contract; no Discord/DB/IO),
    integrity floor, and the two reversible decide-and-flag calls.
- **`tests/fishing/test_inventory_adapter.py`** — **20 net-new tests**: every species → a
  valid neutral `ItemId`; the fishing catalog passes the shipped §7 `run_conformance`
  (round-trip identity, no-spend-lever, catalog-ids-neutral, capacity-in-distinct-types) +
  `assert_nouns_are_data_only` under a re-skin; `catch_to_stack`/`catch_to_grant` expected
  shape + determinism; `cast_to_grant` no-bite → `EMPTY_GRANT` (incl. a real resolver
  too-tired outcome) and a real resolved bite → one-stack grant; round-trip into
  `ReferenceInventory` (held qty / distinct types), `DefaultCapacityPolicy` status; a
  theme-data guard proving reachable ids track `species.py` (remove a row → `fish.pike`
  drops from the reachable set + catalog).
- **CI floor** bumped `210 → 230` in `.github/workflows/tests.yml` (`-lt` check + comment,
  `+ 20 (fishing inventory adapter)`). Full suite `python3 -m pytest tests/
  games/exploration/tests/ -q` → **230 passed**; `bootstrap.py check --strict` exit 0.
- **Design doc §4** migration path — PR-2 (fishing adapter) marked **SHIPPED** with the
  branch ref; Status badge (`plan`) + reachability left intact.
- **Untouched:** `games/fishing/core/` internals, `games/shared/inventory/`, mining — new
  code only. No new shared interface introduced (consumes the existing one), so no
  interface-change announcement needed.
- **Deferred (not resolved):** the §6 ⚑ owner-decisions (neutral-id namespace / mining
  rename; whether `currency` belongs in the contract; one shared vs per-system catalog) all
  stay owner-deferred; this PR's `fish.` mapping + per-system catalog are reversible calls.

## 💡 Session idea

PR-1 built the §7 conformance suite as a reusable adapter template; PR-2 is the first PR to
re-import it, and the whole adapter+tests landed in ~120 lines with zero change to either
migrated surface — evidence the claim-first shared-seam skeleton (neutral-id mechanics +
data-only nouns + a Protocol seam with a reference impl the conformance suite pins) makes an
adapter a near-mechanical slice. Worth capturing PR-2 as the worked example in the proposed
`docs/patterns/claim-first-shared-seam.md`: it shows a downstream adapter should be a pure
`domain-type → Stack/Grant` relay that *carries* every value and adds no noun, so the next
adapters (PR-3 mining catalog, PR-4 quest) start from a filled-in template rather than
re-deriving the shape.

## ⟲ Previous-session review

PR-1 (#29) stood up `games/shared/inventory/` with a reusable §7 conformance suite
explicitly designed for adapter PRs to re-import — this PR is the first consumer, proving
that discipline holds. The design doc §4 sequenced fishing first *because* it is already
neutral-id (`species.py`), so PR-2 is a pure mapping with no Q-0267 remediation, unlike the
mining catalog PR-3 that follows. This card is born-red and flips to `complete` only when
the adapter lands green.
