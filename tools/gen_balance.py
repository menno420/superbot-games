#!/usr/bin/env python3
"""Deterministically regenerate ``docs/balance.md`` from the shipped economy code.

The owner wants to eyeball the whole world-games economy at a glance: every
sim-pinned number, per-domain emission ceiling, and cap that the resolvers,
catalogs, and suite floors already own — collected onto ONE page. This script
is the single source of truth for that page.

READS ONLY. This generator never changes a resolver / balance constant; it
imports the shipped modules, reads their constants, and formats them. If a
number looks wrong, that is a bug in the source module, not here — report it,
do not "fix" it in this file.

Determinism (so ``--check`` never flaps):

* every dict is sorted before it is emitted,
* every float is formatted through :func:`_num` (fixed precision, trailing
  zeros stripped) so ``3.0`` and ``0.6000`` render stably,
* the section order is fixed and there are no timestamps, no randomness, and
  no environment-dependent values.

The committed ``docs/balance.md`` MUST be byte-identical to :func:`render`'s
output; CI enforces this with ``python3 tools/gen_balance.py --check``.

CLI
---
* ``python3 tools/gen_balance.py`` (or ``--write``) → write ``docs/balance.md``.
* ``python3 tools/gen_balance.py --check`` → regenerate in memory, diff against
  the on-disk file, print a unified diff and exit 1 if stale, else exit 0.

Importing this module has NO side effects (all writes are behind functions and
the ``__main__`` guard).
"""

from __future__ import annotations

import difflib
import sys
from pathlib import Path

# Run from anywhere: put the repo root (this file's grandparent) on the path so
# the ``games.*`` imports resolve without needing ``cd`` to the repo root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# --- Shipped economy sources (reads only; stdlib + games.* imports) ---------
from games.dnd.core import models as dnd_models
from games.dnd.core.effects import EFFECTS
from games.dnd.data.scenes import WAYSTATION_ROAD
from games.exploration.quest import catalog as quest_catalog
from games.exploration.quest import leverage as quest_leverage
from games.exploration.quest.models import RewardTier
from games.exploration.survival import difficulty as survival_difficulty
from games.fishing.core import catch as fishing_catch
from games.fishing.core import species as fishing_species
from games.fishing.core import spots as fishing_spots
from games.mining.core import capacity as mining_capacity
from games.mining.core import encounters as mining_encounters
from games.mining.core import energy as mining_energy
from games.mining.core import items as mining_items
from games.mining.core import rewards as mining_rewards

# The generated page's target path (both --write and --check agree on it).
DOC_PATH = _REPO_ROOT / "docs" / "balance.md"

# The auto-generated page's Status badge — a token the bootstrap.py --strict
# badge gate accepts (docs/design/world-inventory-resource-contract.md uses the
# taxonomy; `reference` fits an auto-generated reference page).
STATUS_BADGE = "reference"


def _num(value: object) -> str:
    """Format a number stably: ints as-is, floats fixed-precision, zeros stripped."""
    if isinstance(value, bool):  # guard: bool is an int subclass
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        text = f"{value:.4f}"
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text
    return str(value)


