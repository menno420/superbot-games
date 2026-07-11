# 2026-07-11 — Q-0267 theme-slot audit (parallel delta supplement)

> **Status:** `complete`

📊 Model: Opus 4.8 · 2026-07-11T00:26:26Z · Q-0267 theme-slot audit (docs only)

## Scope
Audit ONLY — do **not** build a theme system. A parallel witness to the merged Q-0267
theme-slot audit (#28): re-read shipped `games/mining/**` and `games/exploration/**` for
player-visible nouns (item / location / structure / title NAMES, FLAVOR / narration, and
EMOJI), classify each as **data-isolated** (a swappable catalog / dict / dataclass table) vs
**hard-coded** (a literal baked into resolver logic). Fishing is explicitly OUT of scope — its
walking skeleton is built in parallel on `feat/fishing-skeleton`, already designing to Q-0267.
Docs-only slice: `docs/design/theme-readiness.md` + this card — **no `games/**` files touched**
(reading them is required; editing forbidden). The merged audit (#28) is authoritative and
broader; this PR ships only the *delta* it did not enumerate.

## 💡 Session idea
The ✓ clusters are already an in-code theme slot in everything but name: every one is a dict
keyed by a stable ID (`Biome.MAGMA`, an `EffectiveStats` field, a `CellFeature`) whose value
is the player-visible noun. A near-free next step for the idle lane: emit the manifest/
theme-slot format by **reflecting those existing dicts** — the slot IDs already exist as enum
members and dict keys, so a "classic" theme is the current values dumped, and validation is
"every ID a resolver references has a slot". The residue is only the handful of nouns *not yet
keyed to an ID*; closing that gap is what makes the reflection total.

## ⟲ Previous-session review
This is a previous-session review of `2026-07-10-order-001-collection-scope` (ORDER 001 /
PR #24, merged). That session was honest and well-scoped: it fixed the real CI hole (the gate
ran `pytest tests/` and silently saw 73 of 121 suites), added a **collected-count floor** so a
dropped suite fails loudly instead of shrinking coverage, banner-marked the gen-1 lane files as
HISTORY, corrected recorded kit-version drift, and converted `control/status.md` into the real
unified single-seat status. Its own close-out named the next debt — make the `tests` job a
*required* status check so the floor is a merge gate, not advice — and that debt is still open
(out of scope for a docs-only audit; flagged, not paid here). The discipline inherited: born-red
card first, docs-only diff, and a headline metric stated honestly.

## What shipped
1. **`docs/design/theme-readiness.md` — delta supplement to the merged Q-0267 audit (#28).**
   Rather than restate #28 (which is authoritative and broader — it covers fishing and the two
   highest-severity leaks), this doc records only the **three shipped `games/mining/**` surfaces
   the merged audit did not enumerate**, so the Q-0267 inventory is complete:
   - ❌ `capacity.py:103-121` pack/vault capacity warnings — `⚠️` emoji + prose welded into
     `pack_warning`/`vault_warning` f-strings, no sibling data table.
   - ❌ `world.py:93-101` descent hints — literal hint strings inside the branch; only the biome
     `{label}` is read from data.
   - ✅ `world.py:30-43` `BIOME_LABELS` / `BIOME_EMOJI` — a whole clean-data surface family #28
     omits (the positive counterpart to the descent-hint leak in the same file).
   - ⚠️ `skills.py:34-39` `BRANCH_LABELS` — data dict on neutral ids, but each value welds the
     emoji into the label copy; fix by splitting into a `BRANCH_EMOJI` dict + emoji-free label.
2. **Roadmap fold-in.** The two ❌ leaks and the ⚠️ welded emoji join the merged audit's **R2**
   ("sweep stray literals into their sibling tables"); `BIOME_*` needs no work. Behaviour-
   preserving (§6 integrity floor). Nothing changes #28's headline: the world games are already
   overwhelmingly theme-ready.
3. **Gate wiring (docs-only).** The doc is `audit`-badged and reachable via the mining domain
   index (`docs/design/mining-index.md`) after #34 restructured `current-state.md` into
   per-domain index links. No `games/**` file edited.

## ⟲ Rebase note (this session)
Rebased onto current `origin/main` after #34 (current-state → per-domain index links) and #47
(status.md rewrite) merged. Dropped the branch's `control/status.md` and old flat
`current-state.md` "Audits:" edits (coordinator-owned / superseded); made the doc reachable via
`mining-index.md` instead. This card lives at the `-parallel.md` path so it no longer add/add-
collides with #28's card of the same base name. Applied the review's one-line stale-prose fix:
#28's encounters narration cluster is now **resolved by #31**, so the supplement no longer frames
it as open.
