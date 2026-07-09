# game-mining · status

updated: 2026-07-09T18:30Z
phase: pure-domain port — games/mining/core landed (ORDER 001 step 4 begun); workflow + host-adapter next
health: green
last-shipped: none merged yet — draft PRs in flight: #4 (kit adoption) + #5 (pure-domain port, stacked on #4)
kit: substrate-kit v1.2.0 (`check --strict` green)
blockers: none (merge sequencing of #4 → #5 is the owner's call — see needs-owner)
orders: acked=001,002 done=
⚑ needs-owner:
  (a) Merge sequencing — PR #5 (pure-domain port) is stacked on PR #4 (kit adoption); both
      are draft. Merge #4 first, then #5 (its base is `mining/adopt-substrate-kit`, so
      GitHub re-targets it to `main` after #4 lands). Owner sequences both.
  (b) Aggregate `control/status.md` two-writer risk — the kit checker
      `check_status_current` hardcodes `control/status.md` while this repo uses per-lane
      status files; an aggregate pointer is the current workaround. Durable fix is kit-side
      (per-lane heartbeat awareness). [carried from adopt session]
  (c) superbot-next host contract — RESOLVED this session: the `SubsystemManifest` contract
      exists concretely in superbot-next (`sb/spec/manifest.py`, `sb/manifest/mining.py`,
      `sb/domain/mining/*`); mining core-loop is live there, deep systems pending on D-0043.
      The pure core docks onto it via the Layer-3 adapter (design doc §3). No owner action
      needed — flagged for awareness.
notes: |
  This session (pure-domain port):
   - Ported all 18 pure oracle modules (disbot/utils/mining/* + disbot/utils/equipment.py)
     into games/mining/core/ VERBATIM (every formula + balance constant unchanged;
     sim-pinned upstream, pinned here as "preserved-from-oracle, unchanged" — no new
     tuning, no pay-to-win). stdlib only; verified zero discord/DB/IO/services/cogs/views
     imports (a purity guard test asserts it).
   - Severed the two fishing couplings + one IO coupling (design doc §5):
       * items.py: dropped `utils.fishing.fish.SPECIES` import → `register_fish_species`
         injection point (structural FishLike protocol).
       * structures.py: dropped the 4 fishing structures (tide pool/dock/boathouse/fishery);
         forge/home/campfire remain; generic registry shape unchanged.
       * recipes.py: dropped filesystem loader → in-code DEFAULT_RECIPES + `overrides`
         injection (keeps the core pure).
     Retained verbatim as inert data (no fishing dependency): equipment fishing-charm rows +
     fishing stat fields, market fishing-charm shop rows + fishing `*_BUILD_REASON` strings.
   - Behaviour-preserving enhancement: optional injectable `rng` on the reward rolls
     (`rng=None` = byte-identical to oracle; matches oracle's exploration.resolve + next's
     own mining port). Enables deterministic tests.
   - 62 unit tests, all green (ore-weight/depth reweight, mine-roll math, energy/capacity/
     vault, skill caps + forced specialization, forge gating, additive-safety invariant,
     grid seed-determinism incl. process-independence + negative coords, fish severance +
     injection, recipes purity, purity guard).
   - Design doc: docs/design/mining-plugin-layout.md (three-layer split, host-contract
     mapping, port DAG, severances, sim-pinned-balance statement, grid-encounters seam
     DESIGNED-not-implemented). Linked from AGENT_ORIENTATION.
  ⚑ Self-initiated decisions (reversible; flagged for review):
   - Placed equipment.py under games/mining/core/ (not games/shared/) to stay in-lane and
     unblocked; flagged as a promotion candidate for games/shared/ when a 2nd game ports
     (that's the claim-first moment). Rationale: no second game has ported yet.
   - Threaded optional `rng` through the reward rolls (behaviour-preserving; see above).
   - Placed tests at tests/mining/ (no pre-existing test dir; standard pytest discovery).
  Named-next (not this session): games/mining/workflow (audited op seam), the Layer-3
  superbot-next adapter, the grid-encounters extension, the economy sim + parity goldens.
  ORDER 002 defaults remain the working plan (no vetoes).
