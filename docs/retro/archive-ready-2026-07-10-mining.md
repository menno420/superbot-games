# Mining lane — ARCHIVE-READY note (gen-1 close-out)

> **Status:** `archive`
> Verified against source at main HEAD `5d38593` on 2026-07-11. Baseline for this
> note is the 2026-07-10 gen-1 close-out (mining PR #20 / prior heartbeat). This is a
> VERIFY + TOP-UP consolidation, not new feature work — it exists so nothing about the
> mining lane's archived state lives only in a soon-to-be-archived chat.

## Current true state (verified against source)

Mining **gen-1 is complete and already archived on `main`**. The pure domain
(`games/mining/core/**` — character, energy, capacity, equipment, items, exploration,
grid, `encounters.py`) plus the `games/mining/sim/` harness shipped and merged
(gen-1 PRs #5 pure-domain, #9 retro, #11 grid-encounters, #14 succession package, #15
status, #20 close-out heartbeat). `main` is strict-GREEN: `bootstrap.py check --strict`
exits 0; the mining suites pass. The two-lane mining/exploration split is itself
**archived**: since gen-1 close, a single **world-games seat** owns all of `games/**`
and writes the unified `control/inbox.md` + single-writer `control/status.md`
(`control/status-mining.md` and `control/inbox-mining.md` now carry a `⟵ GEN-1 HISTORY`
banner — read as archive, do not resurrect the split). Mining gen-1 nonetheless remains
exactly as delivered on `main`; nothing of it is parked, broken, or chat-only.

## ⚑ Owner-actions awaited

1. **Model-line vs. no-id-in-artifacts conflict — owner ruling pending (already flagged
   on main; recorded here durably).**
   - **WHAT:** the kit's strict gate (session telemetry / PL-004) hard-requires a
     `📊 Model:` line on every session card, which brushes against the standing "no
     model identifier in any repo artifact" rule.
   - **WHERE:** `.substrate` session-card gate (`substrate.config.json` `session_markers`
     → `📊 Model:` needle); every `.sessions/*.md` card; flagged in `control/status.md`
     `⚑ needs-owner` item (2).
   - **HOW (fix options):** (a) kit carve-out — the family-level model line is the ONE
     sanctioned place a model family may appear, never the exact internal id, never in
     commit/PR text; OR (b) amend the standing rule to name that carve-out explicitly.
   - **WHY-IT-MATTERS:** without a ruling, agents guess whether the card line violates
     the rule; the current working resolution is family-level-in-card-only.
   - **UNBLOCKS:** removes the last ambiguity between staying CI-green (gate needs the
     line) and the no-id rule.
   - **OWNER-ONLY / VERIFIED-NEEDED:** yes — this is a doctrine ruling, not derivable by
     an agent. **Current resolution in force:** the world-games seat records family-level
     `📊 Model: Opus 4.8` on cards only (never in commit/PR text), delivered as ORDER 003
     (#46); PR #52 likewise records a family-level production DM model ("Haiku-class") in a
     design doc. So the conflict is already CAPTURED and has a working resolution on main —
     only the formal ruling (carve-out vs amend) is outstanding.

2. **Aggregate `control/status.md` single-file kit item (standing).** The kit hardcodes a
   single `control/status.md`; gen-1 mining ran per-lane status files. This is now moot in
   practice — the fleet moved to a single world-games writer of `control/status.md` — but
   the upstream kit question (formalize single-writer vs support per-lane) is recorded as
   still-open for completeness. No mining action depends on it.

No other mining ⚑ owner-actions are open. The gen-1 merge-wall ⚑ is RESOLVED (all mining
PRs merged).

## What a fresh session needs to resume

**Read order:** `control/inbox.md` (unified orders) → `control/status.md` (live fleet
heartbeat) + `control/status-mining.md` (mining archive heartbeat) → `docs/lanes.md` +
`docs/founding-plan-mining.md` (both BINDING) → `docs/retro/next-boot-mining-2026-07-09.md`
(first-10-minutes guide + every known wall with verbatim errors) →
`docs/retro/queue-state-mining-2026-07-09.md` (done / next) →
`docs/retro/gen2-feedback-mining-2026-07-09.md`.

**Gen-2 next 1–3 (ordered, from the groomed queue-state doc):**
1. **Mint parity goldens** (ORDER 002, still 0 minted) — corpus has ~2 mining goldens for
   a 37-command surface; mint AS you port, the oracle mapping is only fresh once. **NOT
   blocked.**
2. **`games/mining/workflow/` audited-op seam** — the composition layer mirroring the
   oracle `mining_workflow`'s one-transaction-per-op pattern (mine / dig / explore /
   descend); pure core stays the decider, workflow is the sole write boundary. **NOT
   blocked.**
3. **superbot-next Layer-3 `SubsystemManifest` host adapter** — verify superbot-next's
   plugin / `SubsystemManifest` contract, then dock the pure core + workflow. **BLOCKED —
   cross-project wait (see below).**

**Routine state — NOT ARMED.** There is no scheduler in this environment; no timed
self-wake is scheduled. The next mining wake is **owner-initiated or webhook-driven (PR
events)** — not a promised timer.

## Cross-project dependency

Gen-2 item 3 (the superbot-next Layer-3 `SubsystemManifest` host adapter) is **BLOCKED on
superbot-next's decision D-0043** — the plugin/manifest contract the gen-1 mining design
doc assumed must exist and be decided in superbot-next before the pure core can dock. This
is a genuine **cross-project wait**, not this repo's to resolve. (D-0043 is named per the
gen-1 handoff; it lives in the superbot-next repo, which is not in this session's checkout,
so the id is relayed, not independently re-verified here.) Gen-2 items 1 and 2 (parity
goldens, workflow seam) are **pure-domain work in THIS repo and are NOT blocked** — the
lane has clear, unblocked buildable work whenever it next wakes.

## Grooming

The gen-2 queue (`docs/retro/queue-state-mining-2026-07-09.md`) is confirmed **groomed and
ordered**: next 1–3 present and unchanged, block status now annotated (items 1–2 free, item
3 cross-project-blocked on D-0043). No new feature work started (archive-prep is VERIFY +
TOP-UP only).

## Confirmation

After this note, **nothing important about the mining lane's archived state is chat-only** —
the true state, every open owner-action, the resume read-order, the gen-2 next 1–3 with
block status, the cross-project D-0043 wait, and the routine-not-armed fact are all durable
here and cross-linked from `docs/retro/README.md`.
