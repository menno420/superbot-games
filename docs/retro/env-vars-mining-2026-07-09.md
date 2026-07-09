# Mining lane — environment variable NAMES (gen-2 handoff)

> **Status:** `audit`
> NAMES ONLY — never values, never secrets. The mining lane is a PURE domain with
> NO live infrastructure (`docs/founding-plan-mining.md`), so it requires ZERO runtime
> env vars. Everything below is optional / harness-provided. Paired with `environments/setup-mining.sh`.

## Required at runtime
- **(none)** — the pure-domain port and its tests need no environment configuration.
  Determinism is by injected RNG/clock, not env.

## Optional / harness-provided (do NOT set values in the repo)
- `GITHUB_TOKEN` — harness-managed; used by the GitHub MCP tools (route GitHub ops through a
  worker; the main session had no GitHub MCP in gen-1). Shared across the fleet under user id
  225413533 — subject to rate limits.
- `HTTPS_PROXY` / `HTTP_PROXY` — set by the remote environment's network policy; outbound HTTPS
  flows through the agent proxy. Do not unset; do not disable TLS verification.
- `PYTHONPATH` — only if you run tests from a non-root cwd; the setup script does not need it.

## Do NOT
- Do NOT add a bare `pip install -r requirements.txt` step — there is no runtime service manifest
  to install; `setup-mining.sh` installs only the test toolchain, non-fatally.
- Do NOT put any token, key, or value into committed files or the team memory directory.
