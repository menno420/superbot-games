# superbot-games — EAP closeout walkthrough (2026-07-14)

> **Status:** `owner-guidance`
>
> ORDER 009 (b) deliverable (`control/inbox.md` @ `ed2fabb`, landed via
> #136): the owner's review walkthrough for this seat at EAP close. Sections:
> A — what shipped (PR-cited) · B — current state + how to run/verify ·
> C — OWNER ACTIONS checklist · D — a 5-minute verify-it-yourself tour ·
> E — handoff notes. Every load-bearing claim cites a PR / SHA; nothing here
> is invented. The ≤40-line close-out summary carrying §C verbatim is in
> `control/outbox.md` § EAP CLOSE-OUT (heartbeat/outbox venue, per the
> order).

## A. What this seat did during the EAP (shipped, PR-cited)

From repo seed to EAP close (2026-07-09 → 2026-07-14), **136 PRs** landed on
main. The arc, compact (per-PR enumeration:
[`current-state.md`](current-state.md) § "Recently shipped"; depth: the seat's
close-out self-review
[`retro/close-out-world-games-2026-07-11.md`](retro/close-out-world-games-2026-07-11.md)
and the external fleet-cleanup audit
[`audit/2026-07-13-fleet-cleanup-audit.md`](audit/2026-07-13-fleet-cleanup-audit.md)):

- **Founding + gen-1 (#1–#13):** repo seeded (founding plans, lanes contract,
  control bus); exploration P1 deterministic quest/encounter engine +
  substrate-kit adoption (#3, D-0002); gen-1 retros and wind-down succession
  packages (#8/#9/#13).
- **Gen-2 world-games seat (#40s–#57):** D&D data-driven scene chaining (#50)
  + DM-clamp property fuzzer (#52), the canonical persistence contract (#53),
  the cross-domain economy sim + invariants (#54), the generated balance page
  + CI freshness check (#55), seat close-out + archive prep (#56/#57).
- **Kit currency (#58, #62–#64):** substrate-kit v1.12.0 → v1.15.0
  (`0082ee2`).
- **Playable-four-games night (#66–#80):** audited rung-2 WORKFLOW seams for
  all four games sharing `services/audit.py` (#68/#69/#75/#77), standalone
  CLIs (#70/#71), the game-neutral hub `python3 -m games` (#72 `ef18b4e`);
  suite 310 → 516.
- **Sim-verdict wiring (#82–#87):** sim-lab verdicts V042–V045 consumed
  (ORDER 007): V043 fishing sell/XP economy + V044 dnd mint-at-most-once
  guard wired VERBATIM (#83 `72a94bb`), all four SIM-REQUESTs closed with
  dispositions (#84 `9caf1b6`), economy surfaced on
  [`balance.md`](balance.md) + fishing CLI `sell` (#87 `67de572`); suite
  → 556.
- **ORDER 008 (#92/#93):** owner's bigger-batches + production-grade
  directive landed; the full-roster fishing SIM-REQUEST (29 legacy species,
  enumerated read-only, zero invented numbers) filed as ONE batch
  (`21937f3`).
- **Coverage + hardening waves (#95–#134):** four sub-80% modules → 100% and
  the tests workflow fixed to actually EXECUTE `services/tests/` (CI count
  442 → 606, #107 `24f6e04`); CLI/hub/sim coverage + three player-visible
  fixes (#115/#116/#117) + sim smoke registry (#119, → 695); tripwire
  registries (#122/#123/#126/#129/#132), shared REPL/scripted-driver seams
  (#127/#130/#134), gate-parity preflight → one-command flip-readiness
  (#128/#131/#133); suite → **810**, ~97% coverage of `games/` +
  `services/` at the #120 groom.
- **Truth discipline (#109/#120/#135, #61, #95):** the living ledger
  re-stamped at every wave with a machine-readable anchor +
  `tools/stamp_scaffold.py` (#120 `51590c6`).

## B. Current state + how to run/verify (exact commands)

**State:** four playable, audited, sim-pinned games behind one hub; zero open
PRs beyond the two ORDER 009 closeout PRs; all remaining balance constants
externally gated (sim-lab verdict batch, routed) or owner-gated (§C).

Run (repo root, Python ≥ 3.10, stdlib only):

```bash
python3 -m games                # hub — pick mining/fishing/dnd/exploration
python3 -m games.mining         # standalone: dig/descend/build/shop
python3 -m games.fishing        # standalone: cast/sell, V043 economy live
python3 -m games.dnd            # standalone: bounded-menu story scenes
python3 -m games.exploration    # standalone: quests + survival energy
```

Verify (what CI runs, byte-for-byte — gate parity by construction, #128):

```bash
python3 tools/preflight.py      # floor guard → pytest (all roots) → balance freshness
python3 -m pytest -q            # 810 passed at ed2fabb (2026-07-14)
python3 bootstrap.py check --strict   # docs + session-card hygiene, exit 0
```

## C. OWNER ACTIONS checklist

Four decision replies are awaited (all ↩️ reversible; no destructive click,
no merge click owed). Deep links: outbox =
<https://github.com/menno420/superbot-games/blob/main/control/outbox.md>,
host-adapter doc =
<https://github.com/menno420/superbot-games/blob/main/docs/design/mining-host-adapter.md>,
persistence doc =
<https://github.com/menno420/superbot-games/blob/main/docs/design/persistence-design.md>,
pulls = <https://github.com/menno420/superbot-games/pulls>.

The block below is the checklist of record — it is copied VERBATIM into
`control/outbox.md` § EAP CLOSE-OUT (the surfaced summary), so the two must
be edited together:

> OWNER ACTIONS (each: what · where · **recommendation** · verify):
> - [ ] 1. Ratify D2 (audit item-grants). WHERE: control/outbox.md
>       § DECISION-NOTE · D1/D2. RECOMMENDATION: **ratify D2 as built** —
>       full audit coverage; reversal stays a one-line toggle. RISK ↩️.
>       VERIFY: reply "D2 ratified"; the seat records it on the note.
> - [ ] 2. Rung-3 packaging + hermeticity (sbg becomes an installable
>       distribution importing sb.spec from superbot-next). WHERE:
>       docs/design/mining-host-adapter.md § ⚑ DECISION. RECOMMENDATION:
>       **approve packaging, sequenced after D2** — the rung-2 op the doc
>       waited on now exists (#68), so the adapter wraps a real op. RISK ↩️.
>       VERIFY: reply approve/defer; build starts only after this + D2.
> - [ ] 3. Persistence format-governance (contract-impl vs flat-local ·
>       namespace mapping · load-vs-audit). WHERE: control/outbox.md
>       § OWNER-QUEUE. RECOMMENDATION: **contract-impl per PR #53 (no rival
>       format) · per-game domain namespaces · load emits NO audit rows**.
>       RISK ↩️. VERIFY: reply the 3 picks; save/load is then mechanical.
> - [ ] 4. Transfer-policy source model. WHERE:
>       docs/design/persistence-design.md §5 (OWNER-DECIDES item 4).
>       RECOMMENDATION: **TRUE source-debit** — seeded-credit violates the
>       doc's own conservation invariant. RISK ↩️. VERIFY: reply the choice.
> - [ ] 5. No merge clicks owed: zero open PRs beyond this closeout pair;
>       both auto-land on green via the #67 enabler. If one parks green
>       un-merged, the click is Squash & merge at
>       github.com/menno420/superbot-games/pulls. RISK ✅. VERIFY: 0 open.

Awareness (no reply needed): the fishing full-roster + cook-leg SIM-REQUEST
batch is ROUTED to the sim-lab (via its ORDER 008, per ORDER 009 @
`ed2fabb`); the seat wires the verdict's constants VERBATIM on receipt.

## D. A 5-minute verify-it-yourself tour

1. **(1 min) Suite + hygiene:** clone, then `python3 -m pytest -q` —
   expect **810 passed**; `python3 bootstrap.py check --strict` — expect
   "all checks passed", exit 0. (✅ read-only)
2. **(1 min) Hub:** `python3 -m games` → the four-game menu; enter `2`
   (fishing) — the "Launching fishing…" banner prints BEFORE the session
   (the #117 fix, visible live). (✅ local state only)
3. **(2 min) V043 economy end-to-end:** in fishing, `cast` a few times, then
   `sell` — coins credit per the sim-pinned curve (minnow 8 / bass 13 /
   pike 27 / legend_carp 80), XP = size_rank, level-ups at
   `xp_to_next(L) = 50·L`; every mutation flows through the audited seam.
   Cross-check the same numbers on [`balance.md`](balance.md) § "Fishing
   economy (V043)" — that section is GENERATED from
   `games/fishing/core/economy.py` (#87), zero hand-copied literals.
   (✅ local state only)
4. **(1 min) Truth records:** `control/status.md` top = this seat's live
   heartbeat (truth-stamped 2026-07-14, orders `acked=001-009
   done=001-007`); `control/outbox.md` § EAP CLOSE-OUT = the ≤40-line
   summary + §C verbatim; the CI runs page shows the two closeout PRs green.
   (✅ read-only)

## E. Handoff notes (batons — what the next phase needs)

1. **Wire the full-roster + cook verdict batch on receipt** — the routed
   SIM-REQUEST (`control/outbox.md`, status `routed`) covers 29 species'
   sell/XP values plus the cook leg; wiring is VERBATIM into
   `games/fishing/core/economy.py` + `services/fishing_workflow.py` with the
   sell-OR-cook haul-debit exclusivity already structural (#83). Watch
   VERDICT 042's FAUCET-BYPASS guardrail (PROPOSAL 035) on any
   energy-restore constants.
2. **Rung-3 host-adapter** — build order per
   [`design/mining-host-adapter.md`](design/mining-host-adapter.md) §7 once
   §C items 1–2 are ratified: adapter wraps the live
   `services/mining_workflow.py` op, plus a superbot-next host PR to pin it
   in `plugins.lock.json`.
3. **Persistence build** — mechanical after §C items 3–4:
   state dataclasses are cleanly JSON-serializable (outbox OWNER-QUEUE has
   the field inventory); do NOT ship a serializer before the governance
   picks land.
4. **Exploration numeric band import** — reopens ONLY when the upstream
   superbot P0 survival balance-sim artifact (Q-0087 / D-0008) lands; V045
   ratified the placeholders with an honest NULL meanwhile.
5. **Ledger hygiene** — `docs/current-state.md` "In flight" still describes
   #102 as an open PR; it merged 2026-07-14T07:20:35Z (`1c323c1`). Next
   truth-stamp groom should record #102/#135/#136 + this closeout pair
   (scaffold: `python3 tools/stamp_scaffold.py`).
