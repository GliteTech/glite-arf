# Infrastructure Setup Instructions

## Planning Guidelines

* Identify exactly what downstream tasks need from this setup and confirm those requirements before
  starting.
* Check whether the dependency or tool is already installed or configured by reviewing prior task
  results and the current environment.
* Plan for idempotency: the setup should succeed whether run for the first time or repeated on an
  already-configured environment.

## Implementation Guidelines

* Follow `arf/styleguide/python_styleguide.md` for all Python code. Key rules: absolute imports,
  keyword arguments for 2+ params, `@dataclass(frozen=True, slots=True)`, centralized paths in
  `code/paths.py`, named constants, explicit type annotations, 100-char line limit.
* **Idempotency**: Write setup scripts that can be re-run safely. Check whether a dependency exists
  before installing it. Use version pins for all installed packages.
* **Verification**: After every installation or configuration step, run a concrete test that proves
  the setup works. For example, after installing NLTK WordNet data, write a script that loads a
  synset and prints it.
* **Documentation**: Record exactly what was installed, which versions, and how to reproduce the
  setup. Include this in `results/results_summary.md`.
* **Dependency tracking**: If the setup adds Python packages, update `pyproject.toml` and run
  `uv sync`. If it adds system-level tools, document the installation command.
* **Cleanup**: If the setup creates temporary files or downloads large artifacts, clean them up or
  document where they live and how to remove them.
* Use `uv run python -m arf.scripts.utils.run_with_logs` for all script executions so the full
  installation output is captured in logs.

## Common Pitfalls

* **Non-idempotent scripts**: A setup script that fails on second run is fragile. Always check state
  before modifying it.
* **Missing version pins**: Installing packages without version pins leads to unreproducible
  environments. Pin every dependency.
* **No verification step**: "It installed without errors" is not sufficient. Run a functional test
  that exercises the installed tool or library.
* **Undocumented side effects**: If the setup modifies global state (env variables, system packages,
  config files), document every change.
* **Large downloads without caching**: If the setup downloads large files, check for existing copies
  first and document the expected file sizes.

## Verification Additions

* Confirm the setup script runs successfully when executed a second time (idempotency check).
* Confirm a functional test exists that exercises the installed tool or library and passes.
* Confirm `results/results_summary.md` documents what was installed, which versions, and how to
  reproduce.
* Confirm any new Python dependencies are added to `pyproject.toml`.

## Related Skills

* `/implementation` — execute setup scripts with logging
* `/setup-remote-machine` — provision and configure remote machines
