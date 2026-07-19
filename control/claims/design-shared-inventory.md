# Claim · design-shared-inventory

- **Branch:** `claude/design-shared-inventory`
- **Scope:** Write ONE planning/design doc —
  `docs/design-shared-cross-game-inventory.md` — proposing a shared cross-game
  inventory that would let fishing catches reach the mining market. Planning
  output only: reads the real seams (the fishing inventory adapter
  `games/fishing/inventory/adapter.py`, the mining item catalog +
  `register_fish_species` in `games/mining/core/items.py`, the mining market
  `games/mining/core/market.py`, and the canonical **V043** fishing valuation
  in `games/fishing/core/economy.py` made canonical for mining by PR #174),
  names where they meet or fail to meet, lays out 2–3 options with honest
  reversibility/blast-radius tradeoffs, recommends one, and marks every genuine
  product-intent fork with `⚠️ OWNER PRODUCT CALL:`. **No game code changes** —
  docs-only DRAFT PR. This is the "shared cross-game inventory seam" latent fork
  queued in `docs/NEXT-TASKS.md` (§ "Next session" item 2).
- **Date:** 2026-07-19
- **Self-initiated:** ⚑ coordinator-directed design-doc slice (owner continue
  directive 2026-07-19): shared inventory = DESIGN DOC FIRST, no build.
