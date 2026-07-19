# Claim · games-mining-qty-diagnostic

- **Branch:** `claude/games-mining-qty-diagnostic`
- **Scope:** Resolve queued owner-input decision **#6 [UX]** from
  `docs/NEXT-TASKS.md` — the mining CLI has no "Quantity must be a number"
  diagnostic (unlike the fishing CLI): a non-integer trailing qty folds into the
  multi-word item name (`_split_item_qty`) and is rejected as an unknown item
  ("… cannot be sold") rather than flagged as a bad quantity. Apply the stated
  owner-default: add the diagnostic to the mining CLI's `sell` path (mirroring
  the fishing CLI's `int()`-at-the-boundary "Quantity must be a number, got X"),
  with the disambiguation rule that resolves mining's multi-word-name/qty-slot
  overlap — a trailing non-int token is flagged as a bad quantity **only** when
  the tokens before it already name a known catalogued item AND the whole phrase
  does not (so a genuine multi-word item name like `iron pickaxe` still resolves,
  no false quantity error; a truly unknown name still reports "cannot be sold").
  One narrow change in `games/mining/cli.py::_do_sell` + a private helper; tests
  in `tests/mining/test_cli.py` (the prior "folds into name" sell test is
  updated to the new flagged behavior + genuine-multiword and unknown-item cases
  added). Reversible; flagged for owner review. No seam / economy / balance
  change.
- **Date:** 2026-07-18 (`date -u` = Sat Jul 18 2026, owner-authorized code slice)
- **Self-initiated:** ⚑ owner-authorized game-improvement slice (menno420, live
  2026-07-18) — one queued owner-input decision resolved as its own flagged PR.
