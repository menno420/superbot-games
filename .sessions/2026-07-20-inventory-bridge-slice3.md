# 2026-07-20 · inventory-bridge-slice3 — feat(inventory): CLI surface + read-only value preview for the fishing→mining bridge (Option B, slice 3)

> **Status:** `complete`
>
> 📊 Model: Opus 4.8 · high · feature build

Slice 3 of the shared cross-game inventory (Option B,
`docs/design-shared-cross-game-inventory.md`). Slice 1 (PR #180) landed the
config-gated `services/inventory_bridge.py` service seam; slice 2 (PR #181) wired
the MUTATING exchange onto a live, gated `exchange` verb. This slice adds the
surrounding **CLI surface + discoverability** — the genuinely-additive remainder,
not a duplicate of slice 2's interactive verb.

The one new affordance is a **read-only `value <species> [qty]` preview verb** in
the fishing CLI (`games/fishing/cli.py::_do_value`): it reports what a catch would
fetch at the mining market via `services/inventory_bridge.py::fish_market_value`
(the canonical V043 price), scaling 1:1 with quantity. Because a price quote is
pure information — no fish move, no coins move, no audit row — it is **available
regardless of the flag** and is always listed in `help_lines()`, so a player can
discover and reason about the cross-game sale before deciding to enable it.

The MUTATING `exchange` verb stays **CONFIG-GATED, DEFAULT OFF**: with
`GAMES_INVENTORY_BRIDGE_ENABLED` unset the mutation surface is byte-identical to
before the bridge existed, and all six §6 coordinator-decided defaults are
unchanged. **Scriptable/non-interactive surface judged not-applicable:** the games
hub (`python3 -m games`) and the per-game entry points are pure REPLs with **no
argv/subcommand dispatch**, so no one-shot CLI command was invented — the preview
is scriptable through the existing TTY-free `run_commands` driver (the real
codebase idiom, the same path the tests drive).

## 💡 Session idea

💡 Slice 4 = promote the bridge from a one-file seam toward the **shared inventory
core** the design doc sketches — either open the still-deferred bidirectional flow
(ore/gear → fishing, gated behind the same flag) or lift `fish_market_value` +
`exchange_fish_for_coins` into a game-neutral `services/inventory_core` so the
mining CLI can expose the symmetric "value your ore in fishing terms" preview from
the same source of truth, with the §6 owner forks (sellable-at-all, 1:1 rate)
surfaced as the gating product decision.

## ⟲ Previous-session review

Predecessors: **#180** (`9d8b22a`, inventory-bridge-slice1) landed the config-gated
`services/inventory_bridge.py` seam (`fish_market_value` reusing the V043 curve,
`exchange_fish_for_coins`, `bridge_enabled()` on `GAMES_INVENTORY_BRIDGE_ENABLED`) —
this slice reuses its pure `fish_market_value` verbatim for the read-only quote.
**#181** (`4afb915`, inventory-bridge-slice2) wired the MUTATING exchange onto the
gated `exchange` verb + `exchange_fish_for_coins_audited`, and its `## 💡 Session
idea` asked for exactly this CLI-surface/discoverability polish — picked up here as
the read-only preview + help/docs, while deliberately NOT duplicating its
interactive verb. Green baseline re-run at base before writing:
`python3 -m pytest -q` → 922 passed.

## ✅ Complete

Card born red (`in-progress`) in the first commit per the born-red discipline —
the claim + this card landed alone to hold the substrate gate red; the read-only
`value` verb + 18 tests + help/docs updates landed in the second commit. Verified
green before this flip: `python3 -m pytest -q` → **940 passed** (922 baseline + 18
new); `python3 bootstrap.py check --strict` → exit **0** (advisory-only + the
born-red HOLD, which was the only exit-affecting item until this flip). The
regenerated `docs/balance.md` (fishing suite floor 142 → 160) keeps the
`gen_balance --check` freshness gate green. PR **#182** opened ready-for-review;
this final commit flips the badge to `complete`, clearing the born-red HOLD so the
green PR can land. `.substrate/guard-fires.jsonl` left uncommitted (kit telemetry).
