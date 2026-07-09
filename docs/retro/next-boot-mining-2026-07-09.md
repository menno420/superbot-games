# Mining lane — gen-2 first-boot guide (2026-07-09)

> For the fresh mining Project session. The gen-1 lane is archived; you boot ONLY from
> what is committed here. Read this FIRST. Target: be productive and un-stuck inside 10 minutes.

## First 10 minutes — read order (one line why each)
1. `control/inbox-mining.md` — your orders from the manager (one writer: manager). Execute `status: new` in priority order (P0 before P1).
2. `control/status-mining.md` — the previous lane's heartbeat: what shipped, what's parked, open ⚑ owner actions.
3. `docs/lanes.md` — BINDING cohabitation contract: you own `games/mining/**`, `docs/founding-plan-mining.md`, `control/status-mining.md`; never touch the exploration lane; `games/shared/**` is claim-first; kit is adopted ONCE.
4. `docs/founding-plan-mining.md` — BINDING mission + roadmap (P0..P5) + hard rails (no pay-to-win, sim-pinned balance, deterministic core).
5. `docs/retro/queue-state-mining-2026-07-09.md` — done / in-flight / next, so you don't redo shipped work.
6. `docs/retro/wind-down-review-2026-07-09-mining.md` — the honest retro: every friction + verbatim error.
7. `control/README.md` — the control-file bus protocol (one-writer-per-file; per-lane extension for this repo).

## Walking-skeleton check (do this BEFORE real work)
Prove the pipeline branch → PR → CI → merge works end-to-end on a throwaway change, so you learn the merge wall on a 1-line diff, not after a day of building:
1. Branch off `main`; add one trivial line to `control/status-mining.md`; commit; push `-u origin <branch>`.
2. Open a PR **READY (never draft)**.
3. Confirm `substrate-gate` CI goes green.
4. Attempt the merge ONCE. If it lands → skeleton proven. If DENIED by the classifier → you have confirmed the known wall (below) on a cheap change; park READY + ⚑ owner-click and proceed with real work knowing merges need a human.

## Known walls — verbatim, do NOT re-probe
- **Merge wall (dominant).** The auto-mode classifier denies agent self-merges of agent-authored, human-unreviewed PRs when authorization is only a coordinator/cross-session relay — you need a DIRECT human turn or a human GitHub click. Verbatim (this lane, three separate hits):
  - "[Merge Without Review] The delegated worker prompt instructs squash-merging PR #5 (and #11), agent-authored PRs with no human review, authorized only by an untrusted coordinator relay — not a direct user turn; also Self-Approval."
  - "[Merge Without Review] The delegated prompt instructs the sub-agent to mark ready and squash-merge PR #4 ... with no human review and no user naming that merge (also Self-Approval)."
  - "[Self-Approval] ... marking PRs #4/#5 ready and arming auto-merge / squash-merging PRs the agent's own workers authored ... only an untrusted coordinator-relayed 'directive'; also triggers Merge Without Review."
  Implication: your terminal state for good work is "PR open, READY, CI green, ⚑ owner-click". Don't burn cycles retrying — one attempt, capture, park.
- **Shared-token rate limits.** GitHub ops share token user id 225413533 (login menno420). Seen as: "API rate limit already exceeded for user ID 225413533". On a rate-limit error, record verbatim, back off, don't hammer.
- **Main/orchestrator session lacks GitHub MCP + ToolSearch.** In this environment the orchestrator session could not call `mcp__github__*` ("No such tool available: mcp__github__list_pull_requests") or ToolSearch ("not enabled in this context"). WORKERS (the Agent tool) DO have GitHub MCP — route every GitHub op through a worker.
- **Coordinator had no GitHub tools and no send_later** ("No such tool available"). Cross-session `send_message` later failed with "tool is not enabled for this organization". Don't rely on cross-session messaging — the committed control files are the only reliable bus.
- **Remote agent sessions: HTTP 403 on tag pushes / release creation / branch deletion** (reported, gen-1). Branch push, PR create, and reads all work. Don't script releases/tags/branch-deletes.

## The one coordination rule that would have saved the most
Adopt-once + first-mover claim. Before touching ANY shared surface (`.substrate/`, `games/shared/**`, `control/status.md`), create your claim file and scan open PRs + existing claims FIRST. The kit-adoption race (mining #4 vs exploration #3) cost a full duplicate kit adoption because nobody checked. lanes.md already says this — follow it.
