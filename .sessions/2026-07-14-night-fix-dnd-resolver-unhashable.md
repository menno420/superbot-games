# 2026-07-14 · night fix — clamp unhashable DM option_id in the dnd resolver

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T01:42:18Z · night-fix-dnd-resolver-unhashable

Bug-fix slice picking up the deferred #52 hardening item recorded at
docs/retro/close-out-world-games-2026-07-11.md:38: `resolve()` raises
`TypeError` on an unhashable `option_id` (a hand-built `DMChoice` with a
list/dict) via the `option_id in allowed_ids` set check at
`games/dnd/core/resolver.py:100` — the only input family that escapes
the bounded-menu clamp law instead of clamping to the scene's
deterministic no-op default. Reproduced this session at main `bdc3445`
(671-test HEAD, #114's merge):
`resolve(scene, DMChoice(option_id=['a','list']), xp=0, seed=1)` →
`TypeError: unhashable type: 'list'`.

Plan, exactly per the retro's owed spec: a 1-line try/except around the
membership test so an unhashable `option_id` is treated as off-menu and
falls into the EXISTING clamp branch (no new behavior, no new constants,
no gameplay changes); extend `tests/dnd/test_resolver_fuzz.py` with
unhashable-and-wrong-typed `option_id` payloads (list, dict, None, int,
set) asserting the same `_assert_clamped_noop` invariant, and retire the
docstring's "out of this suite's scope" carve-out honestly; bump the
`tests/dnd` floor and regenerate `docs/balance.md` in the same push.

Self-release note: this slice's claim file
(`control/claims/night-fix-dnd-resolver-unhashable.md`) is deleted in
this card's flip commit, per the established precedent.
