# Gen-2 feedback — mining lane (2026-07-09)

> **Status:** `audit`
> Titled clearly per the wind-down order. The few structural changes I'd most want gen-2 to make,
> from lived mining-lane experience. Terse on purpose.

1. **Merge authority must be a direct human turn (or a human GitHub click) — never a coordinator
   relay.** The #1 finding. The auto-mode classifier denied every relayed self-merge (three verbatim
   denials in the wind-down review §5a). Design human merge-authorization as a first-class, expected
   step, not an exception. Don't ask agents to launder merges through the coordinator; it cannot work
   and wastes attempts.

2. **Enforce adopt-once with a first-mover claim check before ANY shared-surface work.** The kit race
   (mining #4 vs exploration #3, ~19 min duplicate work, #4 closed) happened because neither lane
   checked claims/open PRs before adopting. Make "scan claims + open PRs, then claim, then act" a hard
   pre-step for `.substrate/`, `games/shared/**`, and `control/status.md`.

3. **Keep per-lane status files; fix the kit's single-`control/status.md` assumption.** The kit
   hardcodes one `control/status.md`; this repo correctly runs per-lane files. That mismatch is a
   standing two-writer risk on shared ground. Either patch the kit to be per-lane aware or formalize
   the aggregate `control/status.md` as manager-written-only. Per-lane status is the right model —
   don't collapse it back.

4. **Put GitHub tools on the orchestrator, or state up front they're worker-only.** Gen-1 wasted
   discovery turns finding the main session couldn't call `mcp__github__*`. Either fix it or document
   it as expected.

5. **Give the coordinator real cross-session reach, or stop depending on it.** The coordinator had no
   GitHub tools, no send_later, and cross-session send_message failed ("tool is not enabled for this
   organization"). The committed control files ended up the only reliable bus — fine, but then design
   *for* that and don't route anything critical through live cross-session messaging.

6. **Make "terminal = READY + CI green + ⚑ owner-click" the explicit contract**, so a session that
   parks correctly is a success, not a stall. Half of gen-1's friction was treating an
   unmergeable-by-agent PR as a problem to keep fighting instead of a defined handoff state.
