# 2026-07-14 — kit upgrade v1.15.0 → v1.16.0

> **Status:** `in-progress`

📊 Model: Fable

## What is about to happen

Substrate-kit distribution wave: upgrade this repo's kit pin from v1.15.0 to
v1.16.0 using the canonical two-command recipe (`bootstrap.py.new upgrade`
then `upgrade --apply-docs`), release asset three-way sha256-verified
(bba34e2102cbaf09394f39992f0501ea5cfd542d90301ef67e31a0854ca59170,
980,026 bytes), followed by `check --strict`. Rails per Q-0261.3: kit-owned
files only; no control/, hooks, settings, or product-code edits. Auto-merge
is never armed by this session (the #40 lesson lives here); the resident
live enabler merging on green after the final card flip is the sanctioned
landing path.
