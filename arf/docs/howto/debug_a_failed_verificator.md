# How to Debug a Failed Verificator

## Goal

Diagnose and fix a verificator failure so the task or asset conforms to its specification.

## Prerequisites

* The verificator command and its full output
* Write access to the offending file (it must not be inside a completed task folder)
* Read `arf/docs/reference/verificators.md` and `arf/docs/reference/specifications.md`

## Steps

1. Read the diagnostic code at the start of each error line (e.g. `PA-E009`, `TS-E003`).
2. Look up the prefix in `arf/docs/reference/verificators.md` to find the verificator and spec.
3. Identify the offending file from the diagnostic message — verificators always print the path.
4. Open the spec via `arf/docs/reference/specifications.md` and locate the rule for the code.
5. Compare the file to the spec section by section. Common failures:
   * YAML frontmatter parse errors — check indentation and quoting
   * Missing mandatory sections — compare heading list against the spec
   * Wrong slugs — slugs are case-sensitive and must match folder names
   * Missing files in `files/` subdirectories
   * `spec_version` missing or outdated
6. Fix the file in place.
7. Re-run the exact command from step 1.
8. Address remaining warnings before considering the fix complete.

## Verification

```bash
uv run python -m arf.scripts.verificators.<verificator_name>
```

Expected: zero errors.

## Pitfalls

* Editing a file inside a completed task folder — use the correction mechanism (see
  `apply_a_correction.md`)
* Ignoring warnings without understanding them
* Renaming a field without reading the spec, leading to repeat failures
* Running the wrong verificator — match the prefix to the script
* Assuming a stale cache — verificators read fresh

## See Also

* `../reference/verificators.md`
* `../reference/specifications.md`
* `apply_a_correction.md`
