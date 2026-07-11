# World-games seat — Archive-ready (2026-07-11)

> **Status:** `archive` — the durable resume+action note for when this session's chat is gone.

## True state (one paragraph)
World-games is a gen-2 single seat owning games/**. main HEAD 5d38593, substrate-kit v1.12.0, `bootstrap.py check --strict` exit 0. This session merged 10 PRs delivering: the CI collection fix + a self-maintaining per-suite test-floor mechanism (per-suite EXPECTED_MIN_TESTS.txt + tests/EXPECTED_SUITES.txt registry) + per-domain docs/design/*-index.md; Q-0267 mining data-isolation (R1 #31 + R2 #36); the exploration survival sim harness (P2 #32); two fleet orders (model-attribution #46, self-review #47); and the D&D story game — design (#38), runnable bounded-menu walking skeleton (#48), menu-balance sim (#49). Five PRs are open, green, clean, and parked for owner merge: #50 (D&D scene-chaining), #52 (D&D DM-clamp fuzz + Haiku-model addendum), #53 (persistence/transfer contract), #54 (cross-domain economy sim), #55 (auto-generated balance page). Integrity floor held throughout: deterministic code owns every outcome, balance numbers sim-pinned, no pay-to-win, the AI Dungeon Master stays bounded-menu.

## ⚑ EVERY owner action outstanding
1. Merge the 5 open PRs — #50, #52, #53, #54, #55 (Squash & merge; agent self-merge is classifier-blocked). If #50 & #52 collide on tests/dnd/EXPECTED_MIN_TESTS.txt, merge one then bump the other's floor by one line.
2. Decide transfer-policy source model: TRUE source-debit vs seeded-credit (persistence §5, #53 item 4). Working assumption = true debit.
3. (Optional) enable a branch-protection merge queue to serialize merges.

## Resume spec for a fresh session
- Land on origin/main HEAD; read control/inbox.md, this note, and docs/retro/close-out-world-games-2026-07-11.md.
- WAKE MECHANICS (being DISARMED at archive — a resuming session must RE-ARM per Q-0265 to run continuous): cron `15 */2 * * *` named "superbot-games failsafe wake" + a ~15-minute send_later continuation chain ("continue the work loop"). Cron = dead-man failsafe; send_later chain = pacemaker.
- Work queue (priority order): CLI demo + boot script (owner-requested; after #50 merges) → economy follow-up PR (after #53/#54/#55 merge) → D&D P-queue (DM-prompt hardening / more scenes / save-resume) → inventory migrations 2–6 (sibling) → theme skin-split (waits on idle-lane manifest). Content posture: RAW VOLUME FIRST, finetune later.
- Merge reality: no agent self-merge (deny-wins); owner click or a direct in-session "merge" turn is the only path.

## Cross-project dependencies (name them for whoever resumes)
- superbot-next plugin host — needed before any of this is actually playable in the bot (manifest/plugin contract).
- idle-lane manifest format — the theme core/skin split (Q-0267) waits on it.
- superbot root — the persistence implementation that #53's save-state contract targets.

## Chat-only confirmation
Nothing important remains chat-only: every ruling, incident (retired seat, review gap), owner answer, open decision, and follow-up spec is captured here + in the close-out retro + in the #52/#53 PR bodies.
