# Theme-readiness audit — delta supplement (Q-0267)

> **Status:** `audit` · seat: world-games · 2026-07-11

Supplements [`../audit/theme-slot-readiness-2026-07-11.md`](../audit/theme-slot-readiness-2026-07-11.md)
(the merged Q-0267 theme-slot audit, #28) with **additional player-visible surfaces found in a
parallel audit** (#27). The merged audit is authoritative and broader — it covers fishing, and
it correctly flags the two highest-severity leaks (the `encounters.py:160-342` narration cluster
— since **resolved by #31** and marked ✅ RESOLVED (R1) in the merged audit — and the still-open
item-identity noun-as-key model). This doc does **not** restate any of that. It records
only the three shipped `games/mining/**` surfaces the merged audit did not enumerate, so the
Q-0267 inventory is complete. Same classification key: ✅ DATA (module-level table on a neutral
id) · ⚠️ MIXED / welded · ❌ CODE (noun hardcoded in a mechanic). Audit only — no code changed.

## Surfaces not covered by #28

| Surface | Where (`file:line`) | Verdict | Note |
|---|---|---|---|
| Pack / vault capacity warnings | `capacity.py:103-111` (`pack_warning`), `capacity.py:113-121` (`vault_warning`) | ❌ | Two player-facing nudges — `"⚠️ Your pack is full …"` / `"⚠️ Your vault is over capacity …"` — are hardcoded f-strings returned inline from the two functions, with no sibling data table. Emoji `⚠️` + prose both baked into the mechanic. |
| Descent hints | `world.py:93-101` (`descend_hint`) | ❌ | `"You have the gear to reach the deepest bands."` and the `"Equip a brighter light to descend to {label} …"` f-string are string literals inside the branch; only the biome `{label}` is read from data. |
| Biome labels + emoji | `world.py:30-36` (`BIOME_LABELS`), `world.py:37-43` (`BIOME_EMOJI`) | ✅ | A whole clean-data surface family the merged audit omits: display labels ("Surface", "the Deep", "the Magma core") and emoji (🌳 🪨 💎 🌋) in two module-level dicts keyed on the neutral `Biome` enum. Swappable by editing data alone — the positive counterpart to the descent-hint leak in the same file. |
| Skill-branch labels | `skills.py:34-39` (`BRANCH_LABELS`) | ⚠️ | Data dict keyed on neutral branch ids (`MINING`/`COMBAT`/…), but each value **welds the emoji into the label copy** (`"⛏️ Mining — raw digging power"`) — the emoji cannot be re-skinned without editing the label string. Same welded-emoji anti-pattern the merged audit notes for the energy bar; fix by splitting into a `BRANCH_EMOJI` dict + an emoji-free label, mirroring how `titles.Title` already keeps `emoji` and `label` as separate fields. |

## How these fold into #28's roadmap

- The two ❌ leaks (`capacity.py`, `world.py` descent hints) join the merged audit's **R2 —
  "sweep stray literals into their sibling tables"**: move each into a small module-level
  narration/warning table (`_WARNINGS`, `_DESCENT_HINTS`) keyed on a neutral id, `.format()`-ing
  the amount/label off the row. Behaviour-preserving (§6 integrity floor); pins with a byte-identity test.
- The `skills.py` welded emoji joins **R2** as well: split `BRANCH_LABELS` into `BRANCH_EMOJI`
  + label so the emoji is an independently swappable slot.
- `BIOME_LABELS` / `BIOME_EMOJI` need **no work** — they are already the target shape; listed
  here only so the audit's ✅ column is complete.

Nothing here changes the merged audit's headline conclusion: the world games are already
overwhelmingly theme-ready, and every residual leak is behaviour-preserving refactor scope that
blocks nothing shipping today.
