# 2026-07-14 · night build — ci: preflight --flip derives the session card from the branch diff

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T04:40:39Z · night-flip-card-parity

Build slice from #131's card idea, verified fresh at branch base `b7b1062`:
`--flip`'s step 4 ran bare `bootstrap.py check --strict`, inheriting
strict's newest-by-mtime card selection (`latest_session_log`,
bootstrap.py ~1939) — the wrong card exactly when it matters (touched
bystander card, groom, fresh checkout equalizing mtimes): a green
`--flip` that never examined the branch's own card.

Shipped card-selection parity in `tools/preflight.py`: under `--flip`,
session cards ADDED vs `origin/main...HEAD` (merge-base, `--diff-filter=A`,
README excluded — the substrate gate's own derivation grammar) are
derived BEFORE any gate runs. Exactly one → step 4 becomes
`check --strict --session-log <card>` with a banner naming the derived
card; multiple → loud fail-fast error listing them (a flip grades ONE
card; no suite pass wasted); zero (control-fast-lane tree) → today's
bare strict behind an explicit "newest-by-mtime card fallback" banner.
Default 3-step mode byte-compatible; `tests.yml` never runs `--flip`.

Floor `tests/tools` 31 → **35** (floor==collected): one-card wiring pins
`--session-log` on the exact strict argv; multi-card pins SystemExit(1)
with ZERO gates run; zero-card re-pins bare strict + fallback banner +
derivation-runs-first; a REAL-git pin of the card idea's scenario (temp
repo, synthetic `refs/remotes/origin/main`, branch adds an older-NAMED
card while a main-side bystander holds the freshest mtime — derivation
returns exactly the branch's card, README and not-added cards excluded);
plus a pure `_pick_flip_card` pin. `docs/balance.md` regenerated BEFORE
flip; suite **794 → 798 passed** locally; preflight green. Mid-slice
dogfood: `--flip` on this very branch derived
`.sessions/2026-07-14-night-flip-card-parity.md` and held red on its
in-progress badge — the designed HOLD, now guaranteed to grade the RIGHT
card. Claim `control/claims/night-flip-card-parity.md` self-released
here.

## 💡 Session idea

The card-lane derivation now exists TWICE: the substrate gate's generated
workflow shell (bootstrap.py's heredoc: added/modified/deleted card
loops, `--diff-filter` grammar, README pathspec) and this slice's Python
re-implementation in `tools/preflight.py` — and they can drift (preflight
mirrors only the ADDED lane; a branch that merely MODIFIES a card — every
close-out flip — falls to the mtime fallback locally while CI runs the
locked-door gate per modified card, and a card DELETION reds in CI but is
invisible to `--flip`). Single-source it: give bootstrap a
`check --strict --cards-from-diff <base-ref>` lane that implements the
FULL card loop (each added card via the added-card lane, each modified
card via the locked door, deletions hard-red) in Python, have the
generated workflow call THAT instead of open-coding shell, and point
preflight `--flip` at the same lane — derivation grammar written once,
local/CI parity by construction. Dedupe check against all 2026-07-14
cards' 💡 lines: #128's idea ADDED step 4, #131's idea (this slice) made
step 4 grade the branch's added card; no card touches the shell/Python
derivation duplication, the modified-card local gap, or a
`--cards-from-diff` bootstrap lane; the stamp-scaffold, telemetry
backfill, golden-corpus, and registry ideas are elsewhere entirely.

## ⟲ Previous-session review

Previous slice is #132 (`claude/night-quest-completability`, squash
`b7b1062`, this branch's base). Same-night-run lineage, discount
accordingly; what I verified independently: its 6 tests collect and pass
at my base (`tests/exploration` floor 23 == collected; they are inside
this slice's 794-passing baseline), the sweep's loops are genuinely
bounded by each quest's own `sum(required)` (read
`_walk_to_completed`, tests/exploration/test_quest_completability.py
~43–80), and the headline-collection shape (failures gathered with
quest id + tier + stall reason, asserted empty) fails informatively by
construction. Two honest dings: (1) `_walk_to_completed` always takes
`pending[0]` — the sweep proves ONE canonical path per quest×tier
completable, not order-independence; a quest whose objectives interact
order-sensitively could pass the sweep yet stall a player who acts in a
different legal order. (2) `test_every_quest_budget_fits_the_energy_bar_
at_every_difficulty` is static arithmetic over `TUNABLES`
(budget×cost ≤ bar), not a driven drain — the card is upfront about
this (its own 💡 concedes no rest op exists on the seam), but the
starvation claim is therefore weaker than the completability claim the
title makes.
