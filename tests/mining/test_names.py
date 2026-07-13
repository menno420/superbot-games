"""names: pin the fuzzy item-name resolver's documented contract.

``resolve_item_name`` promises a strict resolution order — exact
(normalized) → alias map → ``difflib`` closest match at *cutoff* — and that
it "only ever returns a member of *candidates*, so a caller can trust the
result as a canonical name".  Before this suite the whole resolver (and
``_normalize``) sat at 0% — any of those promises could have rotted
silently.  Every test runs at EXISTING constants; nothing is reconfigured.
"""

from __future__ import annotations

from games.mining.core import items
from games.mining.core import names


def test_exact_match_normalizes_and_returns_the_candidate_spelling() -> None:
    """Whitespace/underscore/case noise resolves exactly, and the result is
    the *candidate's* original spelling (the pool maps lowercased → original),
    never the user's raw text."""
    assert (
        names.resolve_item_name("  Iron_Pickaxe ", ["Iron Pickaxe", "pickaxe"])
        == "Iron Pickaxe"
    )


def test_empty_candidates_returns_none() -> None:
    """The empty-pool guard: no candidates means nothing to resolve — even a
    query that is a known alias returns None."""
    assert names.resolve_item_name("pickaxe", []) is None
    assert names.resolve_item_name("tnt", []) is None


def test_alias_resolves_only_when_its_target_is_a_candidate() -> None:
    """"tnt" → "dynamite" via ALIASES when dynamite is on offer; the same
    alias against a pool without its target falls through (and difflib finds
    nothing close), so the muscle-memory name never escapes the candidate set."""
    assert names.resolve_item_name("tnt", ["dynamite", "pickaxe"]) == "dynamite"
    assert names.resolve_item_name("tnt", ["pickaxe"]) is None


def test_fuzzy_typo_resolves_at_the_default_cutoff() -> None:
    """A one-letter typo lands on the closest candidate via difflib."""
    assert names.resolve_item_name("picaxe", ["pickaxe", "iron pickaxe"]) == "pickaxe"


def test_cutoff_is_respected() -> None:
    """cutoff=1.0 demands an exact ratio — the near-miss that resolves at the
    default 0.7 is rejected; garbage never resolves at the default either."""
    assert names.resolve_item_name("iron pickax", ["iron pickaxe"]) == "iron pickaxe"
    assert names.resolve_item_name("iron pickax", ["iron pickaxe"], cutoff=1.0) is None
    assert names.resolve_item_name("zzz", ["pickaxe"]) is None


def test_caller_supplied_aliases_replace_the_default_map() -> None:
    """A custom aliases mapping is consulted *instead of* ALIASES (the
    signature is replace, not merge): the custom entry resolves, and a
    default-map entry like "tnt" no longer does."""
    assert names.resolve_item_name("foo", ["bar"], aliases={"foo": "bar"}) == "bar"
    assert (
        names.resolve_item_name("tnt", ["dynamite"], aliases={"foo": "bar"}) is None
    )


def test_every_alias_target_is_a_canonical_catalog_name() -> None:
    """ALIASES values "must be canonical catalog names" (module comment) —
    an alias pointing at a renamed/removed item would silently dead-end, so
    each target must exist in the item catalog."""
    catalog = set(items.catalog_names())
    missing = {k: v for k, v in names.ALIASES.items() if v not in catalog}
    assert not missing, missing
