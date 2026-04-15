# Write Library Instructions

## Planning Guidelines

* Define the library's public API before writing code. List the functions and classes that
  downstream tasks will import, with their signatures and return types.
* Check existing library assets (run the library aggregator) to avoid duplicating functionality
  already provided by a completed task.
* Review the library asset specification in `meta/asset_types/library/specification.md` for the
  required folder structure and `details.json` schema.
* Identify which downstream tasks will consume this library. Design the API to serve their needs
  without coupling to any single task's data format.
* Plan the test strategy: which functions need unit tests, what test data is required, and where
  test files will live.

## Implementation Guidelines

* Place all library code in the task's `code/` directory. Use absolute imports from the repository
  root (e.g., `from tasks.t0012_build_wsd_data_loader.code.loader import load`).
* Never use relative imports or `sys.path` manipulation. The task folder name is a valid Python
  identifier by design.
* Follow `arf/styleguide/python_styleguide.md` for all Python code. Key rules: absolute imports,
  keyword arguments for 2+ params, `@dataclass(frozen=True, slots=True)`, centralized paths in
  `code/paths.py`, named constants, explicit type annotations, 100-char line limit.
* Write focused modules with single responsibilities. A loader module loads data; a scorer module
  computes metrics. Do not combine unrelated functionality.
* Keep the library generic. Do not hardcode paths, task IDs, or dataset-specific constants into
  shared modules. Accept these as parameters.
* Create the library asset folder at `assets/library/<library_id>/` with `details.json` containing
  `module_paths` pointing to the code files downstream tasks should import. Set `description_path`
  in `details.json` to the canonical documentation file path.
* Write tests in `code/test_*.py` files within the task folder. Tests must be runnable with
  `uv run pytest <test_path> -v`.
* Run `uv run ruff check --fix . && uv run ruff format . && uv run mypy .` before every commit.
  Library code must pass all checks cleanly.

### Library Documentation

Read `meta/asset_types/library/specification.md` for the required description-document format. The
canonical document path comes from `details.json` `description_path`. The documentation is what
makes the library usable. A library without clear documentation will be ignored or misused by
downstream tasks. Follow these rules:

**Source code documentation (follow `arf/styleguide/python_styleguide.md`):**

* Do NOT add docstrings when the name and type hints make the purpose obvious. The style guide
  explicitly says to avoid unnecessary docstrings — they add noise and maintenance burden. A
  function `def load_raganato_xml(*, path: Path) -> WsdDataset` needs no docstring.
* Add docstrings only for non-obvious behavior: surprising side effects, complex algorithms, or
  functions where the name + types are insufficient to understand usage.
* All dataclasses: use descriptive field names and type hints. No class docstrings unless the
  semantics are genuinely unclear from the field names.

**Description document — the consumer's primary reference:**

* **Overview**: Explain what problem the library solves and why it exists. A developer should
  understand whether this library is relevant to their task after reading the overview alone.
* **API Reference**: List every public function with its full signature, parameter descriptions,
  return type, and behavior. Group by module. Use code blocks for signatures. This section must be
  detailed enough that a consumer never needs to read source code to use the library correctly.
* **Usage Examples**: Include at least two concrete, runnable examples: (1) the simplest possible
  usage (import + one call), and (2) a realistic workflow showing how a downstream task would use
  the library with actual data. Use real class/function names and realistic (not `foo`/`bar`)
  variable names.
* **Data formats**: Document all input and output data structures. For each dataclass returned by
  the library, list its fields, types, and what each field means. For example, if
  `load_raganato_xml()` returns a `WsdDataset`, document what `WsdDataset`, `WsdDocument`,
  `WsdSentence`, `WsdInstance`, and `WsdToken` contain.
* **Dependencies**: List third-party packages and explain why each is needed. Also list which
  internal project libraries this library depends on, with their absolute import paths.
* **Testing**: Include the exact command to run tests and describe what the tests cover. Mention
  edge cases tested.
* **Limitations and assumptions**: State what the library does NOT handle (e.g., "Only supports
  WordNet 3.0 sense keys", "Does not handle multi-word expressions").

**details.json `entry_points`:**

* List every public function and class that consumers should import. Each entry point needs the full
  import path and a one-line description. Missing entry points mean consumers won't discover the
  functionality.

## Common Pitfalls

* **Relative imports**: Using `from .loader import X` breaks when other tasks try to import the
  module. Always use absolute imports from the repository root.
* **No tests**: Untested library code breaks silently when downstream tasks use it in unexpected
  ways. Write at least one test per public function.
* **Not running the library verificator**: Run the verificator after creating the asset to catch
  missing fields, broken `module_paths`, or import errors.
* **Coupling to specific task data**: Hardcoding file paths or dataset-specific column names into a
  shared library forces every consumer to match that exact data layout. Accept paths and names as
  parameters.
* **Missing type annotations**: Library code is consumed by other tasks that rely on mypy for
  correctness. Every public function must have complete type annotations for parameters and return
  values.
* **Skeleton documentation**: Writing a description document that just restates function signatures
  without explaining behavior, edge cases, or data formats. The API Reference must explain *what
  happens* when you call each function, not just its signature.
* **No usage examples or toy examples**: Examples using `foo`/`bar` or empty data are useless. Show
  realistic usage with actual project data paths and real dataclass instances.
* **Undocumented data structures**: Returning a dataclass without documenting what each field
  contains forces consumers to read source code — defeating the purpose of documentation.

## Verification Additions

* Confirm all files listed in `module_paths` exist and are importable with
  `uv run python -c "import <module_path>"`.
* Confirm `details.json` matches the library asset specification.
* Confirm all tests pass: `uv run pytest <task_folder>/tests/`.
* Confirm `ruff check`, `ruff format`, and `mypy` report no errors on the library code.
* Confirm no relative imports or `sys.path` hacks exist in library modules.
* Confirm the canonical description document API Reference documents every public function listed in
  `details.json` `entry_points`.
* Confirm the canonical description document Usage Examples contain at least two runnable code
  blocks with realistic data.
* Confirm every public dataclass has its fields documented in the canonical description document.

## Related Skills

* `/implementation` — for writing the library code and tests
* `/research-code` — for reviewing existing code assets before design
