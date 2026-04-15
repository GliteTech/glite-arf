---
paths:
  - "**/*.py"
---

# Python Style (Critical Rules)

Full guide: `arf/styleguide/python_styleguide.md`

* Python 3.12+ syntax (`list[int]` not `List[int]`, `X | None` not `Optional[X]`)
* Line length: 100 characters
* Absolute imports only, never relative
* Keyword arguments for 2+ heterogeneous parameters
* `@dataclass(frozen=True, slots=True)` for all structured data; never return tuples
* Centralize all file paths as `Path` constants in `paths.py`
* Named constants for all magic strings; no hardcoded values
* Strict mypy with explicit type annotations everywhere
* Explicit checks: `if x is None:` not `if not x:`, `if len(lst) == 0:` not `if not lst:`
* `pathlib.Path` always, never `os.path`
* `tqdm` for progress bars, `argparse` for CLI arguments
* `@property` only for trivial field access, never for computation or IO
