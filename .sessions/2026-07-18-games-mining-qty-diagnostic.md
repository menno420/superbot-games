# 2026-07-18 · games-mining-qty-diagnostic — feat(mining-cli): add "Quantity must be a number" diagnostic

> **Status:** `complete`
>
> 📊 Model: Claude Opus 4.x · high · feature build

⚑ Owner-authorized code slice (menno420, live 2026-07-18): resolve ONE queued
owner-input decision from `docs/NEXT-TASKS.md` as its own small, tested,
autonomous PR, applying the decision's stated default and FLAGGING it in the PR
body for the owner's asynchronous review. The change lives in
`games/mining/cli.py`; it is reversible. Executed at branch base `99cbc59`
(#171, main HEAD).

**What this slice ships.**

- **Decision #6 [UX] — mining CLI "Quantity must be a number" diagnostic.**
  Unlike the fishing CLI (which `int()`-parses the qty at its input boundary and
  says "Quantity must be a number, got X"), the mining CLI's `_split_item_qty`
  test `args[-1].lstrip("-").isdigit()` folds a non-integer trailing token into
  the multi-word item name, so `sell diamond xyz` was rejected as an unknown
  item ("`diamond xyz` cannot be sold") rather than flagged as a bad quantity.
  Owner-default applied: add the diagnostic to the mining CLI's `sell` path,
  with the **disambiguation rule** that resolves mining's multi-word-name / qty
  overlap — a trailing non-int token is flagged as a bad quantity **only** when
  the tokens BEFORE it already name a known catalogued item (`items.lookup`) AND
  the whole phrase does not. So `sell iron abc` → "Quantity must be a number,
  got 'abc'." (remainder `iron` is a known resource), while a genuine multi-word
  item name (`sell iron pickaxe` — a real TOOL in the catalog) still resolves as
  the item ("… cannot be sold", no false quantity error), and a truly unknown
  single-token name (`sell foobar`) still reports "cannot be sold". The negative
  path (`sell iron -3`) is unchanged — the sign survives `lstrip("-")`, so it
  parses as an int and the seam's non-positive guard rejects it one layer
  deeper. Reversible; flagged for owner review.

**Tests.** `tests/mining/test_cli.py` — the prior
`test_sell_non_integer_qty_folds_into_name_and_no_ops` (which pinned the OLD
"folds into name → cannot be sold" behavior) is updated to assert the new
diagnostic, plus new cases: a genuine multi-word item name still resolves as the
item (no false quantity error), and an unknown single-token name still reports
"cannot be sold". Mirrors the fishing CLI's `test_sell_with_non_numeric_qty_is_
graceful`. The build / skill non-integer-fold tests are untouched (scope is the
sell "item" path, matching the decision's framing). No seam / economy / balance
number changed.

## 💡 Session idea

⚑ Self-initiated. Two CLIs that share a "sell `<thing>` `[qty]`" grammar can
diverge in their error ergonomics precisely because their PARSERS differ:
fishing keys on a single-token id, so a bad qty is unambiguous at the boundary;
mining allows a multi-word name, so the same bad qty is grammatically
indistinguishable from "part of a longer name" until you consult the catalog.
The reusable move is to make the diagnostic *catalog-aware* rather than
*position-only* — flag a trailing token as a botched quantity only when the
prefix already resolves to a known name and the whole phrase does not, so the
error message follows the player's evident intent without ever false-flagging a
real (longer) name.

## ⟲ Previous-session review

The 2026-07-18 build-structure-audit-ledger slice (card
`2026-07-18-games-build-structure-audit-ledger`, PR #171) resolved queued
decisions #3 and #8 from `docs/NEXT-TASKS.md`, landing main at `99cbc59`. This
slice is the next owner-authorized follow-through in the same queue: take one
more queued owner-input decision (#6), apply its stated default, flag it, and
land on green. Green baseline at branch base `99cbc59`: `853 passed, 1 xfailed`
(`python3 -m pytest -q`, re-confirmed this session before editing).

## ✅ Landed (PR #172)

Shipped in PR [#172](https://github.com/menno420/superbot-games/pull/172)
(`claude/games-mining-qty-diagnostic`), plus this card:

- `games/mining/cli.py` — `_do_sell` now consults the item catalog before
  folding a trailing non-int token into the name: a new private
  `_bad_quantity_token` helper flags "Quantity must be a number, got X" only
  when the tokens before it resolve via `items.lookup` to a known catalogued
  item AND the whole phrase does not (decision #6). On a flag it returns an
  `ok=False` seam-shaped `mw.TradeResult`, so nothing mutates and no audit row
  is recorded — mirroring the fishing CLI's boundary diagnostic. `build` /
  `skill` fold behavior untouched.
- `tests/mining/test_cli.py` — the prior
  `test_sell_non_integer_qty_folds_into_name_and_no_ops` (which pinned the OLD
  "cannot be sold" fold) is replaced by
  `test_sell_non_integer_qty_with_known_item_flags_bad_quantity` (asserts the
  new "Quantity must be a number, got 'abc'" flag, and that the old unknown-item
  message is gone), plus
  `test_sell_genuine_multiword_item_name_still_resolves_no_false_quantity_error`
  (`sell iron pickaxe` → "cannot be sold", no false quantity flag) and
  `test_sell_unknown_single_token_item_still_reports_unknown_item` (`sell
  foobar` → "cannot be sold"). Net +2 tests.
- `tests/mining/EXPECTED_MIN_TESTS.txt` 202 → 204; `docs/balance.md`
  regenerated (`python3 tools/gen_balance.py --write`).
- `docs/NEXT-TASKS.md` — decision #6 marked ✅ RESOLVED with the applied
  owner-default + PR link; the other queued items left untouched.

**Suite green:** `python3 -m pytest -q` = `855 passed, 1 xfailed` (+2 from the
net test change). **`bootstrap.py check --strict`** pre-flip = the designed
born-red hold on this card; this flip-to-complete commit clears it so the gate
goes green and the auto-merge apparatus lands the squash. No seam / economy /
balance number changed.