def _table(header: tuple[str, ...], rows: list[tuple[str, ...]]) -> list[str]:
    """Render a GitHub-flavoured markdown table (caller pre-sorts rows)."""
    lines = ["| " + " | ".join(header) + " |"]
    lines.append("| " + " | ".join("---" for _ in header) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def _read_floor(path: Path) -> str:
    """Read a suite's EXPECTED_MIN_TESTS.txt floor as text (stripped)."""
    return path.read_text(encoding="utf-8").strip()


def render() -> str:
    """Return the full ``docs/balance.md`` text (deterministic, no side effects)."""
    out: list[str] = []

    # --- 1. Header -----------------------------------------------------------
    out.append("# World Games — Economy Balance (auto-generated)")
    out.append("")
    out.append(f"> **Status:** `{STATUS_BADGE}`")
    out.append("")
    out.append(
        "Do NOT edit by hand — regenerate with `python3 tools/gen_balance.py`; "
        "CI enforces freshness (`--check`)."
    )
    out.append("")
    out.append(
        "Every number below is READ from the shipped code (the source `module.py` "
        "is noted per section); this page only formats constants, it never owns them."
    )
    out.append("")

    # --- 2. Global reward ceiling -------------------------------------------
    gm = quest_catalog.GLOBAL_MAX
    out.append("## Global reward ceiling")
    out.append("")
    out.append("_Source: `games/exploration/quest/catalog.py` (`GLOBAL_MAX`)._")
    out.append("")
    out.append(
        "The absolute per-grant ceiling. It binds the quest engine and the DND "
        "bounded-menu effects (every grant is `<= GLOBAL_MAX` component-wise); it "
        "does NOT bind the mining / fishing item faucets (those are throttled by "
        "energy, below)."
    )
    out.append("")
    out += _table(
        ("component", "value"),
        [
            ("global_xp", _num(gm.global_xp)),
            ("game_xp", _num(gm.game_xp)),
            ("currency", _num(gm.currency)),
        ],
    )
    out.append("")

    # --- 3. Action-rate ceilings (emission throttle) -------------------------
    out.append("## Action-rate ceilings (emission throttle)")
    out.append("")
    out.append(
        "_Sources: `games/mining/core/energy.py`, "
        "`games/exploration/survival/difficulty.py`, `games/fishing/core/catch.py`._"
    )
    out.append("")
    out.append(
        "Energy is the frequency brake the owner chose instead of a per-action "
        "cooldown: each dig/cast spends energy that refills at a fixed passive rate, "
        "so sustained emission per active hour is capped by the regen, not a timer."
    )
    out.append("")
    out.append(
        f"Mining base bar: `MAX_ENERGY` = {_num(mining_energy.MAX_ENERGY)}, "
        f"`DIG_COST` = {_num(mining_energy.DIG_COST)}, "
        f"`REGEN_SECONDS` = {_num(mining_energy.REGEN_SECONDS)} "
        f"→ sustained digs/hr = 3600 // REGEN_SECONDS = "
        f"{3600 // mining_energy.REGEN_SECONDS}."
    )
    out.append("")
    # Survival difficulty tiers — sorted by Difficulty name for stability.
    tunables = survival_difficulty.TUNABLES
    tier_rows: list[tuple[str, ...]] = []
    for diff in sorted(tunables, key=lambda d: d.name):
        t = tunables[diff]
        digs_hr = 3600 // t.regen_seconds
        casts_hr = digs_hr // fishing_catch.CAST_COST
        tier_rows.append(
            (
                diff.value,
                _num(t.max_energy),
                _num(t.regen_seconds),
                _num(t.cost),
                str(digs_hr),
                str(casts_hr),
            )
        )
    out.append(
        "Survival difficulty scales the shipped bar "
        "(`TUNABLES`; Easy is byte-identical to the mining bar). "
        f"Fishing casts/hr = digs/hr // `CAST_COST` "
        f"(`CAST_COST` = {_num(fishing_catch.CAST_COST)})."
    )
    out.append("")
    out += _table(
        (
            "difficulty",
            "max_energy",
            "regen_seconds",
            "cost",
            "sustained digs/hr",
            "sustained casts/hr",
        ),
        tier_rows,
    )
    out.append("")

    # --- 4. Mining -----------------------------------------------------------
    out.append("## Mining")
    out.append("")
    out.append(
        "_Sources: `games/mining/core/rewards.py`, `games/mining/core/encounters.py`, "
        "`games/mining/core/items.py`, `games/mining/core/capacity.py`._"
    )
    out.append("")

    out.append("### Loot roll (`rewards.py`)")
    out.append("")
    out.append(
        f"`BASE_ROLL_MAX` = {_num(mining_rewards.BASE_ROLL_MAX)} · "
        f"`TOOL_POWER_GAIN` = {_num(mining_rewards.TOOL_POWER_GAIN)} · "
        f"`LEGACY_PICKAXE_MULT` = {_num(mining_rewards.LEGACY_PICKAXE_MULT)}."
    )
    out.append("")
    out.append("Surface ore weights (`ORE_WEIGHTS`, depth 0):")
    out.append("")
    out += _table(
        ("ore", "weight"),
        [(ore, _num(w)) for ore, w in sorted(mining_rewards.ORE_WEIGHTS.items())],
    )
    out.append("")

    out.append("### Encounter tunables (`encounters.py`)")
    out.append("")
    enc_consts = [
        ("LOOT_CACHE_CHANCE", mining_encounters.LOOT_CACHE_CHANCE),
        ("RICH_VEIN_CHANCE", mining_encounters.RICH_VEIN_CHANCE),
        ("NORMAL_HAZARD_CHANCE", mining_encounters.NORMAL_HAZARD_CHANCE),
        ("HAZARD_MAX_CHANCE", mining_encounters.HAZARD_MAX_CHANCE),
        ("HAZARD_LOOT_MIN", mining_encounters.HAZARD_LOOT_MIN),
        ("HAZARD_LOOT_MAX", mining_encounters.HAZARD_LOOT_MAX),
        ("LOOT_CACHE_MIN", mining_encounters.LOOT_CACHE_MIN),
        ("LOOT_CACHE_MAX", mining_encounters.LOOT_CACHE_MAX),
        ("RICH_VEIN_MIN", mining_encounters.RICH_VEIN_MIN),
        ("RICH_VEIN_MAX", mining_encounters.RICH_VEIN_MAX),
        ("HAZARD_ENERGY_COST", mining_encounters.HAZARD_ENERGY_COST),
        ("FLEE_ENERGY_EXTRA", mining_encounters.FLEE_ENERGY_EXTRA),
        ("RICH_VEIN_ENERGY_COST", mining_encounters.RICH_VEIN_ENERGY_COST),
        ("BASE_PLAYER_DAMAGE", mining_encounters.BASE_PLAYER_DAMAGE),
        ("BASE_PLAYER_HP", mining_encounters.BASE_PLAYER_HP),
    ]
    out += _table(
        ("constant", "value"),
        [(name, _num(val)) for name, val in sorted(enc_consts)],
    )
    out.append("")

    out.append("### Per-unit ore coin value (`items.py`)")
    out.append("")
    ore_value_rows = []
    for ore in ("wood", "stone", "bronze", "iron", "silver", "gold", "diamond"):
        ore_value_rows.append((ore, _num(mining_items.item_value(ore))))
    ore_value_rows.sort()
    out += _table(("ore", "value"), ore_value_rows)
    out.append("")

    out.append("### Storage caps + vault coin sink (`capacity.py`)")
    out.append("")
    cap_consts = [
        ("PACK_SOFT_CAP", mining_capacity.PACK_SOFT_CAP),
        ("BASE_VAULT_CAP", mining_capacity.BASE_VAULT_CAP),
        ("VAULT_SLOTS_PER_LEVEL", mining_capacity.VAULT_SLOTS_PER_LEVEL),
        ("MAX_VAULT_LEVEL", mining_capacity.MAX_VAULT_LEVEL),
        ("_VAULT_UPGRADE_BASE_COST", mining_capacity._VAULT_UPGRADE_BASE_COST),
        ("_VAULT_UPGRADE_COST_STEP", mining_capacity._VAULT_UPGRADE_COST_STEP),
    ]
    out += _table(
        ("constant", "value"),
        [(name, _num(val)) for name, val in sorted(cap_consts)],
    )
    out.append("")

    # --- 5. Fishing ----------------------------------------------------------
    out.append("## Fishing")
    out.append("")
    out.append(
        "_Sources: `games/fishing/core/catch.py`, `games/fishing/core/species.py`, "
        "`games/fishing/core/spots.py`._"
    )
    out.append("")

    out.append("### Catch resolver (`catch.py`)")
    out.append("")
    catch_consts = [
        ("CAST_COST", fishing_catch.CAST_COST),
        ("BASE_BITE_CHANCE", fishing_catch.BASE_BITE_CHANCE),
        ("MAX_BITE_CHANCE", fishing_catch.MAX_BITE_CHANCE),
        ("MIN_BITE_CHANCE", fishing_catch.MIN_BITE_CHANCE),
        ("BITE_LUCK_PER_POINT", fishing_catch.BITE_LUCK_PER_POINT),
        ("MAX_FISHING_POWER", fishing_catch.MAX_FISHING_POWER),
        ("MAX_BITE_LUCK", fishing_catch.MAX_BITE_LUCK),
    ]
    out += _table(
        ("constant", "value"),
        [(name, _num(val)) for name, val in sorted(catch_consts)],
    )
    out.append("")

    out.append("### Species (`species.py`)")
    out.append("")
    species_rows = []
    for s in fishing_species.all_species():
        species_rows.append(
            (s.species_id, _num(s.size_rank), _num(s.rarity_weight))
        )
    species_rows.sort()
    out += _table(("species_id", "size_rank", "rarity_weight"), species_rows)
    out.append("")

    out.append("### Spot bite biases (`spots.py`)")
    out.append("")
    spot_rows = [
        (s.spot_id, _num(s.bite_bias)) for s in fishing_spots.all_spots()
    ]
    spot_rows.sort()
    out += _table(("spot_id", "bite_bias"), spot_rows)
    out.append("")

    # --- 6. DND --------------------------------------------------------------
    out.append("## DND")
    out.append("")
    out.append(
        "_Sources: `games/dnd/core/effects.py`, `games/dnd/data/scenes.py`, "
        "`games/dnd/core/models.py`._"
    )
    out.append("")
    tier_i = quest_catalog.TIER_CAPS[RewardTier.I]
    out.append(
        "The AI DM only picks a pre-priced option id; it never sizes an outcome. "
        f"The `escort_step` effect mints the tier-I quest bundle "
        f"(global_xp {_num(tier_i.global_xp)} / game_xp {_num(tier_i.game_xp)} / "
        f"currency {_num(tier_i.currency)}); the other skeleton effects mint nothing."
    )
    out.append("")
    # Effect -> mints? Derived from the escort_step tier-I fact; narrate-only
    # effects (rest_noop / scout_narrate) mint nothing.
    minting = {"escort_step"}
    effect_rows = []
    for eid in sorted(EFFECTS):
        if eid in minting:
            mints = (
                f"tier-I bundle ({_num(tier_i.global_xp)}/"
                f"{_num(tier_i.game_xp)}/{_num(tier_i.currency)})"
            )
        else:
            mints = "nothing (narrate-only)"
        effect_rows.append((eid, mints))
    out += _table(("effect_id", "mints"), effect_rows)
    out.append("")
    out.append(
        f"`MAX_MENU_SIZE` = {_num(dnd_models.MAX_MENU_SIZE)} "
        f"(the walking-skeleton scene `{WAYSTATION_ROAD.scene_id}` offers "
        f"{len(WAYSTATION_ROAD.options)} options). Every option is `<= GLOBAL_MAX` "
        "(bounded-menu posture)."
    )
    out.append("")

    # --- 7. Exploration quests ----------------------------------------------
    out.append("## Exploration quests")
    out.append("")
    out.append(
        "_Sources: `games/exploration/quest/catalog.py`, "
        "`games/exploration/quest/leverage.py`._"
    )
    out.append("")
    out.append("Per-tier reward bundles (`TIER_CAPS`), each `<= GLOBAL_MAX`:")
    out.append("")
    tier_cap_rows = []
    for tier in sorted(quest_catalog.TIER_CAPS, key=lambda t: t.name):
        b = quest_catalog.TIER_CAPS[tier]
        tier_cap_rows.append(
            (tier.name, _num(b.global_xp), _num(b.game_xp), _num(b.currency))
        )
    out += _table(
        ("tier", "global_xp", "game_xp", "currency"), tier_cap_rows
    )
    out.append("")
    out.append(
        f"Menu-width leverage (`leverage.py`): `BASE_MENU_WIDTH` = "
        f"{_num(quest_leverage.BASE_MENU_WIDTH)}, `MAX_MENU_WIDTH` = "
        f"{_num(quest_leverage.MAX_MENU_WIDTH)}, `XP_PER_EXTRA_OPTION` = "
        f"{_num(quest_leverage.XP_PER_EXTRA_OPTION)}."
    )
    out.append("")

    # --- 8. Test suite floors ------------------------------------------------
    out.append("## Test suite floors")
    out.append("")
    out.append(
        "_Sources: `tests/EXPECTED_SUITES.txt` + each suite's "
        "`EXPECTED_MIN_TESTS.txt`._"
    )
    out.append("")
    out.append(
        "The per-suite pytest count floors the CI coverage ratchet enforces "
        "(ORDER-001)."
    )
    out.append("")
    suites_file = _REPO_ROOT / "tests" / "EXPECTED_SUITES.txt"
    suite_dirs: list[str] = []
    for line in suites_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            suite_dirs.append(stripped)
    floor_rows = []
    for suite in sorted(suite_dirs):
        floor_path = _REPO_ROOT / suite / "EXPECTED_MIN_TESTS.txt"
        floor_rows.append((f"`{suite}`", _read_floor(floor_path)))
    out += _table(("suite", "min tests"), floor_rows)
    out.append("")

    # --- 9. Footer -----------------------------------------------------------
    out.append("## Notes")
    out.append("")
    out.append(
        "Per-hour currency/xp for DND and exploration is host-gated (there is no "
        "in-domain cooldown, so the host decides how often a scene/quest can be "
        "run). Cross-domain per-hour emission enumeration lives in the economy sim; "
        "folding those derived numbers into this page is a follow-up once that sim "
        "lands on main."
    )
    out.append("")

    return "\n".join(out) + "\n"


def write(path: Path = DOC_PATH) -> None:
    """Write the rendered page to *path* (the only file this module mutates)."""
    path.write_text(render(), encoding="utf-8")


def check(path: Path = DOC_PATH) -> int:
    """Compare rendered output to *path*; print a diff and return 1 if stale."""
    fresh = render()
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if fresh == current:
        return 0
    diff = difflib.unified_diff(
        current.splitlines(keepends=True),
        fresh.splitlines(keepends=True),
        fromfile=f"{path} (committed)",
        tofile=f"{path} (regenerated)",
    )
    sys.stdout.writelines(diff)
    sys.stdout.write(
        f"\nERROR: {path.relative_to(_REPO_ROOT)} is stale — "
        f"regenerate with `python3 tools/gen_balance.py`.\n"
    )
    return 1


def main(argv: list[str]) -> int:
    """CLI entry point: no args / --write writes; --check diffs and gates."""
    args = argv[1:]
    if args and args[0] == "--check":
        return check()
    if not args or args[0] == "--write":
        write()
        print(f"wrote {DOC_PATH.relative_to(_REPO_ROOT)}")
        return 0
    sys.stderr.write(f"usage: {argv[0]} [--write | --check]\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
