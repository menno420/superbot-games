"""Mining structure recipes — in-code defaults + a pure normalisation seam.

Ported from the oracle ``utils/mining/recipes.py``. FILESYSTEM IO SEVERED for the
pure core: the oracle read ``disbot/data/json/recipes.json`` off disk and fell back
to :data:`DEFAULT_RECIPES`. The pure mining core does **no** file IO, so
:func:`load_recipes` now returns the in-code defaults directly, and an optional
``overrides`` argument is the documented injection point a host uses to feed
JSON-loaded (or DB-loaded) recipe data in. The normalisation rules are preserved
verbatim, so an injected payload is cleaned exactly as the oracle's loader did.

See docs/design/mining-plugin-layout.md § "Severed couplings / purity".
"""

from __future__ import annotations

from collections.abc import Mapping

DEFAULT_RECIPES: dict[str, dict[str, int]] = {
    "stone hut": {"stone": 5},
    "iron pickaxe": {"iron": 3, "wood": 2},  # keep in lockstep with recipes.json
    "gold statue": {"gold": 4},
    "diamond throne": {"diamond": 6},
    "wooden house": {"wood": 8},
    # Starter gear — craftable from mineable resources so broken gear
    # (the durability sink) is always re-craftable, not buy-only.
    "pickaxe": {"wood": 2, "stone": 3},
    "torch": {"wood": 2},
    "lantern": {"iron": 2, "gold": 1},
}


def normalise_recipes(data: object) -> dict[str, dict[str, int]]:
    """Clean an untrusted recipe payload to the canonical shape (pure).

    Normalisations (verbatim from the oracle loader):
      * recipe names lower-cased
      * material names lower-cased
      * non-dict entries skipped
      * non-int quantities skipped

    Returns ``{}`` for anything that is not a dict of dicts, so the caller can
    decide whether to fall back to :data:`DEFAULT_RECIPES`.
    """
    if not isinstance(data, Mapping):
        return {}
    normalised: dict[str, dict[str, int]] = {}
    for recipe_name, requirements in data.items():
        if not isinstance(requirements, Mapping):
            continue
        recipe_lower = str(recipe_name).lower()
        normalised_req: dict[str, int] = {}
        for mat, qty in requirements.items():
            if isinstance(mat, str) and isinstance(qty, int):
                normalised_req[mat.lower()] = qty
        if normalised_req:
            normalised[recipe_lower] = normalised_req
    return normalised


def load_recipes(overrides: object = None) -> dict[str, dict[str, int]]:
    """Return the recipe table — the in-code defaults, or *overrides* if given.

    Pure: no filesystem IO (the oracle's ``open(RECIPES_FILE)`` is severed). Pass
    *overrides* (a JSON- or DB-loaded ``{recipe: {material: qty}}`` payload) to
    inject host data; it is normalised through :func:`normalise_recipes` exactly
    as the oracle loader cleaned the on-disk file, and an empty/invalid payload
    falls back to :data:`DEFAULT_RECIPES` — the same safe-default behaviour.
    """
    if overrides is None:
        return dict(DEFAULT_RECIPES)
    normalised = normalise_recipes(overrides)
    return normalised if normalised else dict(DEFAULT_RECIPES)


__all__ = ["DEFAULT_RECIPES", "normalise_recipes", "load_recipes"]
