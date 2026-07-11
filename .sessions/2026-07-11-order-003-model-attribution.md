# 2026-07-11 · ORDER 003 — model-attribution ground truth (family-level 📊 Model line)

> **Status:** `complete`
>
> 📊 Model: Opus 4.8 · 2026-07-11T13:20:07Z · ORDER 003 model-attribution rule

## Goal

Consume **ORDER 003 (P3, model-attribution ground truth)**. Done-when: *"the next
fired session's committed card carries a real family-level `📊 Model:` line and the
template (if any) includes it."* The rule (Q-0262): every fired session's committed
session card carries a `📊 Model:` line naming the model **family** its own
harness/environment reports — family-level only (examples: `fable-5`, `opus-4.8`,
`sonnet-5`), sourced from the session's own harness, **never** the Routines/schedule
screen (cross-surface attribution disagreement per fm model-matrix), and never the
full dated internal id.

This session's environment reports family **Opus 4.8**, so this card self-reports
`📊 Model: Opus 4.8` — this committed card IS the "next fired session's card carries
a real family-level 📊 Model line" deliverable.

## What shipped

- **`.sessions/2026-07-11-order-003-model-attribution.md`** (this card) — born-red →
  complete, carrying a real family-level `📊 Model: Opus 4.8` self-report line.
- **`.sessions/README.md`** — verified it already documents the `📊 Model:`
  requirement: the completeness marker list (Status badge, Session idea,
  Previous-session review, **Model line**) plus the kit-owned model-attribution
  doctrine block (`<!-- substrate-kit: model-attribution doctrine … ORDER 012 -->`)
  that mandates family-level names from the session's own harness. No template edit
  needed — the requirement was already present and survives kit regen (it lives in
  the doctrine block the kit merges into the README, not in a regenerated template).

## 💡 Session idea

The attribution ground truth is the *committed card's own self-report*, not any
external dashboard — because the harness that writes the card is the only surface
that knows which family actually ran. `substrate.config.json` `session_markers`
already carries the `📊 Model:` needle, so `bootstrap.py check` enforces the line at
the completeness gate; the doctrine only needs the family-level discipline in the
human-readable README, which it has. Enforcement + doctrine are already wired — the
recurring cost is purely authoring discipline, which a born-red template line removes.

## ⟲ Previous-session review

The model-attribution doctrine block landed via ORDER 012 (the
`_merge_model_doctrine` path in `bootstrap.py`), and the `📊 Model:` needle joined
`session_markers` at kit upgrade (KL-3, added at v1.9.0-era upgrade time). Earlier
cards vary in format — some blockquote (`> 📊 Model:`), some bullet
(`- **📊 Model:**`) — and some still carry non-family strings (e.g.
`2026-07-11-mining-narration-data.md` reads `📊 Model: Claude Opus`, a display name
rather than a family id like `opus-4.8`). ORDER 003 pins the going-forward rule:
family-level, harness-sourced. This card sets the example.

## Guard recipe

Completeness anchor: `check_log` / `_default_session_markers` in `bootstrap.py`
(needle `📊 Model:` from `config.session_markers`); the gate target is
`python3 bootstrap.py check --strict`. The family-level doctrine lives in
`.sessions/README.md` under the `substrate-kit: model-attribution doctrine` comment
(merged by `_merge_model_doctrine`). If a future card records a display name or dated
id instead of a family name, the needle still passes — the family-level rule is
doctrine, not machine-enforced; correct at authoring time.
