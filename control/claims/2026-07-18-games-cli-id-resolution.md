# Claim · games-cli-id-resolution

- **Branch:** `claude/games-cli-id-resolution`
- **Scope:** Resolve two queued owner-input **product** decisions from
  `docs/NEXT-TASKS.md` (§ "Owner-input decisions queued (2026-07-18 overnight
  loop)") in one flagged PR, applying each decision's stated default:

  - **#4 [product] — dnd CLI clamps a capitalised option id to the safe
    default.** The dnd CLI (`games/dnd/cli.py::_resolve_choice_id`) treats a
    capitalised option id as OFF-MENU and clamps to the scene's safe default
    (behaviour pinned `xfail` in the cross-CLI case-normalisation sweep). Apply
    the owner-default: **case-fold option ids** at the CLI boundary so a
    capitalised id (`Advance_Escort`) resolves to the same surfaced option as
    its lowercase form, mirroring how the other game CLIs lower-case a token
    (#158). Un-xfail / convert the pinned test to a passing assertion and fold
    dnd into the sweep. A token matching NO surfaced id is still passed through
    verbatim and clamps (the "off-menu keeps you safe" guardrail is unchanged).

  - **#5 [product] — CLIs address items/species by single-token neutral id
    only.** A multi-word display name (e.g. "Legendary Carp") no-ops instead of
    resolving. Apply the owner-default: **add a display-name → id resolver**
    (`games/fishing/core/species.py::resolve`) so a display name (case-insensitive,
    multi-word) resolves to its neutral id, falling back to id-only when no
    display-name match — **id match is preferred** (only try display-name
    matching when the id lookup misses; no ambiguity). Route the fishing CLI's
    `sell` path through it (mirroring the mining CLI's `sell <item> [qty]` split
    so a multi-word name is addressable). The mining CLI already resolves
    multi-word names natively (its catalog key IS the lowercased display name),
    so no mining change is needed — and the fishing rework preserves the
    existing "Quantity must be a number" diagnostic via the same catalog-aware
    disambiguation the mining CLI's decision-#6 diagnostic uses (a trailing
    non-int token is a bad quantity only when the prefix already names a species
    yet the whole phrase does not).

  Narrow changes in `games/dnd/cli.py::_resolve_choice_id`,
  `games/fishing/core/species.py` (new `resolve`), and
  `games/fishing/cli.py::_do_sell`, plus tests in
  `tests/cross_cli/test_cli_case_normalisation.py`, `tests/fishing/test_cli.py`,
  and `tests/fishing/test_theme_data.py`. Both reversible; the resolver and the
  case-fold are product-semantics calls the owner can override. Flagged for
  owner review.
- **Date:** 2026-07-18 (owner-authorized code slice)
- **Self-initiated:** ⚑ owner-authorized game-improvement slice (menno420, live
  2026-07-18) — two queued owner-input product decisions resolved as one
  flagged PR.
