# 2026-07-14 · night build — fix: gen_balance --check handles out-of-repo paths in its stale message

> **Status:** in-progress
>
> 📊 Model: Fable · 2026-07-14T02:56:04Z · night-fix-gen-balance-relpath

Build slice fixing the quirk pinned by #121 (`fefe16c`,
`tests/tools/test_gen_balance.py::test_check_stale_path_outside_repo_raises`):
`gen_balance.check()` on a stale path OUTSIDE the repo root raises
`ValueError` from `path.relative_to(_REPO_ROOT)` while constructing the
error message (tools/gen_balance.py:493) instead of returning 1. Plan:
minimal fallback to the absolute path when `relative_to` fails, and
flip the #121 pin from `pytest.raises(ValueError)` to asserting exit 1
with the absolute path in the message.
