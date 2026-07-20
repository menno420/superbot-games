# 2026-07-20 · inventory-bridge-slice1 — feat(inventory): config-gated fishing→mining bridge service seam (Option B, slice 1)

> **Status:** `complete`
>
> 📊 Model: Opus 4.8 · high · game-economy-service

Slice 1 of the shared cross-game inventory. The merged design doc
(`docs/design-shared-cross-game-inventory.md`, PR #179) recommended **Option B**:
a config-gated, reversible **bridge/exchange service** that lets a fish caught in
the fishing world be sold at the mining market for coins, at the canonical **V043**
fish valuation (landed in PR #174). This slice adds only the **service seam** —
`services/inventory_bridge.py` — with nothing wired into a live CLI/command path
(that is a later slice). The module exposes a PURE valuation function
(`fish_market_value`, reusing `games.fishing.core.economy.sell_value` — the exact
V043 curve #174 wired into the mining market via `items._fish_value`), a
config-gated exchange (`exchange_fish_for_coins`, moving fish from a real
`FishingState.haul` and crediting coins on a real `MiningState`, 1:1 at V043,
all-or-nothing/non-destructive on error, a no-op when the flag is OFF), and a
default-OFF config flag (`GAMES_INVENTORY_BRIDGE_ENABLED`, read from the env).

The 6 `⚠️ OWNER PRODUCT CALL` forks were resolved to the most conservative,
reversible defaults (coordinator-decided, owner continue directive 2026-07-20):
(1) fish sellable at the mining market YES **in principle** but the whole path is
CONFIG-GATED OFF BY DEFAULT — no existing gameplay changes until enabled;
(2) BRIDGED holds (two per-game inventories, a service pipes between them), not a
unified store; (3) ONE-DIRECTIONAL (fishing → mining only); (4) V043 canonical
valuation as the fish's mining-market coin value; (5) 1:1 at the shared V043 price
(no currency/XP conversion); (6) N/A by design — the bridge SELLS fish for coins,
never deposits fish objects into the mining pack, so no fish occupies the mining
capacity cap. All reversible: flip the flag off or delete the one file.

## 💡 Session idea

💡 The natural next slice is to wire `exchange_fish_for_coins` onto a live
command path (a "walk your catch to the market" verb) and route BOTH legs — the
fishing-haul debit and the mining-coin credit — through the existing
`services/audit.py` sink, exactly as the sibling `fishing_workflow.sell` /
`mining_workflow.sell` legs already audit, so the cross-game money flow becomes
reconstructable from one ledger instead of two.

## ⟲ Previous-session review

Predecessors: **#178** (`e0bcf3c`, explore-verb-wiring) threaded the mining
exploration engine onto a live `explore` verb — the pattern this slice mirrors in
spirit (a seam that makes an already-decided capability reachable, no new balance
numbers), except this slice deliberately stops at the seam and does NOT wire a
verb yet. **#179** (`cb1b546`, this branch's base and current main HEAD) is the
one-page design doc that recommended Option B and flagged the 6 owner product
calls this slice now resolves to their conservative, reversible defaults. Upstream
of both, **#174** made the fishing V043 curve canonical for a fish's mining-market
price — the valuation this bridge reuses directly rather than re-deriving. Green
baseline re-run at base before writing: `python3 -m pytest -q` → 877 passed.

## ✅ Complete

Card born red (`in-progress`) in the first commit per the born-red discipline —
the claim + this card landed alone to hold the substrate-gate red; the bridge
module + 26 tests + doc updates landed in the second commit. Verified green
before this flip: `python3 -m pytest -q` → **903 passed**;
`python3 bootstrap.py check --strict` → exit 0 (advisories only). PR **#180**
opened ready-for-review; this final commit flips the badge to `complete`,
clearing the born-red HOLD so the green PR can auto-land.
