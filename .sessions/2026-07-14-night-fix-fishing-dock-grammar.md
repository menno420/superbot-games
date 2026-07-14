# 2026-07-14 · night fix — de-duplicate the article in fishing spot banners

> **Status:** ✅ `complete`
>
> 📊 Model: Fable · 2026-07-14T01:51:48Z · night-fix-fishing-dock-grammar

UX bug-fix slice. `games/fishing/core/catch.py:216` rendered the bite
banner as `f"At the {spot.name}"`, and the dock spot's DATA name is
"The Old Dock" (`games/fishing/core/spots.py:102`) — the name's own
article doubled the template's. Reproduced this session at main
`bdc3445`: `printf 'cast\nquit\n' | python3 -m games.fishing` →
"🪝 At the The Old Dock — 🐠 … you land a Bass (29 cm)!". Grep found
exactly one sibling with the same defect through the same data — the
no-bite line at catch.py:206 ("You cast into the the old dock…") — and
no snapshot/test pinning the old text.

Shipped the smallest-blast-radius fix, display handling only: one
article-aware helper (`_article_free_name` — strip a leading "The "
when the name carries its own article) applied at the two narration
render sites. The banner now reads "🪝 At the Old Dock — …" and the
no-bite line "🎣 You cast into the old dock…"; non-"The" spots (Tide
Pool, Deep Water, Open Water) render byte-identically to before. NO
sell values, NO balance constants, NO spot ids or DATA rows touched;
mechanics never read the name. Three regression tests in
`tests/fishing/test_spots.py` pin the corrected dock banner, the
non-"The" Tide Pool banner through the same template, and the no-bite
sibling line. Verified by rerunning the repro: "🪝 At the Old Dock — …".
`tests/fishing` floor 104 → 119 (catching it up to collection);
`docs/balance.md` regenerated (gen-balance gate). Full suite 671 →
**674 passed** locally on this branch; `gen_balance.py --check` green.
Claim `control/claims/night-fix-fishing-dock-grammar.md` self-released
in this flip commit (established precedent).

## 💡 Session idea

This bug is a DATA row (a name carrying its own article) colliding with
a TEMPLATE (supplying the article) — invisible to unit tests until a
human reads the composed sentence. Adopt a **composed-narration grammar
lint**: a meta-test that renders every narration template against every
catalog DATA row it can compose with (all spots × bite/no-bite here;
dnd flavour lines; mining encounter narration) and greps the composed
output for a tiny denylist of mechanical grammar defects — doubled
words ("the the", "At the The"), doubled spaces, doubled punctuation —
so any future data row or template edit that composes into broken
English fails loudly at the seam where data meets template. Dedupe
check against the used-idea list: the display-table completeness
registry checks tables COVER their domain, and the verb-table single
source checks command surfaces agree; neither (nor any other used idea)
inspects the grammar of composed template × data output. No card idea
to date does.

## ⟲ Previous-session review

The previous slice is this run's own #115
(`claude/night-fix-dnd-resolver-unhashable`, born-red `134fe1d`, fix
`e29ebb6`, flip `9011634`), reviewed honestly against its branch: the
claimed repro and fix both verify — pre-fix
`resolve(scene, DMChoice(option_id=['a','list']), xp=0, seed=1)` raised
`TypeError: unhashable type: 'list'` at main `bdc3445`, post-fix it
returns the clamped default (`make_camp`, `clamped=True`); suite 671 →
677 on that branch with the six-payload sweep; strict exit 0 after its
flip. One honest caveat: at flip time #115's CI had not yet reported
(check runs pending at first poll) — its green is asserted from the
local suite + strict run, with CI conclusions recorded in the session
report, not in that card. The wave before (#113 `73111d0` / #114
`bdc3445`) was reviewed in #115's card; nothing found there has changed
since.
