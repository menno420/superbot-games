# 2026-07-19 · design-shared-inventory — planning doc for a shared cross-game inventory (fishing → mining market)

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus 4.x · high · design-doc

A one-page design/planning doc (NOT a build). PR #174 made the fishing **V043**
sell curve (minnow 8 · bass 13 · pike 27 · legend_carp 80,
`games/fishing/core/economy.py`) the canonical valuation for a fish in the
mining market via `games/mining/core/items.py::register_fish_species` — but that
registration is called only from a test, and **no seam moves a caught fish into
`MiningState.inventory`**, so the canonical valuation is correct-by-construction
yet unreachable. `docs/NEXT-TASKS.md` (§ "Next session" item 2) queued the
missing "shared cross-game inventory" seam as a latent architecture fork needing
an owner design call before any build. This doc reads the real seams —
fishing's neutral-id adapter (`games/fishing/inventory/adapter.py`) onto the
already-shipped pure contract at `games/shared/inventory/`, vs mining's
lowercased-display-string catalog + market — states where they meet or fail,
lays out 3 options with honest reversibility / blast-radius, recommends one, and
flags every genuine product fork with `⚠️ OWNER PRODUCT CALL:` rather than
deciding it. Docs-only; no game code touched.

## 💡 Session idea

💡 When a valuation is made "canonical" (#174) but the seam that would exercise
it does not exist yet, the honest next artifact is a *design doc*, not a build:
the canonical-price decision quietly assumed a shared-inventory shape (one price
per species across games) that is itself an unmade product call. Writing the
seam down first — as options with reversibility, with the product forks pulled
out and explicitly left to the owner — keeps a latent balance decision from
hard-coding an architecture decision nobody signed off on. The design doc is the
place the two decisions get un-braided before code makes them for you.

## ⟲ Previous-session review

Predecessors: the 2026-07-19 decision sweep, PRs #170–#177, which emptied the
owner-input queue in `docs/NEXT-TASKS.md`. Directly upstream here: **#174**
(`e0b8123`) made the fishing V043 curve canonical for fish valuation in
`register_fish_species` (decision #7, reversible, flagged for owner review) and
flattened exploration ore-scaling (decision #1); **#177** (`1c63f3b`, current
main HEAD) refreshed `docs/current-state.md` truth-stamp and wrote the
"post-freeze forward plan" whose item 2 ("Route caught fish into a shared
cross-game inventory") is exactly the latent fork this doc scopes. Both #174's
canonical valuation and the shared-contract foundation at
`games/shared/inventory/` (migration PR-1, additive, unconsumed) are latent /
unwired today — this doc proposes how they meet. Green baseline re-run this
session before writing: `python3 -m pytest -q` = `868 passed`.

## 🔎 In progress

Card born red (`in-progress`) in the first commit per doctrine. The DRAFT PR
carries the doc for owner review; the card is intentionally **left red** — the
owner has not yet picked an option, and the `⚠️ OWNER PRODUCT CALL:` forks in
the doc are unmade by design. Do not flip to complete until the owner decides.
