# 2026-07-14 · night fix — clamp unhashable DM option_id in the dnd resolver

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T01:46:03Z · night-fix-dnd-resolver-unhashable

Bug-fix slice paying down the deferred #52 hardening item recorded at
docs/retro/close-out-world-games-2026-07-11.md:38: `resolve()` raised
`TypeError` on an unhashable `option_id` (a hand-built `DMChoice` with a
list/dict/set) via the `option_id in allowed_ids` set check at
`games/dnd/core/resolver.py:100` — the only input family that escaped
the bounded-menu clamp law instead of clamping. Reproduced this session
at main `bdc3445` (671-test HEAD, #114's merge):
`resolve(scene, DMChoice(option_id=['a','list']), xp=0, seed=1)` →
`TypeError: unhashable type: 'list'`.

Shipped exactly the retro's owed spec: the membership test is wrapped in
a try/except `TypeError` so an unhashable `option_id` is off-menu by
definition and falls into the EXISTING clamp branch (deterministic no-op
default, `clamped=True`, reward/event `None`) — no new constants, no
gameplay changes, no behavior change for any previously-non-raising
input. `tests/dnd/test_resolver_fuzz.py` gains a parametrized
unhashable/wrong-typed `option_id` sweep (list, dict, set,
nested-unhashable tuple, None, int; the hashable members pin
no-regression alongside the fix) asserting the suite's own
`_assert_clamped_noop` invariant across every catalog scene, and the
module docstring's "out of this suite's scope" carve-out is retired
honestly. `tests/dnd` floor 55 → 61; `docs/balance.md` regenerated
(gen-balance gate). Verified post-fix: the repro now returns the clamped
default (`make_camp`, `clamped=True`); full suite 671 → **677 passed**
locally; `gen_balance.py --check` green. Claim
`control/claims/night-fix-dnd-resolver-unhashable.md` self-released in
this flip commit (established precedent).

## 💡 Session idea

This fix's test sweep hand-rolls the same adversarial shapes
(list/dict/None/int payloads, injection strings) that
`tests/dnd/test_resolver_fuzz.py`'s `_INJECTION_SHAPES` and generator
kinds already encode — and any future fishing/mining/exploration
input-hardening suite will hand-roll them a third time. Adopt a **shared
adversarial-payload corpus module** (e.g.
`tests/shared/adversarial_corpus.py`): ONE maintained catalog of
wrong-typed payloads (unhashable containers, None/int/float/bytes,
opaque objects) and injection-shaped strings (prompt-injection prose,
control chars, confusables, path traversal), which every game's fuzzer
imports instead of maintaining a private copy — a new attack shape added
once immediately hammers every game's input seam. Dedupe check against
the used-idea list: the pinned-bug marker ledger tracks pinned wrong
behavior, the detector-trip registry tracks detector activations, the
sim-harness smoke registry tracks harnesses; none is a shared corpus of
adversarial INPUTS reused across suites. No card idea to date is.

## ⟲ Previous-session review

The previous session is the #113/#114 coverage wave, re-verified against
`origin/main` at `bdc3445`: #114 (squash `bdc3445`) delivered what its
card claims — `tests/dnd/test_cli_repl.py` and
`tests/dnd/test_menu_report.py` exist at HEAD, the card's 659 → **671
passed** matches this session's fresh baseline run (671 passed at
`bdc3445` before this slice), and the `tests/dnd` floor stood at 55 as
the card's bump left it. #113 (squash `73111d0`) chains consistently:
its 659-test end state is exactly #114's recorded start. Both cards are
`✅ complete` on main and both claims are absent from
`control/claims/` (README.md only at `bdc3445`) — notably with NO
deletion commit in main's history, because each wave's claim was created
and self-released inside its own PR, so the squash-merge collapsed it
to nothing on main. That's the self-release precedent working better
than the earlier follow-up-control-PR pattern (#105's cleanup), and
this slice repeats it.
