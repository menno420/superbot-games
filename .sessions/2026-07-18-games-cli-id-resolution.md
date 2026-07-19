# 2026-07-18 · games-cli-id-resolution — feat(cli): case-fold dnd option ids + resolve multi-word display names to ids

> **Status:** `complete`
>
> 📊 Model: opus-4.8 · high · feature build

⚑ Owner-authorized code slice (menno420, live 2026-07-18): resolve TWO queued
owner-input **product** decisions from `docs/NEXT-TASKS.md` (§ "Owner-input
decisions queued (2026-07-18 overnight loop)") as one small, tested, autonomous
PR, applying each decision's stated default and FLAGGING it in the PR body for
the owner's asynchronous review. Both changes are reversible. Executed at branch
base `e0b8123` (#174, main HEAD).

**What this slice ships.**

- **Decision #4 [product] — case-fold dnd option ids.** The dnd CLI
  (`games/dnd/cli.py::_resolve_choice_id`) treated a capitalised option id as
  OFF-MENU and clamped to the scene's safe default (pinned `xfail` in the
  cross-CLI case-normalisation sweep). Owner-default applied: the CLI now
  case-folds a non-digit token against the width-capped SURFACED option ids, so
  `Advance_Escort` resolves to the same option as `advance_escort` — mirroring
  how the other game CLIs lower-case a token at their seam boundary (#158). Only
  the surfaced ids (the exact set the resolver would accept) are matched, so an
  id beyond the menu still clamps; a token matching NO surfaced id is still
  passed to the seam verbatim and clamps to the deterministic safe default (the
  "anything off-menu keeps you safe" guardrail is unchanged).

- **Decision #5 [product] — resolve multi-word display names → ids.** All game
  CLIs addressed items/species by single-token neutral id only; a multi-word
  display name ("Legendary Carp") no-oped. Owner-default applied: a new
  `games/fishing/core/species.py::resolve` maps a token to its neutral id —
  **id match first** (case-insensitive), then a case-insensitive **display
  name** match, else `None`. The fishing CLI's `sell` path is reworked to split
  a trailing integer as the quantity (mirroring the mining CLI's
  `sell <item> [qty]` grammar) and resolve the remaining (possibly multi-word)
  phrase through `resolve`, so `sell Legendary Carp 2` now commits. Id-based
  resolution is preserved (id wins, never shadowed by a display name), and the
  existing "Quantity must be a number" diagnostic is preserved via the same
  catalog-aware disambiguation the mining CLI's decision-#6 diagnostic uses (a
  trailing non-int token is a bad quantity only when the prefix already names a
  species yet the whole phrase does not). The **mining CLI needs no change**: its
  catalog key IS the lowercased display name, so multi-word names ("lucky
  charm") already resolve — so this slice touches only the genuine id≠display
  gap (fishing species) and does not collide with the mining qty-diagnostic
  (`_split_item_qty` / `_bad_quantity_token`) shipped in #172.

**Tests.**

- `tests/cross_cli/test_cli_case_normalisation.py` — the strict-`xfail` dnd case
  test is converted to a passing assertion and dnd is folded into the shared
  `CLI_CASES` sweep (a capitalised option id resolves identically to lowercase);
  the module docstring moves dnd from "Gap" to "Covered".
- `tests/fishing/test_cli.py` — the prior
  `test_sell_multiword_display_name_is_honest_noop` (which pinned the OLD no-op)
  is replaced by `test_sell_multiword_display_name_resolves_to_id_and_commits`,
  plus `test_sell_multiword_display_name_is_case_insensitive`,
  `test_sell_legend_carp_by_neutral_id_still_commits` (id path preserved), and
  `test_sell_unknown_multiword_name_is_honest_noop` (an unknown multi-word name
  reports "cannot be sold", not a false quantity error).
- `tests/fishing/test_theme_data.py` — four direct `species.resolve` unit tests
  (id wins, multi-word display name case-insensitive, single-word display name,
  unknown → `None`).
- `tests/cross_cli/EXPECTED_MIN_TESTS.txt` 4 → 5; `tests/fishing/EXPECTED_MIN_TESTS.txt`
  125 → 131; `docs/balance.md` regenerated (`python3 tools/gen_balance.py --write`).

## 💡 Session idea

⚑ Self-initiated. A "case-fold the token at the CLI boundary" fix and a
"resolve a display name to its neutral id" fix are the same move seen from two
angles: both let the player TYPE a natural surface form (a capitalised id, a
multi-word display name) that the mechanic layer keys on in one canonical shape.
The reusable discipline is to normalise at the CLI boundary and keep the seam
strict — never loosen the mechanic key. The guardrail that keeps it honest is
**id-wins**: try the exact (neutral) key first and only fall back to the
friendlier surface form when it misses, so a display name can never shadow a
real id and no ambiguity is introduced.

## ⟲ Previous-session review

The 2026-07-18 games-balance-curves slice (card
`2026-07-18-games-balance-curves`, PR #174) resolved queued balance decisions #1
and #7 from `docs/NEXT-TASKS.md`, landing main at `e0b8123`. This slice is the
next owner-authorized follow-through in the same queue: take the two remaining
**product** decisions (#4, #5), apply their stated defaults, flag them, and land
on green. Green baseline at branch base `e0b8123`: `python3 -m pytest -q` passes
(re-confirmed this session before editing).

## ✅ Landed (PR #175)

Shipped in PR [#175](https://github.com/menno420/superbot-games/pull/175)
(`claude/games-cli-id-resolution`), plus this card:

- `games/dnd/cli.py` — `_resolve_choice_id` case-folds a non-digit token against
  the surfaced option ids before the seam's clamp (decision #4).
- `games/fishing/core/species.py` — new `resolve(token)` (id-wins, then
  case-insensitive display name) + a `_BY_NAME` index built from the same table
  (decision #5).
- `games/fishing/cli.py` — `_do_sell` reworked to split a trailing integer as
  the quantity and resolve the (possibly multi-word) name via `species.resolve`,
  preferring the resolved id and preserving the "Quantity must be a number"
  diagnostic (decision #5).
- `tests/cross_cli/test_cli_case_normalisation.py` — dnd case pin un-xfailed
  (passing assertion) + folded into `CLI_CASES`; docstring dnd Gap → Covered.
- `tests/fishing/test_cli.py` — multi-word display-name resolution tests
  (commits / case-insensitive / id-still-commits / unknown no-op).
- `tests/fishing/test_theme_data.py` — direct `species.resolve` unit tests.
- `tests/cross_cli/EXPECTED_MIN_TESTS.txt` 4 → 5;
  `tests/fishing/EXPECTED_MIN_TESTS.txt` 125 → 131; `docs/balance.md`
  regenerated (`python3 tools/gen_balance.py --write`).
- `docs/NEXT-TASKS.md` — decisions #4 and #5 marked ✅ RESOLVED with the applied
  owner-defaults + PR link; the other queued items left untouched.

**Suite green:** `python3 -m pytest -q` = `868 passed` (no xfails — the dnd case
pin is now a passing assertion). **`bootstrap.py check --strict`** pre-flip = the
designed born-red hold on this card; the flip-to-complete commit clears it. No
seam / economy / balance number changed.
