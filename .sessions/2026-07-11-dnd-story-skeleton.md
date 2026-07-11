# 2026-07-11 · D&D story game — walking skeleton (bounded-menu resolver)

> **Status:** `complete`
>
> 📊 Model: Opus 4.8 · 2026-07-11T14:00:16Z · D&D walking skeleton (bounded-menu resolver)

## Goal

Ship the FIRST code slice of the D&D story game designed in PR #38
(`docs/design/dnd-story-design.md`): the smallest end-to-end **walking skeleton** —
one scene, one ≤4-option menu, one deterministic resolver — that makes the design's
**bounded-menu law** (Q-0040 / D-0007) executable. The AI Dungeon Master's entire
authority is to pick one id from a pre-approved, hard-capped menu; deterministic code
owns every outcome it narrates; any off-menu / hallucinated / malformed / null DM
output CLAMPS to a deterministic no-op. Pure domain only (no workflow, no host wiring,
no LLM in the loop), REUSING the shipped quest engine rather than duplicating it.

## What shipped

- **`games/dnd/core/models.py`** — the bounded-menu schema (design §4.1): frozen
  `MenuOption` (stable `id`, neutral `text_key`, registry `effect_id` — **no amount
  field**), frozen `Scene` (`scene_id`, `context_key`, `options`, `default_option_id`)
  whose `__post_init__` asserts menu size ≤ `MAX_MENU_SIZE (4)`, unique ids, the
  default is on the menu, and every `effect_id` is registered; frozen `DMChoice`
  (`option_id` + display-only `flavor`) — the DM's entire return payload. `FLAVOR_CAP
  = 240`.
- **`games/dnd/core/effects.py`** — the pre-priced effect **registry** `EFFECTS`:
  `rest_noop` (narrate-only NO-OP, the clamp target), `scout_narrate` (flavour beat),
  `escort_step` (reuses the engine: `offer → accept → apply_event → grant_rewards`,
  minting exactly `TIER_CAPS[I]`, `≤ GLOBAL_MAX`). No effect reads DM input to size an
  outcome.
- **`games/dnd/core/resolver.py`** — `resolve(scene, dm_choice, *, xp, seed, player_id)`
  = the validate → clamp → apply core (design §4.4): (1) cap the surfaced menu by
  `leverage.menu_width(xp)`; (2) validate `option_id ∈` the width-capped allowed set
  BEFORE resolving; (3) clamp ANY invalid input to `scene.default_option_id` (a
  deterministic no-op); (4) length-cap `flavor` to `FLAVOR_CAP`, display-only, never
  parsed; (5) apply the pre-defined effect, seeded via the shipped `derive_seed`
  (process-stable). Returns a `Resolution` (chosen id, effect id, code-owned
  reward/event, flavour, `clamped` flag).
- **`games/dnd/data/scenes.py`** — THE THEME DATA (Q-0267): the `waystation_road`
  scene + a `SCENE_TEXT` dict mapping every neutral `context_key`/`text_key` to
  player-visible copy. Deterministic logic references ids only; re-skin = data edit.
- **`tests/dnd/test_resolver.py`** (+15) — determinism + a pinned escort outcome +
  process-independence subprocess check; **the DM-clamp test** (hallucinated id,
  `None`/`{}`/dict/bare-string/empty/whitespace, off-menu-by-width → the `rest_noop`
  no-op, state unchanged); menu-cap rejection (>4 options / bad default / unregistered
  effect raise); flavour safety (a ~19k-char injection is capped to 240 and never
  changes the effect).
- **Suite registration (#34 guard):** `tests/dnd` added to `tests/EXPECTED_SUITES.txt`
  + a new `tests/dnd/EXPECTED_MIN_TESTS.txt = 15`.
- **Verification:** `pytest tests/dnd/` → 15 passed; `check_suite_floors.py` → exit 0
  (tests/dnd 15/15, TOTAL 280); `pytest tests/ games/exploration/tests/` → 280 passed;
  `bootstrap.py check --strict` → exit 0.

## 💡 Session idea

The resolver is a *pure* function of `(scene, dm_choice, xp, seed)`, so the safety
property that matters most — "a hallucinating model can never move state off the
menu" — is provable by *feeding the resolver garbage* rather than by prose. The
DM-clamp test parametrizes the full adversarial surface (a hallucinated id, a timeout
`None`, a wrong-type dict that even has the right *shape*, a bare string, empty and
whitespace ids) through one `_noop_resolution` assertion: every one lands on
`rest_noop` with `reward is None` and `event is None`. That turns the bounded-menu law
from a design claim into an executable invariant — the same "make the worst case a
capped/no-op outcome" discipline the quest catalog pins one level down.

## ⟲ Previous-session review

**I reviewed the previous session** before starting: PR #38 shipped
`docs/design/dnd-story-design.md` as a *design-only* doc that explicitly named the
files the first code PR would add (§6) and pinned the bounded-menu contract down to
dataclass shapes and the clamp rule (§4). This session implements that contract
verbatim — `Scene`/`MenuOption`/`DMChoice`, `MAX_MENU_SIZE=4`, `FLAVOR_CAP=240`,
`default_option_id` as the clamp target, the effect registry, `resolver.resolve` with
its validate→clamp→apply order — and honours the design's hard rule "reuse the engine,
never duplicate it": `DetRng`/`derive_seed`, `engine.grant_rewards` (`≤ GLOBAL_MAX`),
and `leverage.menu_width` are imported, not re-rolled. It also carries forward the
fishing skeleton's proven shape (PR #25): a pure resolver with a process-independence
subprocess check and a self-maintaining per-suite count floor, so the new `tests/dnd`
suite is registered against silent removal from day one.
