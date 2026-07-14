# 2026-07-14 · night fix — de-duplicate the article in fishing spot banners

> **Status:** `in-progress`
>
> 📊 Model: Fable · 2026-07-14T01:49:08Z · night-fix-fishing-dock-grammar

UX bug-fix slice. `games/fishing/core/catch.py:216` renders the bite
banner as `f"At the {spot.name}"`, and the dock spot's DATA name is
"The Old Dock" (`games/fishing/core/spots.py:102`) — so the name's own
article doubles the template's. Reproduced this session at main
`bdc3445`: `printf 'cast\nquit\n' | python3 -m games.fishing` →
"🪝 At the The Old Dock — 🐠 … you land a Bass (29 cm)!". Grep confirms
one sibling with the same defect through the same data: the no-bite line
at catch.py:206 (`f"cast into the {spot.name.lower()}…"` → "cast into
the the old dock…"). No other "At the" render sites or snapshots pin the
spot name.

Plan (smallest blast radius, display handling only): one tiny
article-aware display helper in catch.py — strip a leading "The " when
the name carries its own article — applied to the two narration
templates; NO sell values, NO balance constants, NO spot ids or DATA
rows touched. Regression tests pin the corrected banner for the dock
spot AND a non-"The" spot (Tide Pool) plus the no-bite sibling; verify
by rerunning the repro. `tests/fishing` floor bumped and
`docs/balance.md` regenerated in the same push.

Self-release note: this slice's claim file
(`control/claims/night-fix-fishing-dock-grammar.md`) is deleted in this
card's flip commit, per the established precedent.
