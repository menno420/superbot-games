# 2026-07-18 · mining-negqty-coverage — test(mining): pin CLI negative/non-integer-qty honest rejection

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus 4.x · high · test writing

⚑ Self-initiated: small game-improvement slice (owner night order 2026-07-18 —
land ONE contained, tested, independently-landable game-improvement slice as a
PR on green via auto-merge). Executed at branch base `bcaf032` (#161).

The standalone mining CLI's qty-taking verbs (`sell` / `build` / `skill`) share
one boundary split, `_split_item_qty`, whose test is
`args[-1].lstrip("-").isdigit()`. That test branches TWO WAYS on a bad quantity,
and neither edge was pinned. This slice investigates both, pins the true
behavior, and confirms no bug.

**(a) Negative quantity.** `sell iron -3`, `build forge -1` and `skill mining -2`
all PASS the isdigit test — `lstrip("-")` strips the sign, so the token parses as
a NEGATIVE int and is forwarded to the audited seam. The seam then rejects it one
layer deeper: `sell`/`skill` via their `qty <= 0` / `points <= 0` guards
("Quantity must be positive." / "Points must be positive."), and `build` via
`structures.build_cost` returning `None` for a level `< 0` ("Forge cannot be
upgraded from level -1."). Every one is an honest no-op — no coins moved, no
inventory/skill/structure change, no audit row (D2: a rejected action records
NOTHING). This is the same CLI→seam interaction PR #161 pinned for the fishing
CLI's `sell bass -2`; here it is pinned across all three mining qty verbs.

**(b) Non-integer quantity.** `sell iron abc`, `build forge xyz` and
`skill mining foo` FAIL the isdigit test, so `_split_item_qty` folds the trailing
token into the (multi-word) NAME and returns qty `None`. The unknown name then
simply does not resolve, and the seam rejects it ("iron abc cannot be sold." /
"forge xyz is not buildable." / "mining foo is not a skill branch.") — again a
clean no-op with zero state change and no row. Note this DIFFERS from the fishing
CLI, which int()-parses its qty at the boundary and emits a dedicated "Quantity
must be a number" message; the mining CLI has no such message because the token
becomes part of the name. The tests PIN the true mining behavior, not a
fishing-shaped expectation.

Scope: pure test additions to `tests/mining/test_cli.py` (6 tests — negative +
non-integer for each of `sell` / `build` / `skill`, asserting the honest message,
unchanged state, and zero audit rows) + the `tests/mining`
`EXPECTED_MIN_TESTS.txt` floor bump 196 → 202 + `docs/balance.md` regenerated
(its Test-suite-floors section pins that count). No CLI, seam, economy, or
balance number changes; the audited seam's `target`/message strings are
untouched.

## 💡 Session idea

⚑ Self-initiated. The investigation surfaced one deferred **UX** question, not a
bug: **should the mining CLI give a dedicated "quantity must be a number" message
for a non-numeric qty, the way the fishing CLI already does?** Today a
non-numeric trailing token silently folds into the item/structure/branch name, so
`sell iron abc` reports "iron abc cannot be sold" rather than naming the qty as
the problem. Both are honest no-ops (nothing is consumed, no row is recorded), so
this is a diagnostics-clarity call, not a correctness fix — and it interacts with
the deliberately multi-word name grammar (`build forge`, `skill mining`, and the
`sell iron pickaxe`-style names), where the last token is genuinely ambiguous
between "a qty" and "the tail of a name". Deferred as a follow-up backlog item:
**decide whether the mining CLI (and siblings) should distinguish a malformed-qty
token from an unknown-name token at the boundary** — if yes, a shared boundary
parser could surface the fishing-style message (seam untouched, no balance
change) and be pinned across CLIs; if no, keep the fold-into-name grammar as the
pinned contract (this slice's tests already make it explicit instead of silent).

## ⟲ Previous-session review

Target: games PR #161 (`bcaf032`, "test(fishing): pin CLI non-integer-qty +
multi-word-species handling") — this branch's base and main's current HEAD
(`git fetch origin main && git reset --hard origin/main` → `bcaf032`, confirmed).
Its load-bearing claim (the fishing CLI's `sell <species> [qty]` had two unpinned
edges — a non-integer qty, float `sell bass 1.5` and negative `sell bass -2`, and
a multi-word DISPLAY name `sell Legendary Carp 3` — and investigation found NO
bug: species are addressed by their neutral single-token id `legend_carp`, never
the display name, so the multi-word input honestly no-ops while `sell legend_carp
2` sells correctly) re-checks TRUE from this session's own reading of the shipped
tree, not its word: `tests/fishing/test_cli.py` carries the float
(`test_sell_with_float_qty_is_graceful`), negative
(`test_sell_with_negative_qty_is_honest_noop`) and multi-word
(`test_sell_multiword_display_name_is_honest_noop`) pins, all collected; the
`tests/fishing` floor reads 125 and `docs/balance.md`'s Test-suite-floors section
carries the matching `tests/fishing | 125` row; and the fishing seam/economy were
left untouched. Green baseline this HEAD: `842 passed, 1 xfailed` (re-run this
session). This mining slice pins the SAME CLI→seam negative-qty interaction one
game over, plus the non-integer edge, so the two are complementary and
non-overlapping — #161 covered fishing's `sell`, this covers mining's `sell` /
`build` / `skill`.
