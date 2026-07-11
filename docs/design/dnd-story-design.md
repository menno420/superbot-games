# D&D story game — design (AI Dungeon Master as a bounded-menu plugin package)

> **Status:** `reference` · lane: game-exploration · 2026-07-11
>
> The engineering design for the **AI Dungeon Master story game** as a pure-domain
> **plugin package** for superbot-next. It sits on top of the already-shipped
> deterministic quest/encounter engine (`games/exploration/quest/**`) and specifies
> the **bounded-menu contract** (Q-0040 / D-0007) concretely enough to build against:
> the menu schema, what the DM sees, what it returns, the validation/clamp point, and
> the determinism/sim-pin discipline. **This is a DESIGN doc — no code ships here; the
> first code PR is a one-scene walking skeleton (§6).** Companion to the plan/spec
> `docs/planning/dnd-story-game-plan.md` (posture, session lifecycle, persistence,
> budget) and the engine design `docs/design/quest-encounter-engine.md`. Where this
> doc and the shipped engine disagree, **the shipped engine wins** (its behaviour is
> the spec).

## 1. Purpose & scope

The exploration domain's one genuinely undesigned pillar is the **D&D story game**
itself — the AI Dungeon Master (buildability map §8: "the domain's largest invention
gap"). The deterministic substrate it needs is **already built and sim-pinned** — the
quest/encounter engine under `games/exploration/quest/**` (48 tests green incl. the
balance-pin sim). What is *not* built is the story game as a shippable unit.

This doc designs that unit as a **plugin package** in the exact shape mining and fishing
already ship (§2), reusing the engine rather than duplicating it (§3), and pins the
**bounded-menu law** — the contract that keeps the AI's authority to "pick one
pre-approved button" — down to dataclass shapes and a clamp rule (§4). It is a design
doc: it names the files the first code PR would add and where their tests live (§6), but
ships no code itself.

Scope boundaries:

- **In scope:** the pure-domain package shape; the reused engine seams; the bounded-menu
  contract (schema, DM I/O, validation, clamp, determinism); theme-readiness; the
  walking-skeleton cut; the post-skeleton P-queue; the integrity rails.
- **Out of scope (owned elsewhere):** the session lifecycle state machine, persistence
  schema, per-guild budget/degrade, the `dungeon_master` AI-orchestration profile, and
  the image seam — all specified in `docs/planning/dnd-story-game-plan.md` §3. This doc
  references them, it does not re-specify them.

## 2. Plugin-package shape (mirrors mining / fishing)

The story game is a **pure-domain plugin package** with the host seams left open — the
same three-layer decomposition mining ships (`docs/design/mining-plugin-layout.md` §2)
and fishing mirrors (`games/fishing/__init__.py` docstring). Proposed package path
**`games/story/`** (the "D&D story game"; `games/dnd/` is an equivalent name — `story`
is chosen to match the shipped D-1 "Story Actions" vocabulary and to read as a genre-
neutral container the theme catalog re-skins into D&D):

```
games/story/
  core/            # LAYER 1 — pure domain (stdlib only; no Discord/DB/IO; injectable RNG)
    scene.py           # the bounded-menu dataclasses: Scene, MenuOption, DMChoice, Effect
    resolver.py        # resolve(scene, dm_choice, ...) — the validate → clamp → apply core
    effects.py         # the pre-priced effect registry (id → deterministic transition)
    rng.py             # story_seed(seed, scene_id) — independent splitmix64 stream (story salt)
  data/            # THE THEME DATA (Q-0267) — every player-visible noun keyed on neutral ids
    scenes.py          # scene catalog: context copy, option copy, flavour, default-option ids
  sim/             # pure seeded sim harness — pins menu balance (per-option effect yields)
    menu_sim.py
  workflow/        # LAYER 2 — named-next. Audited op seam (read state → call core → 1 commit)
  # host-adapter   # LAYER 3 — named-next. superbot-next SubsystemManifest binding (swappable)
```

**Mapping onto the layers (identical role split to mining/fishing):**

| story layer | role | mining/fishing analogue |
|---|---|---|
| `games/story/core/` | pure domain — decides *what happens* (the menu resolution) | `games/mining/core/`, `games/fishing/core/` |
| `games/story/data/` | theme catalog — player-visible nouns/copy in DATA | `games/fishing/core/species.py`, `spots.py` |
| `games/story/sim/` | seeded balance harness — pins every per-option yield | `games/mining/sim/`, `games/fishing/sim/` |
| `games/story/workflow/` (next) | audited op: read host state → call core → one transaction | `services/*_workflow.py` (oracle) |
| host-adapter (next) | superbot-next manifest facets (commands/panels/stores) | `sb/manifest/<x>.py` |

**Host-facing seam (how superbot-next consumes it).** The pure core has **zero**
knowledge of the host contract; Layer 3 is the only place that imports `sb.spec.*`
(`docs/design/mining-plugin-layout.md` §3). The host binds the story game as a
`SubsystemManifest` (`sb/spec/manifest.py`, `@dataclass(frozen=True)` with facet slots
`key/version/commands/panels/settings/stores/events/capabilities/...`); a
`sb/manifest/story.py` declares `MANIFEST = SubsystemManifest(...)` and routes each
Story-Action panel click into a Layer-2 workflow op, which calls the Layer-1 resolver.
The AI's `dungeon_master` profile (plan §3.6) is a host concern whose **only tool** is
`select_story_action(menu, choice_id)` — it never imports or bypasses the pure core.
Because the core is contract-independent, it is safe to ship ahead of any host churn.

## 3. Engine reuse — extend, never duplicate

The story game is a **thin domain on top of the shipped quest engine**. It adds a
*scene/menu* layer; it reuses the engine for determinism, state transitions, gating, and
rewards. Exact seams:

| Reused seam (file:line) | What it provides | How the story game uses it |
|---|---|---|
| `games/exploration/quest/rng.py:52` `DetRng` + `:36` `derive_seed` | splitmix64 PRNG + process-stable FNV-1a seed derivation (no wall-clock, no global RNG) | seeded, reproducible scene resolution; `story_seed` folds a story-domain salt over `derive_seed`, mirroring fishing's `fishing_seed` (`games/fishing/core/rng.py`) |
| `games/exploration/quest/models.py:90` `QuestInstance` (+ `:23` `QuestState`, `:66` `ObjectiveProgress`) | immutable, seed-derived quest state; transitions return NEW instances | a scene's quest-advancing option holds a `QuestInstance`; the resolver never mutates it |
| `games/exploration/quest/engine.py:28` `offer` / `:58` `accept` / `:69` `apply_event` / `:141` `grant_rewards` | the pure transition core — offer/accept a quest, advance objectives by matching a `GameEvent`, mint the tier-capped reward | an option's effect emits a `GameEvent` into `apply_event`; a `COMPLETED` quest mints via `grant_rewards` (amounts are code-owned) |
| `games/exploration/quest/predicates.py:25` `GameEvent` + `:85` `evaluate` | normalized event + pure predicate matcher `(GameEvent, params) -> int` | an option effect is expressed as "emit this `GameEvent`"; the engine (not the DM) decides the increment — the story game authors no new predicate logic for the skeleton |
| `games/exploration/quest/catalog.py:22` `TIER_CAPS` / `:29` `GLOBAL_MAX` / `:32` `TEMPLATES` / `:131` `menu()` | the hard-capped, code-owned reward catalog + the "menu the DM picks from" | the reward ceiling is inherited verbatim; the story menu is the same "pick from a pre-approved surface" pattern, one level up |
| `games/exploration/quest/leverage.py:16` `menu_width` (`BASE=2`, `MAX=4`, `+1/500 XP`) | message-XP → how MANY options may be surfaced (code-computed, monotonic, hard-capped) | the resolver caps the rendered menu to `menu_width(message_xp)` — chat activity widens *count*, never amounts or outcomes |

**Reused vs new (minimal new surface):**

- **REUSED (built, sim-pinned):** `DetRng`/`derive_seed`, `QuestInstance` + the four
  engine transitions, `GameEvent`/`evaluate`, `TIER_CAPS`/`GLOBAL_MAX`, `menu_width`.
- **NEW (the story domain adds):** the `Scene`/`MenuOption`/`DMChoice`/`Effect`
  dataclasses (§4); the `resolver.resolve` validate→clamp→apply core (§4); the
  effect registry (`effects.py`) whose entries are pre-priced references *into* the
  engine; the scene theme catalog (`data/scenes.py`, §5); the menu-balance sim.

The story game **does not** re-implement RNG, reward caps, quest state, or menu-width
math — those exist. Its new code is the scene/menu shell and the clamp.

## 4. THE BOUNDED-MENU LAW — the contract (Q-0040 / D-0007)

This is the heart of the design and the binding posture (`docs/founding-plan-exploration.md`
§57 "AI picks from bounded menus"; adopted as D-0007 in
`docs/retro/self-review-exploration-2026-07-09.md`; spine of
`docs/planning/dnd-story-game-plan.md` §1). Stated as one law:

> **The AI Dungeon Master picks ONLY from a pre-approved, hard-capped menu enforced by
> code. It never computes amounts and never mutates state. Deterministic code owns every
> outcome the DM narrates.**

The subsections below make that concrete.

### 4.1 Menu schema (the dataclass shape)

A **Scene** presents a hard-capped list of **MenuOptions**. Each option carries a stable
id, player-visible text drawn from the **theme catalog** (not code), and a reference to a
**pre-defined deterministic effect by id** — never a runtime-computed amount:

```python
# games/story/core/scene.py  (design shape)

MAX_MENU_SIZE = 4          # hard cap on options in ANY scene (matches leverage.MAX_MENU_WIDTH)
FLAVOR_CAP    = 240        # DM flavour text is length-capped and DISPLAY-ONLY

@dataclass(frozen=True)
class MenuOption:
    id: str                # stable option id, e.g. "advance_escort"  (mechanics key on THIS)
    text_key: str          # neutral id into data/scenes.py copy — NOT the copy itself (Q-0267)
    effect_id: str         # id into effects.EFFECTS — a PRE-DEFINED, PRE-PRICED transition

@dataclass(frozen=True)
class Scene:
    scene_id: str
    context_key: str                     # neutral id -> scene prose in the theme catalog
    options: tuple[MenuOption, ...]       # 1..MAX_MENU_SIZE, hard-capped (post_init asserts)
    default_option_id: str               # the safe no-op fallback — the clamp target (§4.4)

    def __post_init__(self) -> None:
        assert 1 <= len(self.options) <= MAX_MENU_SIZE
        ids = {o.id for o in self.options}
        assert self.default_option_id in ids           # the clamp target is always ON the menu
        assert all(o.effect_id in EFFECTS for o in self.options)  # every effect is pre-defined
```

No `MenuOption` field can hold an amount, a reward, or free text — the *only* number-
bearing thing (`effect_id`) is an **id into a code-owned registry**, resolved at build
time, sim-pinned. This is the same shape the quest catalog already uses (the DM picks a
`(template_id, RewardTier)` *key*, never a bundle — `catalog.py:131` `menu()`).

### 4.2 What the DM (AI) SEES

Only the scene context prose (resolved from the theme catalog) and the **enumerated
allowed options** — each option's `id` and its player-visible `text`. Nothing mechanical:

```jsonc
// the ENTIRE payload handed to the model
{
  "scene": "You reach the fork on the waystation road. Dusk is coming.",
  "options": [
    { "id": "advance_escort", "text": "Press on toward the waystation" },
    { "id": "scout_ahead",    "text": "Scout the treeline first" },
    { "id": "make_camp",      "text": "Make camp and wait for dawn" }
  ]
}
```

The model sees no seeds, no amounts, no effect ids, no quest state, no other scenes.

### 4.3 What the DM RETURNS

Exactly **one option id chosen from the menu**, plus *optional* display-only flavour:

```jsonc
{ "option_id": "advance_escort", "flavor": "The party steels itself and marches on." }
```

That is the model's entire authority. It cannot emit amounts, state, new options, or a
menu — the `dungeon_master` profile's only tool is `select_story_action(menu, choice_id)`
(plan §3.6). Anything else in its output is ignored.

### 4.4 Validation & clamp-to-no-op (the enforcement point)

Deterministic host code validates the returned id **before any resolution**, and clamps
any invalid output to a designated safe default. This is the single choke point:

```python
# games/story/core/resolver.py  (design shape)

def resolve(scene, dm_choice, *, world_seed, player_id, message_xp, rng=None):
    # 1. CAP the surfaced menu by code-computed width (chat activity widens COUNT only).
    width   = leverage.menu_width(message_xp)          # exploration/quest/leverage.py:16 — 2..4
    allowed = scene.options[:min(len(scene.options), width, MAX_MENU_SIZE)]
    allowed_ids = {o.id for o in allowed}

    # 2. VALIDATE the DM's returned id ∈ the allowed set BEFORE resolving anything.
    if not isinstance(dm_choice, DMChoice) or dm_choice.option_id not in allowed_ids:
        chosen = _option(scene, scene.default_option_id)   # 3a. CLAMP → deterministic no-op
    else:
        chosen = _option(scene, dm_choice.option_id)       # 3b. a legal, pre-approved option

    # 4. Flavour is length-capped and treated as DISPLAY-ONLY — never parsed for effects.
    flavor = _sanitize(getattr(dm_choice, "flavor", ""))[:FLAVOR_CAP]

    # 5. Resolve the PRE-DEFINED, PRE-PRICED effect deterministically (code owns the outcome).
    effect = EFFECTS[chosen.effect_id]
    seed   = story_seed(world_seed, scene.scene_id)        # process-stable (rng.py:36 derive_seed)
    return effect.apply(seed=seed, player_id=player_id, rng=rng, flavor=flavor)
```

The clamp fires on **every** off-menu condition — id not in the (width-capped) menu, a
malformed / non-`DMChoice` payload, a hallucinated id, a timeout (host passes a null
choice), or injected text. In all of them the resolver falls back to
`scene.default_option_id`, which by construction (§4.1 `__post_init__`) is always a real
menu option and is designed to be a **narrate-only no-op** (advances no quest, mints no
reward). The DM can therefore **never move state off the menu**. Flavour is capped at
`FLAVOR_CAP` and never inspected for mechanics — it is rendered, not parsed.

### 4.5 Determinism & sim-pinning

Deterministic code owns every outcome (`games/exploration/quest/rng.py:1` — "Determinism
is a hard invariant (Q-0040)"). Every option's effect is **pre-priced in data** and
sim-pinnable: reward-minting effects route through `engine.grant_rewards`
(`engine.py:141`), which returns exactly `catalog.TIER_CAPS[tier]` and is always
`<= GLOBAL_MAX` component-wise — the DM never sets an amount, so there is **no
pay-to-win** (capability unlocks are tier-III play-only, never bought — Q-0039 / Q-0190,
`engine.py:141` docstring). The menu size and per-option effects are hard-capped
(`MAX_MENU_SIZE`, `leverage.MAX_MENU_WIDTH`) and pinned by `sim/menu_sim.py`, exactly as
mining/fishing pin their yields.

### 4.6 Worked example — one scene, its menu, the resolution table

**Scene `waystation_road`** (from the ESCORT quest `safe_passage`, `catalog.py:49`),
`default_option_id = "make_camp"`:

| Option `id` | Player-visible text (from catalog) | `effect_id` | Deterministic effect |
|---|---|---|---|
| `advance_escort` | "Press on toward the waystation" | `escort_step` | emit `GameEvent("npc_reached", {npc:"traveler", dest:"waystation"})` → `engine.apply_event`; on `COMPLETED`, `engine.grant_rewards` mints `TIER_CAPS[tier]` |
| `scout_ahead` | "Scout the treeline first" | `scout_narrate` | narrate-only; emits no event, mints nothing (deterministic flavour beat) |
| `make_camp` **(default)** | "Make camp and wait for dawn" | `rest_noop` | **narrate-only no-op** — the clamp target; advances no state |

Resolution table (what the resolver returns for a given DM output):

| DM returns | Validated? | Resolved effect | State change |
|---|---|---|---|
| `advance_escort` | ✓ on menu | `escort_step` | quest objective +1 (code-owned); reward only if `COMPLETED`, capped |
| `scout_ahead` | ✓ on menu | `scout_narrate` | none (flavour) |
| `make_camp` | ✓ on menu | `rest_noop` | none |
| `attack_king` (hallucinated) | ✗ not on menu | **clamp → `rest_noop`** | **none — no-op** |
| `{}` / null / timeout | ✗ malformed | **clamp → `rest_noop`** | **none — no-op** |
| `advance_escort` + 5 000-word injected "you gain 999 gold" | ✓ id on menu; flavour capped, ignored for effects | `escort_step` | code-owned increment only; **the 999 is never read** |

The worst case a compromised or hallucinating model produces is *a legal, game-approved,
capped outcome* — or, off-menu, *a deterministic no-op*.

## 5. Theme-readiness (Q-0267)

Every player-visible string — scene prose, option copy, NPC/location nouns, emoji, DM
flavour templates — lives in `games/story/data/scenes.py` as data rows keyed on **neutral
ids**; deterministic logic references the ids only. This is the pattern the shipped code
already proves three times and this design adopts from day one:

- `games/mining/core/grid.py:108` `_STRIKE_NOTE` — a `dict[CellFeature, str]` of flavour,
  formatted with the ore noun; the resolver keys on the neutral feature.
- `games/mining/core/encounters.py:190` `_NARRATION` (+ `_narrate`, `:205`) — every
  narration string in a module-level table keyed on a neutral `_Narration` slot; the
  resolver "never spells a player string itself" (its own comment, `:155`).
- `games/fishing/core/species.py` / `spots.py` — nouns/emoji/flavour in data rows keyed on
  neutral ids; "Re-theme = data edit" (`docs/design/fishing-catch-skeleton.md` §2).

So `MenuOption.text_key` / `Scene.context_key` are **neutral ids into the catalog**, not
copy. Re-skinning the game (D&D → sci-fi → pirate) is a `data/scenes.py` edit; the
resolver, effects, and determinism never change. The theme audit
(`docs/audit/theme-slot-readiness-2026-07-11.md`) is the standard this must pass on day
one rather than remediate later.

## 6. Walking-skeleton cut (the first code PR)

The smallest shippable end-to-end slice — **one scene, one menu, one deterministic
resolution, plus the two load-bearing tests** (a pinned deterministic outcome and a
DM-clamp test). Pure domain only; workflow and host wiring are deferred (as fishing did).

**Files the first code PR adds:**

- `games/story/__init__.py` — the three-layer docstring (mirrors `games/fishing/__init__.py`).
- `games/story/core/scene.py` — `MenuOption`, `Scene`, `DMChoice`, `Effect` (§4.1).
- `games/story/core/effects.py` — `EFFECTS` registry with the three skeleton effects
  (`escort_step`, `scout_narrate`, `rest_noop`); reward effects route through
  `engine.grant_rewards`.
- `games/story/core/resolver.py` — `resolve(...)` = the validate → clamp → apply core (§4.4).
- `games/story/core/rng.py` — `story_seed(seed, scene_id)` folding a story salt over
  `derive_seed` (mirrors `games/fishing/core/rng.py`).
- `games/story/data/scenes.py` — the `waystation_road` scene's context/option copy/flavour
  (THE THEME DATA, §5).
- `games/story/sim/menu_sim.py` — a seeded sweep pinning each option's effect yield.
- `tests/story/__init__.py`
- `tests/story/test_resolver.py` — **the deterministic-outcome pin:** a fixed
  `(world_seed, scene, chosen id)` resolves to a byte-identical outcome, including a
  subprocess process-independence check (mirrors mining/fishing).
- `tests/story/test_dm_clamp.py` — **the clamp pin:** feed a hallucinated id, a malformed
  payload, a null/timeout, and an injected-flavour choice; assert each clamps to the
  `rest_noop` no-op (no event emitted, no reward minted) and that flavour is never parsed.
- `tests/story/test_theme_data.py` — every player-visible string comes from `data/scenes.py`
  (no copy inlined in `resolver.py`/`effects.py`).
- `tests/story/test_no_pay_to_win.py` — `resolve` exposes no spend/purchase lever; reward
  effects never exceed `GLOBAL_MAX`.

**Where the tests live & CI:** `tests/story/`, collected by the same `tests.yml` job that
already collects `tests/` and `games/exploration/tests/`. The PR bumps the **ORDER-001
count floor** in `.github/workflows/tests.yml` (currently `248`, the transitive
churn/reachability mechanism from PR #34) by the net-new story test count, so a dropped
suite trips the floor instead of silently shrinking coverage — the exact discipline the
fishing spot-biome slice used (`.sessions/2026-07-11-fishing-spot-biomes.md`). *(The task
brief names an `EXPECTED_MIN_TESTS.txt` variant of this mechanism; this repo implements
the same guard inline in `tests.yml` as the `COLLECTED -lt <floor>` check — the walking-
skeleton PR uses whichever form is current at that commit.)*

## 7. P-queue after the skeleton (ordered follow-ups, each a small slice)

1. **More scenes** — add rows to `data/scenes.py` (TRAVEL / SOCIAL / REST connective menus,
   plan §3.2) with per-scene sim-pins. No resolver change.
2. **Quest-chaining via the exploration engine** — wire `escort_step`-style effects across
   the five catalog quest kinds (`catalog.py:32`), so a scene sequence drives a
   `QuestInstance` through `offer → accept → apply_event → grant_rewards`.
3. **Save/resume** — the versioned-JSONB bounded summary (plan §3.3); a workflow concern,
   the resolver stays per-scene.
4. **DM prompt hardening** — the `dungeon_master` profile/toolset (plan §3.6): the single
   `select_story_action` tool, per-session `AIToolBudget`, degrade-CLOSED.
5. **Theme catalogs** — a second, non-D&D re-skin proving the Q-0267 seam (data-only).
6. **Sim harness for menu balance** — extend `menu_sim.py` to sweep option distributions
   across scenes and gear tiers, pinning bands (as fishing's `catch_sim.py` does).

## 8. Integrity checklist (rails this design must never violate)

- **Deterministic core owns every outcome** — no LLM in the resolution loop; the DM only
  picks an id. (`games/exploration/quest/rng.py:1`; §4.4/§4.5.)
- **Bounded-menu DM** — the AI's entire authority is one id from a hard-capped,
  pre-approved menu; off-menu output clamps to a deterministic no-op. (Q-0040 / D-0007;
  §4.)
- **Amounts are code-owned & capped** — every reward flows through `engine.grant_rewards`
  ≤ `GLOBAL_MAX`; the DM never emits a number. (`engine.py:141`, `catalog.py:22`/`:29`.)
- **Sim-pinned balance** — every per-option effect yield is pinned by `sim/menu_sim.py`;
  no invented number ships unpinned. (§4.5; mining/fishing precedent.)
- **No pay-to-win** — no spend lever in `resolve`; capability unlocks are tier-III
  play-only. (Q-0039 / Q-0190; §4.5.)
- **Theme-readiness from day one** — all player-visible strings in `data/`, keyed on
  neutral ids. (Q-0267; §5.)
- **Menu width is code-computed & capped** — chat activity widens option *count* only
  (`leverage.menu_width`, 2..4), never amounts or outcomes. (`leverage.py:16`; §3, §4.4.)
</content>
</invoke>
