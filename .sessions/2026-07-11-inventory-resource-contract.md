# 2026-07-11 · Unified inventory/resource contract (design)

> **Status:** `in-progress`
>
> 📊 Model: Claude Opus · 2026-07-11T00:26:40Z · design doc unifying item/reward/inventory across world games

## Goal

Deliver ONE merged-on-green PR carrying a **plan/reference design doc**,
`docs/design/world-inventory-resource-contract.md`, that unifies how the world-games
systems (mining, exploration/quest, fishing, shared/encounter) represent an **item**, a
**quantity/stack**, a **reward/grant**, and **inventory capacity**. This is a PLAN doc —
NOT an implementation. No system code, README, tests.yml, or inbox is touched. The doc
must be grounded in the real, divergent representations found in the code (file:line
citations), propose a single pure-domain contract (frozen dataclasses / Protocol,
plugin-package-friendly, Q-0267 nouns-in-data), argue for `games/shared/inventory/` as its
home (claim-first shared surface), lay out an incremental per-system migration path, hold
the integrity floor (deterministic, no pay-to-win, theme-ready), flag genuine
owner-decisions, and specify a shared conformance test each adapter runs.

## What shipped

_(filled at close — born red first commit)_

## 💡 Session idea

_(filled at close)_

## ⟲ Previous-session review

_(filled at close)_
