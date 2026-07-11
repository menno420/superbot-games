# superbot-games · status

updated: 2026-07-11T01:35:32Z
phase: fishing spot biomes shipped — the resolver's `spot_id` argument now carries meaning via a data-driven `games/fishing/core/spots.py` catch-profile table; READY PR to main (green-pending)
health: green — full suite 248 pure-domain tests pass (79 mining + 44 fishing core + 20 fishing inventory adapter + 48 exploration + 57 tests/shared/inventory/); `bootstrap.py check --strict` exit 0; sim deterministic
last-shipped: fishing spot biomes (data-driven, sim-pinned) — `games/fishing/core/spots.py` (tide_pool / dock / deep_water) biases the catch via per-species weight multipliers + a per-spot bite modifier; `resolve_cast` reads the profile deterministically; neutral default identity preserves the skeleton fixtures; no pay-to-win (every spot leaves the common species reachable at zero gear)
orders: acked=001,002 done=001,002
blockers: none
notes: CI count floor bumped 230 → 248 (+18 spot-biome tests). Existing fishing + adapter tests stayed green UNCHANGED — `dock` is a neutral identity profile, so the skeleton's dock-keyed determinism fixtures reproduce byte-for-byte. Design doc `docs/design/fishing-catch-skeleton.md` gained a `## Spot biomes` section + a §5b per-spot sim-pin table. Species ids unchanged, so the fishing→shared-inventory adapter (`games/fishing/inventory/`) is untouched.

## Boot record
Landed on origin/main HEAD `773fab0` (PR #33 fishing → shared inventory adapter; PR #31
mining narration→data; PR #29 shared inventory seam PR-1; PR #28 theme-slot audit; PR #25
fishing skeleton). Branch `feat/fishing-spot-biomes` off origin/main. This seat owns all of
`games/**` and reports here (single-seat status file).

## Last shipped — fishing spot biomes (2026-07-11, data-driven catch profiles)
- **`games/fishing/core/spots.py`** — the second theme-data table (mirrors `species.py`): a
  `Spot` frozen dataclass + three neutral-id biomes (`tide_pool` / `dock` / `deep_water`),
  each a catch profile of per-species weight multipliers + a `bite_bias`. `dock` is the
  neutral identity spot; the flanks bias small/common vs big/rare. `profile_for` falls back
  to `DEFAULT_SPOT` (exact identity) for an unknown/`None` id, no raise.
- **`games/fishing/core/catch.py`** — `resolve_cast` applies the spot profile to the bite
  roll (`+bite_bias`, floored at `MIN_BITE_CHANCE`) and the weighted species pick
  (`×multiplier_for`, orthogonal to the earned-gear lever). Narration assembled from spot +
  species DATA. Default profile → the skeleton's mechanical outcome byte-for-byte.
- **Sim + tests** — `catch_sim.py` sweeps each spot × tier and pins per-spot bounds; +18
  tests (`test_spots.py`, extended `test_catch_sim.py`) cover neutral ids, per-spot fair
  access, data-swap-not-determinism, unknown→default, and the ordered biome gradients.
- **No pay-to-win, per spot:** every weight multiplier is strictly positive and bite chance
  is floored, so no biome gates a species — a zero-gear angler lands the whole table at
  every spot (Q-0039/Q-0190).

## Orders
`orders: acked=001,002 done=001,002`
- ORDER 001 — done (merged #24). ORDER 002 — done (superseded by Q-0265).

## Queue (inherited)
- done: fishing skeleton (#25); inventory contract design doc (#26); theme-slot audit (#28);
  inventory seam PR-1 (#29); mining narration table R1 (#31); inventory migration PR-2 —
  fishing adapter (#33); **fishing spot biomes** (this PR).
- next (inventory migration): **PR-3** mining catalog adapter (closes the Q-0267 §1a gap) →
  **PR-4** quest adapter → **PR-5** encounter typed grant → **PR-6** fish→mining bridge fix.
  Also queued (theme-audit roadmap): R2 mining stray-literal sweep; R3 fishing status
  scaffold; R4 de-dupe count-in-prose. Fishing follow-ups: a richer species table (more
  rows / size records) and multi-cast state (streaks, per-spot depletion) stay deferred (§7).
