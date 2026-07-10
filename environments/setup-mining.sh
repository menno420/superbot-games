#!/usr/bin/env bash
# setup-mining.sh — defensive environment bootstrap for the superbot-games mining lane.
#
# Contract (from gen-1 wind-down, deliverable 5):
#   * ALWAYS exits 0 — a setup script must never fail the environment boot.
#   * Assumes NOTHING about repo shape — every path is probed before use.
#   * All installs are NON-FATAL — a missing package degrades, never aborts.
#   * NO bare `pip install -r requirements.txt` — the mining lane is a PURE domain
#     with no live infrastructure; it needs no runtime service deps. We install only
#     the test/lint toolchain, and only if a manifest for it actually exists.
#
# Env vars: NONE are required (pure domain, no live infra). See
# docs/retro/env-vars-mining-2026-07-09.md for the optional NAMES the harness may provide.

set +e            # non-fatal: keep going past any single failure
set +u            # unset vars are not errors here

log() { printf '[setup-mining] %s\n' "$*"; }

log "starting defensive bootstrap ($(date -u 2>/dev/null || echo 'date unavailable'))"

# --- locate a Python 3.10 interpreter (CI pins 3.10); fall back gracefully -------
PY=""
for cand in python3.10 python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then PY="$cand"; break; fi
done
if [ -n "$PY" ]; then
  log "python: $PY ($("$PY" --version 2>&1))"
else
  log "WARN: no python interpreter found on PATH — skipping python steps"
fi

# --- ensure pip is available (non-fatal) ----------------------------------------
if [ -n "$PY" ]; then
  if ! "$PY" -m pip --version >/dev/null 2>&1; then
    log "pip not present; attempting ensurepip (non-fatal)"
    "$PY" -m ensurepip --upgrade >/dev/null 2>&1 || log "WARN: ensurepip failed — continuing"
  fi
fi

# --- install the TEST/LINT toolchain only, and only from a dev manifest ----------
# Never a bare runtime requirements install: the pure domain has no service deps.
install_pkg() {
  # install_pkg <pip-name> — best-effort, never fatal
  [ -z "$PY" ] && return 0
  "$PY" -m pip install --quiet --disable-pip-version-check "$1" >/dev/null 2>&1 \
    && log "installed: $1" \
    || log "WARN: could not install $1 — continuing"
}

if [ -n "$PY" ]; then
  DEV_REQ=""
  for f in requirements-dev.txt requirements/dev.txt dev-requirements.txt; do
    [ -f "$f" ] && DEV_REQ="$f" && break
  done
  if [ -n "$DEV_REQ" ]; then
    log "dev manifest found: $DEV_REQ (installing, non-fatal)"
    "$PY" -m pip install --quiet --disable-pip-version-check -r "$DEV_REQ" >/dev/null 2>&1 \
      && log "installed dev manifest" \
      || log "WARN: dev manifest install failed — continuing"
  else
    log "no dev manifest; installing pytest directly (non-fatal)"
    install_pkg pytest
  fi
fi

# --- substrate-kit gate: run its strict check if the kit is engaged --------------
if [ -d ".substrate" ]; then
  log ".substrate/ present — attempting kit check (non-fatal)"
  if [ -f ".substrate/bin/check" ]; then
    bash .substrate/bin/check --strict >/dev/null 2>&1 \
      && log "substrate check: PASS" \
      || log "substrate check: reported issues (non-fatal here; CI is the gate)"
  elif [ -n "$PY" ] && [ -f "bootstrap.py" ]; then
    "$PY" bootstrap.py check --strict >/dev/null 2>&1 \
      && log "bootstrap check: PASS" \
      || log "bootstrap check: reported issues (non-fatal here)"
  else
    log "no runnable kit check entrypoint found — skipping"
  fi
else
  log "no .substrate/ in this checkout (expected on a fresh lane branch) — skipping kit check"
fi

# --- smoke: run the mining core tests if they exist on this checkout -------------
if [ -n "$PY" ] && [ -d "games/mining" ]; then
  log "games/mining present — running a quick test smoke (non-fatal)"
  "$PY" -m pytest -q tests/mining >/dev/null 2>&1 \
    && log "mining tests: PASS" \
    || log "mining tests: not run / not green here (non-fatal; CI is authoritative)"
else
  log "games/mining not on this checkout (lives on PR #5 until merged) — skipping test smoke"
fi

log "bootstrap complete — exiting 0 by contract"
exit 0
