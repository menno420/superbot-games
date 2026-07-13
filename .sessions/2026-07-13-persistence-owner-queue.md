# 2026-07-13 · persistence owner-queue entry (standalone-CLI save/load · docs)

> **Status:** ✅ `complete`
>
> 📊 Model: Opus 4.8 · 2026-07-13T01:52:31Z · persistence owner-queue entry

## 💡 Session idea

Both standalone CLIs now drive their audited seams end to end
(`python3 -m games.mining` / `python3 -m games.fishing`), but neither can SAVE:
close the terminal and the session is gone. The last standalone-polish item is
save/load — and a scoping pass shows the blocker is NOT the data shape. The two
session states are cleanly JSON-serializable: `MiningState`
(`services/mining_workflow.py`) is plain `int`/`str`/`dict` plus one all-int
nested `EnergyState` (`games/mining/core/energy.py`: `current`/`updated_at`), and
`FishingState` (`services/fishing_workflow.py`) is `seed`/`spot_id`/`energy`
(int/str) + a `{species_id: count}` haul dict + an optional all-int
`EffectiveStats` (`games/mining/core/equipment.py`). No RNG or live instance is
held in either. So the blocker is FORMAT GOVERNANCE, not data: PR #53 just merged
the canonical namespaced/versioned `PlayerState` contract
(`docs/design/persistence-design.md`, `status: plan` — docs-only, zero
implementing `serialize`/`deserialize`/`PlayerState` code, grep-confirmed), and
shipping a second CLI-local flat JSON days later would fragment persistence. This
session does NOT build save/load; it records the decision the build waits on as a
six-field ⚑ OWNER-ACTION / OWNER-QUEUE entry appended to `control/outbox.md`
(the owner-facing SIM-REQUEST/decision channel), citing three coupled
sub-decisions: contract-impl vs flat-local (and §1 assigns filesystem/storage to
the `superbot-next` host, so CLI file I/O may not belong in this repo at all);
the field→namespace mapping the contract leaves unspecified for the real state
shapes (coins + inventory → `shared-inventory` per §2 "wealth is not
double-stored"; haul/depth/structures/seed unassigned); and whether `load`
reconstructs state WITHOUT emitting audit rows — which turns on the still-open
D2 audit-boundary ratification in the same file. No balance number is invented;
no code ships. docs/control-only.

## ⟲ Previous-session review

Builds on the two 2026-07-13 standalone-CLI cards
(`.sessions/2026-07-13-mining-standalone-cli.md`,
`.sessions/2026-07-13-fishing-standalone-cli.md`), which delivered the playable
loops and each explicitly kept economy tuning as a SIM-REQUEST in
`control/outbox.md` rather than inventing numbers. This session follows the same
discipline for persistence: rather than silently pick a serialization format, it
routes the choice to the owner through the same decision channel. It consumes,
but does not modify, PR #53's persistence contract and the open D1/D2
audit-schema DECISION-NOTE already in `control/outbox.md`.
