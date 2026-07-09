# 2026-07-09 · Port the pure mining domain (games/mining/core)

> **Status:** `in-progress`
>
> 📊 Model: automation-agent · high · port · lane: game-mining · branch: mining/port-pure-domain

## Goal (what I'm about to do)

Execute mining **ORDER 001 step 4 / ORDER 002**: begin the P0→P1 port. Stack on the
kit-adoption work (draft PR #4, `mining/adopt-substrate-kit`) and land the **pure
mining domain** as `games/mining/core/` — all 18 pure oracle modules
(`disbot/utils/mining/*` + `disbot/utils/equipment.py`) ported VERBATIM (formulas
and balance constants unchanged, "preserved-from-oracle"), Discord/DB/IO-free,
with unit tests. Sever the two fishing couplings (items→fish SPECIES import,
structures→4 fishing structures). Write the plugin-layout design doc mapping the
pure core onto superbot-next's `SubsystemManifest` contract. This PR ships the
pure-core slice only; workflow + host-adapter layers are named-next.

_This card opens the PR born-red; it flips to `complete` as the deliberate final
step once the port + tests + docs land and `bootstrap.py check --strict` is green._
