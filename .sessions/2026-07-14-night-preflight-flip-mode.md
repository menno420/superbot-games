# 2026-07-14 · night build — ci: preflight --flip — one command to flip-readiness

> **Status:** in-progress
>
> 📊 Model: Fable · 2026-07-14T04:12:45Z · night-preflight-flip-mode

Build slice from #128's card idea: `tools/preflight.py` gains a `--flip`
mode appending step 4 = `python3 bootstrap.py check --strict`, so
flip-readiness is one command. Default 3-step behavior stays
byte-compatible for CI (tests.yml unchanged). Unit tests: argument wiring,
step-4 invocation, red propagation, and the strict born-red HOLD semantics
pinned via `--session-log` against a synthetic in-progress card.

## 💡 Session idea

(pending — filled at flip)

## ⟲ Previous-session review

(pending — filled at flip)
