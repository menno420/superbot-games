#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup-exploration.sh — exploration-lane environment setup (gen-2)
#
# Canonical copy: menno420/superbot-games · environment/setup-exploration.sh
# Owner pastes this into: claude.ai/code → Environments → <env> → Setup script.
# Pattern mirrors the fleet template (menno420/fleet-manager ·
# environments/templates/setup-universal.sh) — read this session, 2026-07-09.
#
# CONTRACT (fleet playbook R15): this script NEVER fails the session.
# A failing setup script = dead session, no signal. Every step is non-fatal
# and the script ALWAYS exits 0. Worst case is a session with missing deps
# that can still report and self-repair; that beats no session at all.
#
# Lane facts this script assumes NOTHING about but exploits when true:
#   - games/exploration + games/shared are pure stdlib Python (no
#     requirements.txt exists at wind-down; zero installs needed).
#   - bootstrap.py (substrate-kit) needs only python3.
#   - TESTED 2026-07-09 by the wind-down session: two runs (repo dir + clean
#     empty dir), exit 0 both times — evidence in the wind-down retro/PR #13.
# ---------------------------------------------------------------------------

# --- Block 1: defensive posture ---------------------------------------------
# set +e     -> a non-zero step must not abort the script.
# no set -u  -> unset variables are tolerated, never fatal.
# no pipefail-> a hiccup mid-pipe is tolerated, never fatal.
set +e

log() { echo "[env-setup:exploration] $*"; }

# --- Block 2: per-repo setup -------------------------------------------------
# Detection order, most-specific first; every branch guarded.
setup_one() {
  repo_dir="$1"
  name="$(basename "$repo_dir")"
  if [ -f "$repo_dir/scripts/env-setup.sh" ]; then
    log "$name: running scripts/env-setup.sh"
    ( cd "$repo_dir" && bash scripts/env-setup.sh ) \
      || log "$name: env-setup.sh failed (non-fatal, continuing)"
  elif [ -f "$repo_dir/requirements.txt" ]; then
    log "$name: python3 -m pip install -r requirements.txt"
    ( cd "$repo_dir" && python3 -m pip install --quiet -r requirements.txt ) \
      || log "$name: pip install failed (non-fatal, continuing)"
  else
    log "$name: no scripts/env-setup.sh or requirements.txt — pure-stdlib lane, nothing to install"
  fi
  # Lane sanity probes — informational only, never fatal:
  if command -v python3 >/dev/null 2>&1; then
    log "$name: python3 = $(python3 --version 2>&1)"
    if [ -f "$repo_dir/bootstrap.py" ]; then
      ( cd "$repo_dir" && python3 bootstrap.py check >/dev/null 2>&1 ) \
        && log "$name: bootstrap.py check — green" \
        || log "$name: bootstrap.py check reported findings or could not run (non-fatal; run it in-session)"
    fi
  else
    log "$name: python3 missing — session must self-report this"
  fi
}

# --- Block 3: multi-repo vs single-repo detection ----------------------------
if [ -d .git ]; then
  setup_one "$PWD"
else
  found=0
  for d in */; do
    [ -d "$d/.git" ] || continue
    found=1
    setup_one "$PWD/${d%/}"
  done
  [ "$found" -eq 1 ] || setup_one "$PWD"
fi

# --- Block 4: env var contract (NAMES ONLY — never values here) ---------------
# The exploration lane's domain code needs NO secrets: pure-stdlib Python,
# no live infrastructure, no DB, no Discord token (host integration is P4,
# superbot-next's job). The only variables the *session tooling* relies on
# are platform-provided; listed so a gen-2 owner scopes the environment
# minimally and adds nothing else:
#   GITHUB_TOKEN (or the platform's git-proxy equivalent) — push/PR/merge
#   HTTPS_PROXY / SSL_CERT_FILE-style proxy vars — platform-managed, do not unset
# Explicitly NOT needed (do not add): Railway IDs (production bot!), Discord
# tokens, database URLs, Anthropic API keys.
log "env vars: lane needs none beyond platform git access (names doc above)"

# --- Block 5: unconditional success -------------------------------------------
# The single most important line in the file (R15). Do not "improve" this.
log "setup complete (defensive shim: always exit 0)"
exit 0
