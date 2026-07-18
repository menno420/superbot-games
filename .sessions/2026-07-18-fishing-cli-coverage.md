# 2026-07-18 · fishing-cli-coverage — test(fishing): pin CLI non-integer-qty + multi-word-species handling

> **Status:** `complete`
>
> 📊 Model: Claude Opus 4.x · high · test writing

⚑ Self-initiated: small game-improvement slice (owner night order 2026-07-18 —
land ONE contained, tested, independently-landable game-improvement slice as a
PR on green via auto-merge). Executed at branch base `b205c79` (#160).

The standalone fishing CLI's `sell <species> [qty]` argument handling had two
unpinned edges. This slice investigates both, pins the true behavior, and
records the one product question the investigation surfaced.

**(a) Non-integer quantity.** `sell bass 1.5` and `sell bass abc` fail the
`int()` parse at the CLI boundary → honest "Quantity must be a number, got …"
no-op (no crash, no state change, no audit row). `sell bass -2` PARSES as an int
but is rejected one layer deeper by the audited seam's non-positive guard →
"Quantity must be positive." no-op. Only `sell bass abc` (a word) was pinned
before; the float and negative paths were not. Now pinned.

**(b) Multi-word species.** The task flagged `sell Legendary Carp 3` as a
possible latent bug (like the exploration one #160 fixed). Investigation:
**there is no bug, and no multi-word species is reachable by the CLI's grammar.**
Species are addressed by their *neutral single-token id*
(`minnow`/`bass`/`pike`/`legend_carp` — `games/fishing/core/species.py`), which
is exactly what the seam's `sell()` and `economy.is_sellable()` key on. The
string "Legendary Carp" is only the *display name* of `legend_carp`; it is never
an input token. So `sell Legendary Carp 3` tokenises to species `legendary` +
qty `Carp`, and honestly no-ops on the `int("Carp")` parse ("Quantity must be a
number, got 'Carp'.") with zero state change — while `sell legend_carp 2` sells
that very species correctly (80 coins each). The mis-parse is the *current,
honest* behavior of a single-token grammar, not a silent misfire: nothing is
consumed, no wrong species is touched, no row is recorded.

Scope: pure test additions to `tests/fishing/test_cli.py` (float qty, negative
qty, the multi-word display-name no-op, and a positive `legend_carp`-by-id sell
proving the species IS reachable) + the `tests/fishing`
`EXPECTED_MIN_TESTS.txt` floor bump 121 → 125 + `docs/balance.md` regenerated
(its Test-suite-floors section pins that count). No CLI, seam, economy, or
balance number changes.

## 💡 Session idea

The investigation surfaced one deferred **product-semantics** question, not a
bug: **should the fishing CLI (and its siblings) accept a species' multi-word
DISPLAY name as sell input, not only its neutral id?** Today `sell legend_carp`
works and `sell Legendary Carp` honestly no-ops. Resolving display names would
need a name→id alias/lookup at the CLI boundary (join the pre-qty tokens, match
case-insensitively against `species.get(...).name`), and it interacts with the
grammar's optional trailing qty (is the last token a qty or the tail of a
name?), so it is a UX design decision, not the mechanical fix this slice takes.
Deferred as a follow-up backlog item: **decide whether game CLIs should resolve
display names to ids for the `sell` verb** — if yes, add a shared boundary
resolver (seam untouched, no balance change) and pin the round-trip across
CLIs; if no, keep the id-only grammar as the pinned contract (this slice's
tests already make it explicit instead of silent).

## ⟲ Previous-session review

Target: games PR #160 (`b205c79`, "test: pin cross-CLI case-normalisation
invariant (guards the #158 drift class)") — this branch's base and main's
current HEAD (`git reset --hard origin/main` → `b205c79`, confirmed). Its
load-bearing claim (a parametric sweep drives every game CLI's real entry point
with a lowercase token and its CAPITALISED twin and asserts an IDENTICAL
committed outcome, guarding the #158 case-drift class across CLIs, and it
surfaced + fixed a real latent instance in the exploration CLI's `offer`/`act`
boundaries) re-checks TRUE from this session's own reading of the shipped tree,
not its word: `tests/cross_cli/test_cli_case_normalisation.py` is present and
collected, `games/exploration/cli.py` lower-cases the `offer`/`act` tokens at
the boundary (seam untouched, only case ever normalised), the dnd gap is xfailed
as the documented off-menu-safe-clamp product semantic, `tests/cross_cli` is
registered in `tests/EXPECTED_SUITES.txt` with its own floor, and
`docs/balance.md` carries the new suite row. Green baseline this HEAD:
`838 passed, 1 xfailed`. The fishing CLI's `sell` is one of the CLIs that sweep
already pins as *case-correct*; this slice pins an ADJACENT, previously-uncovered
axis (non-integer + multi-word qty/species parsing), so the two are complementary
and non-overlapping.
