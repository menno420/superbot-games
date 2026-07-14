# 2026-07-14 · night test — display-table completeness registry: vocab and display tables stay in sync

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T02:47:06Z · night-display-table-registry

Test slice implementing the display-table completeness registry card
idea from `.sessions/2026-07-14-night-coverage-mining-core-naming.md`,
verified unimplemented at main `f3fd346`: no `test_display_tables.py`
existed anywhere; the ItemKind↔`_KIND_EMOJI` relation was covered only
incidentally, and a new enum member / stat field / biome could ship
without its player-facing label and fail only at render time (a
`KeyError` in an embed) or silently (a `.get` fallback).

Shipped `tests/mining/test_display_tables.py` (9 tests, registered
`tests/mining/` suite — a `tests/shared/`-root file would have forced a
new overlapping suite under the floor guard's discovery rules). Pins
the idea's named triples plus every sibling vocabulary↔display pair
found by reading the mining core modules: ItemKind values ↔
`_KIND_EMOJI` keys BOTH ways (missing emoji and stale key each named);
`EffectiveStats` field names = `STAT_LABELS` keys pinned to DECLARATION
ORDER (describe_stats renders in dict order) and = `STAT_GLYPHS` keys
as a set; `_CATEGORY_LABEL` **values** = `CATEGORY_ORDER` =
`CATEGORY_EMOJI` keys + no-duplicate order tuple — one honest spec
correction: the slice spec phrased this as `_CATEGORY_LABEL` *keys*,
but those are the internal slugs (`weapons`, `armour`, …); the
originating card idea and the shipped code both key
`CATEGORY_ORDER`/`CATEGORY_EMOJI` by the label VALUES, which is what is
pinned; `TYPE_EMOJI` keys ⊆ catalog base types (a renamed item can't
leave a stale emoji key); `Biome` ↔ `BIOME_LABELS`/`BIOME_EMOJI` both
ways (world); `CellFeature` ↔ `_FEATURE_GLYPH`/`_FEATURE_LABEL` both
ways plus `MAP_LEGEND` naming every glyph incl. `PLAYER_GLYPH` /
`FOG_GLYPH` (grid); `_SECTION_ORDER` ↔ `SHOP_SECTION_LABEL` (market);
`BRANCHES` ↔ `BRANCH_LABELS` (skills). Equivalents in other games were
looked for and honestly found absent: a repo-wide grep for
`EMOJI|_LABEL|GLYPH` dicts under `games/` hits only mining core (the
sims' report strings are not vocabulary tables), so the registry is
mining-scoped. All nine pairs are IN SYNC at HEAD — no desync found, so
no shipped bug; the value is the tripwire.

`tests/mining` floor 177 → **186** (floor==collected convention);
`docs/balance.md` regenerated BEFORE flip (gen-balance gate),
`gen_balance.py --check` green. Full suite 727 → **736 passed** locally
on this branch; strict check exit 0. Claim
`control/claims/night-display-table-registry.md` self-released in this
flip commit (established precedent).

## 💡 Session idea

The registry pins that every vocabulary member HAS a glyph/label — but
not that the glyphs are USABLE: two `_FEATURE_GLYPH` values colliding
(or one equal to `PLAYER_GLYPH`/`FOG_GLYPH`) would render an ambiguous
map that every sync check still passes, and duplicate `CATEGORY_EMOJI`
/ `STAT_GLYPHS` values would make two categories or stats read
identically in embeds. Add a **glyph collision audit**: one test per
display table asserting values are non-empty and pairwise distinct
where ambiguity is player-facing (map glyph namespace = `_FEATURE_GLYPH`
values ∪ `{PLAYER_GLYPH, FOG_GLYPH}`; category emoji; stat glyphs;
biome emoji), with a documented allowlist for deliberate reuse across
DIFFERENT tables (🛡️ is both a shield type and the Armour category —
fine, different surfaces). Dedupe check against the used-idea list: the
display-table completeness registry (this slice) checks key coverage,
not value distinctness; the composed-narration grammar lint targets
sentence assembly, not glyph namespaces; no card idea to date audits
display-value collisions.

## ⟲ Previous-session review

The previous slice is this run's #122
(`claude/night-detector-trip-registry`, born-red `1639c75`, tests
`09bbc3c`, flip `63e83ca`, squash-merged to main as `f3fd346`).
Verified against live CI: at flip SHA `63e83ca` all three workflows
completed green (tests run 29301835284, substrate-gate 29301835305,
auto-merge-enabler 29301835319), and born-red `1639c75`'s
substrate-gate failure (run 29301684184) was exactly the designed
pre-flip HOLD while tests (29301684190) and the enabler (29301684182)
stayed green. Verified against this branch's base (includes `f3fd346`):
`tests/shared/sim/test_detector_trips.py` exists, its enumeration is
genuinely derived (annotation scan over the five sim modules, filtered
by `__module__`), the four predicates it claims are exactly what the
scan yields, `tests/shared/sim/EXPECTED_MIN_TESTS.txt` reads 40, and
the balance page's floors table carries `| \`tests/shared/sim\` | 40 |`.
Its headline holds up: menu_sim's `_reward_leq_global_max` fail branch
had no prior trip test (`git grep` at `fefe16c` finds no reference to
it outside menu_sim itself). One honest nit: #122's card says
enumeration accepts "class `bool`" annotations so it "survives a module
dropping the future import" — true, but untested in that slice (all
five modules carry the future import, so the class-object branch of the
check is itself dead code by its own registry's standard).
