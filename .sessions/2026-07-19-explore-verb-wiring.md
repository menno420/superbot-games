# 2026-07-19 · explore-verb-wiring — feat(mining): wire the exploration engine onto a live `explore` verb

> **Status:** `complete`
>
> 📊 Model: Claude Opus 4.x · high · feature-wiring

The mining **exploration engine** (`games/mining/core/exploration.py`) already
resolves weighted, biome-gated, loadout-aware outcomes — but nothing in a
command path reaches it: `explore_from_state` was live only under test. This
slice adds the missing seam. `services/mining_workflow.py` gains an `explore()`
op that feeds the player's real position (`world.biome_for_depth(state.depth)`)
and equipped gear/consumables into `exploration.explore_from_state`, grants (or,
for a hazard, debits — never below zero) the resolved `(item, amount)` into
`MiningState.inventory`, and records exactly one audit row on a committed delta
while treating a "found nothing" roll as an honest no-op (`ok=False`, no row,
mirroring `mine`'s empty-roll discipline, D2). `games/mining/cli.py` routes a new
`explore` verb through `_ACTIONS` (`_do_explore`) with a help line. **The
flattened `1 + power * TOOL_POWER_GAIN` ore-scaling curve goes live to players
via this path** — the faucet the engine already computes becomes reachable.
Behavioural tests cover the committed find, the no-op, the zero-clamped hazard,
the biome-for-depth threading, and determinism; `services/tests` floor 221→228,
`tests/mining` floor 207→209, and `docs/balance.md` regenerates to pin them.

## 💡 Session idea

💡 A weighted-outcome ENGINE that is only ever driven from tests is a latent
faucet: its balance (here the flattened `1 + power*0.0625` ore curve) is already
"decided" in code yet mints nothing, so the decision is untested against real
play. The honest way to make such an engine live is a thin verb seam that threads
the player's *real* state (depth→biome, equipped loadout) into it and audits the
committed delta exactly as the sibling verbs do — no new balance numbers, just
reachability — so the pre-existing curve becomes observable and testable on a
live path instead of silently assumed correct.

## ⟲ Previous-session review

Predecessors: PRs **#170–#177**, the 2026-07-19 decision sweep + docs refresh
that emptied the owner-input queue. Directly upstream: **#174** (`e0b8123`)
flattened the exploration ore-scaling curve to `1 + power * TOOL_POWER_GAIN`
(decision #1) — the very curve this slice now routes to players — and made the
fishing V043 valuation canonical (decision #7); **#177** (`1c63f3b`, this
branch's base and current main HEAD) refreshed `docs/current-state.md` and wrote
the post-freeze forward plan. The exploration engine landed and was tuned across
that sweep but stayed test-only; this slice supplies the command seam that makes
it reachable. Green baseline re-run at base before writing: `python3 -m pytest -q`.

## 🔎 In progress

Card born red (`in-progress`) in the first commit per the born-red discipline —
the claim + this card land alone to hold the DRAFT PR red; the explore code +
tests + regenerated `docs/balance.md` land in the second commit. The PR carries
the wiring for owner review of the now-live curve; the card is intentionally
**left red** and is not flipped to complete this session (owner reviews the
explore diff before it flips).
