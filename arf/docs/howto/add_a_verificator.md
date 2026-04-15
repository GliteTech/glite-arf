# How to Add a Verificator

## Goal

Create a new verificator that checks structural rules and reports diagnostics without raising.

## Prerequisites

* A clear rule set, usually from a specification
* Read
  [`arf/scripts/verificators/verify_paper_asset.py`](../../scripts/verificators/verify_paper_asset.py)
  as a reference
* A unique 2-3 letter diagnostic prefix (e.g. `PA`, `TK`, `RS`)

## Steps

1. Copy the reference:
   `cp arf/scripts/verificators/verify_paper_asset.py arf/scripts/verificators/verify_<name>.py`.
2. Define error codes `<PREFIX>-E001`, `<PREFIX>-E002`... and warnings `<PREFIX>-W001`... as
   module-level constants.
3. Collect diagnostics in a list and return a `VerificationResult` dataclass. Never raise on rule
   violations — only on programming errors.
4. Run every check independently. Do not short-circuit on the first failure.
5. Wire up `argparse`, taking the target as positional arguments. Use keyword arguments for 2+
   parameters.
6. Print diagnostics in the format used by `verify_paper_asset.py`. Exit `1` on any error, `0`
   otherwise.
7. If the verificator runs during a task step, hook it into
   [`arf/scripts/verificators/verify_step.py`](../../scripts/verificators/verify_step.py).
8. Add every code to the spec's "Verification Rules" section.
9. Document it in `arf/docs/reference/verificators.md`.
10. Run `uv run ruff check --fix . && uv run ruff format . && uv run mypy .`.

## Verification

```bash
uv run python -m arf.scripts.verificators.verify_<name> <target>
```

Expected: exit `0` with no output on a good fixture; exit `1` with a full diagnostic list on a bad
one.

## Pitfalls

* Raising on rule violations instead of appending diagnostics
* Short-circuiting after the first error
* Forgetting to update the spec's verification-rules table
* Prefix collides with an existing verificator
* Checks depend on network state — verificators must be deterministic

## See Also

* `../reference/verificators.md`
* `../explanation/verification_model.md`
