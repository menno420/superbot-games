# 2026-07-20 · inventory-bridge-slice2 — feat(inventory): wire gated fishing→mining exchange onto an audited verb (Option B, slice 2)

> **Status:** `complete`
>
> 📊 Model: Opus 4.8 · high · game-economy-service

Slice 2 of the shared cross-game inventory (Option B,
`docs/design-shared-cross-game-inventory.md`). Slice 1 (PR #180) landed the
config-gated `services/inventory_bridge.py` service seam but wired NOTHING onto a
live command path. This slice threads that exchange onto a real **audited verb** —
a `exchange` command in the fishing CLI ("walk your catch to the mining market") —
and routes **BOTH legs** of the money flow (the fishing-haul debit and the
mining-coin credit) through the SAME `services/audit.py` sink the sibling
`fishing_workflow.sell` / `mining_workflow.sell` legs already use, so the
cross-game money flow is reconstructable from one ledger.

It stays **CONFIG-GATED, DEFAULT OFF**. With `GAMES_INVENTORY_BRIDGE_ENABLED`
unset (the default) the verb is unavailable — it returns a clear "bridge is
disabled" response, changes nothing, records nothing, and does not appear in the
help surface — so the full suite is byte-unchanged when the flag is off. Nothing
goes live until the owner flips the flag. The exchange remains all-or-nothing and
non-destructive on error (never removes fish without crediting coins and emitting
both audit events), one-directional (fishing → mining only), and keeps the 6
coordinator-decided slice-1 defaults intact (gated-off default, bridged,
one-directional, V043 price, 1:1, fish never occupy the mining cap — sold for
coins).

## 💡 Session idea

💡 Slice 3 = the CLI surface / help-text polish for the verb — a discoverable
`exchange` help line + a "mining market" status/summary readout that surfaces the
credited mining-coin wallet in the fishing session, and a matching help-parity
pin, so a player can find and reason about the cross-game sale from the CLI itself
(this slice keeps the wallet internal and the help line gated behind the flag).

## ⟲ Previous-session review

Predecessors: **#180** (`9d8b22a`, inventory-bridge-slice1) landed the config-gated
`services/inventory_bridge.py` seam (`fish_market_value` reusing the V043 curve,
`exchange_fish_for_coins`, `bridge_enabled()` on `GAMES_INVENTORY_BRIDGE_ENABLED`)
with 26 tests but deliberately stopped at the seam — this slice picks up exactly
its `## 💡 Session idea` (wire the exchange onto a verb, route both legs through
the audit sink). **#178** (`e0cbbc7`, explore-verb-wiring) is the command-registration
pattern this slice mirrors: it wired the mining exploration engine onto a live
`explore` verb via the fishing/mining CLI `_ACTIONS`/`step` dispatch + a help line —
the same seam-onto-verb move, adapted here for a gated, cross-game exchange.
Green baseline re-run at base before writing: `python3 -m pytest -q` → 903 passed.

## ✅ Complete

Card born red (`in-progress`) in the first commit per the born-red discipline —
the claim + this card landed alone to hold the substrate-gate red; the audited
exchange (`exchange_fish_for_coins_audited`) + the gated `exchange` verb in the
fishing CLI + 19 tests + doc updates landed in the second commit. Verified green
before this flip: `python3 -m pytest -q` → **922 passed** (903 baseline + 19
new); `python3 bootstrap.py check --strict` → advisory-only (born-red HOLD was
the only exit-affecting item). PR **#181** opened ready-for-review; this final
commit flips the badge to `complete`, clearing the born-red HOLD so the green PR
can auto-land.
