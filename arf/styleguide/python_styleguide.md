# Style Guide

This document consolidates all style requirements for the project, covering general Python
conventions and data-handling patterns.

## Quick Reference

### Frequently Ignored Rules

These rules are well-established but often overlooked:

1. **Use dataclasses instead of tuples** - Never use `tuple[int, Path, str]`, always use dataclasses
2. **Use keyword arguments** - Functions with 2+ heterogeneous params require keyword arguments
3. **Never return tuples** - Functions must return dataclasses, not tuples
4. **Centralize paths** - All file paths must be defined as constants (per-task or in a shared
   `paths.py`)
5. **Use constants for magic strings** - No hardcoded strings like `"test_id"`, `"country"`
6. **Use `None` for missing data** - Never use `0.0` or `""` when data is not available;
   `None`/`null` means "no measurement", `0.0` means "measured zero"

### Core Principles

* **Type Safety**: Use enums, dataclasses, and explicit types throughout
* **Constants Over Magic Values**: Extract all reused strings/values to typed constants
* **Separation of Concerns**: Keep validation, conversion, and business logic separate
* **Explicit Over Implicit**: Be explicit about types, conversions, and dtypes
* **Resource Safety**: Always clean up temporary files with try/finally

* * *

## General Coding Practices

### Use `@property` only for simple operations

Never put non-trivial computation or IO inside a `@property`.

#### Why:

It's impossible to distinguish an innocent field access from a heavy/IO `@property` access on the
call site, which becomes a problem in loops or tight timing scenarios.

#### Do:

```python
class MyClass:
    a: int

    @property
    def aplusone(self) -> int:
        return self.a + 1

    def get_db_data(self) -> Data:
        return fetch_b_from_db(self.a)
```

#### Don't:

```python
class MyClass:
    a: int

    @property
    def aplusone(self) -> int:
        return self.a + 1

    @property
    def db_data(self) -> Data:
        return fetch_b_from_db(self.a)
```

* * *

### Use explicit checks instead of relying on falsiness

Don't use the idiomatic falsiness of empty lists, zeroes, empty strings, and `None`s. Check them
explicitly.

#### Why:

This idiom is too error-prone, especially in presence of `T | None` types.

#### Do:

```python
if x is None:
    ...

if len(x) == 0:
    ...

if (x := get_x()) is not None:
    ...
```

#### Don't:

```python
# Assuming non-bool x
if x:
    ...

if x := get_x():
    ...
```

* * *

### Use `None` for missing data, never zero or empty string

When a metric, measurement, or result is **not available** (data doesn't exist, computation was
skipped, input missing), use `None` — never `0`, `0.0`, or `""`. Zero is a valid measurement; `None`
means "no measurement was taken."

#### Why:

Using `0.0` for "not available" is indistinguishable from an actual score of zero. Downstream
consumers (charts, aggregators, reports) will treat it as a real value — averaging it in, plotting
it, comparing it. This silently corrupts results.

#### Do:

```python
@dataclass(frozen=True, slots=True)
class SubsetResult:
    subset: str
    f1: float | None  # None when no predictions exist
    has_predictions: bool

# JSON output: {"f1": null} — clearly "not available"
```

#### Don't:

```python
@dataclass(frozen=True, slots=True)
class SubsetResult:
    subset: str
    f1: float  # 0.0 when no predictions — looks like a real score
    has_predictions: bool

# JSON output: {"f1": 0.0} — is this a real score or missing data?
```

* * *

### Put general, context-y parameters first when defining functions

A useful rule of thumb is "would it be convenient to use `partial()` on this function".

#### Why:

Consistency, extra semantic information, and convenience of `partial()`.

#### Do:

```python
def foo(
    context: Context,
    db: Database,
    ids_to_fetch: list[int],
) -> None:
    ...
```

#### Don't:

```python
def foo(
    ids_to_fetch: list[int],
    context: Context,
    db: Database,
) -> None:
    ...
```

* * *

### Write durations in fractional seconds (floats)

Store all durations as fractional seconds using floats.

#### Why:

Consistency. We don't normally need to be more precise than milliseconds, and milliseconds can be
perfectly expressed as fractional seconds.

#### Do:

```python
QUERY_TIMEOUT: float = 5.000  # seconds as a float
```

#### Don't:

```python
QUERY_TIMEOUT: int = 5000  # milliseconds not as a float
```

* * *

### Use "kind" instead of "type" in names

#### Why:

`type` clashes with built-in `type` too much.

#### Do:

```python
class UserKind(Enum):
    ...
```

#### Don't:

```python
class UserType(Enum):
    ...
```

* * *

## Type System

### Use dataclasses instead of tuples

**CRITICAL**: Never use complex tuple types for structured data or return values. Always use
dataclasses.

#### Why:

* Type safety and IDE support
* Self-documenting code
* Prevents position-based errors
* Required by project style guide

#### Do:

```python
@dataclass(frozen=True, slots=True)
class BatchMetadata:
    batch_id: int
    file_path: Path
    display_name: str

def process_batch() -> BatchMetadata:
    return BatchMetadata(
        batch_id=1,
        file_path=Path("data.csv"),
        display_name="Batch 1",
    )
```

#### Don't:

```python
def process_batch() -> tuple[int, Path, str]:
    return (1, Path("data.csv"), "Batch 1")
```

#### Exception: Named tuples for cache keys

Plain tuples are acceptable for cache keys, but use `NamedTuple` for type safety:

```python
from typing import NamedTuple

class CacheKey(NamedTuple):
    user_id: int
    language: str
    version: int

cache: dict[CacheKey, Result] = {}
cache[CacheKey(123, "en", 1)] = result
```

**Don't use plain tuples even for cache keys:**

```python
cache: dict[tuple[int, str, int], Result] = {}  # Hard to understand
cache[(123, "en", 1)] = result  # What does each position mean?
```

* * *

### Use enum objects internally, convert to strings only at boundaries

Store enum objects throughout internal logic. Only convert to strings at I/O boundaries (CSV export,
API responses).

#### Why:

* **Type safety**: Catches typos and invalid values at type-checking time
* **IDE support**: Better autocomplete and refactoring
* **Clear intent**: The type system documents valid values
* **Separation of concerns**: Internal logic stays clean, conversion happens once at boundaries

#### Do:

```python
@dataclass(frozen=True, slots=True)
class AnnotationRecord:
    label: LabelKind | None
    source: CorpusSource | None

def _annotation_record_to_dict(record: AnnotationRecord) -> dict[str, Any]:
    data: dict[str, Any] = asdict(obj=record)
    # Convert enums to strings at CSV export boundary
    for key in ENUM_FIELDS:
        if data[key] is not None and hasattr(data[key], "value"):
            data[key] = data[key].value
    return data
```

#### Don't:

```python
@dataclass(frozen=True, slots=True)
class AnnotationRecord:
    label: str | None  # Lost type safety
    source: str | None
```

* * *

### Use semantic type aliases for domain-specific strings

Use type aliases like `Word`, `ConceptID`, `BatchID` for domain-specific strings. Keep `str` for
truly generic strings.

#### Why:

* Self-documenting code
* Helps catch logical errors where different string types are mixed
* Makes function signatures clearer

#### Do:

```python
# Define semantic type aliases (Python 3.12+ syntax)
type InstanceID = str
type ItemID = str
type TaskID = str

# Add research-specific aliases as needed
type MetricName = str
type ModelLabel = str

def collect_item_ids(
    df_annotations: DataFrame,
    item_column: str,
) -> set[ItemID]:  # Clear: returns a set of item IDs
    ...
```

#### Don't:

```python
def collect_item_ids(
    df_annotations: DataFrame,
    item_column: str,
) -> set[str]:  # Unclear: str of what?
    ...
```

**Note**: Don't overuse. Keep `str` for truly generic strings (column names, messages, display
strings).

* * *

### Use `int | None` instead of `Optional[int]`

#### Why:

Consistency with modern Python typing conventions.

#### Do:

```python
def process(value: int | None) -> str | None:
    ...
```

#### Don't:

```python
from typing import Optional

def process(value: Optional[int]) -> Optional[str]:
    ...
```

* * *

### Use `int | float` in `isinstance`, not `(int, float)`

#### Why:

Consistency with PEP 604 union syntax. Enforced by ruff rule UP038.

#### Do:

```python
if isinstance(value, int | float):
    ...
```

#### Don't:

```python
if isinstance(value, (int, float)):
    ...
```

* * *

### Use exhaustive matches with `assert_never`

Use `assert_never` to make mypy scream when you forget to handle a branch or element of a type
union.

#### Why:

Types and code change over time. Exhaustive checking ensures that when unions are extended, mypy
will complain that not every case is covered.

#### Do:

```python
from typing import assert_never

X: TypeAlias = Foo | Bar

def f(x: X) -> None:
    if isinstance(x, Foo):
        ...
    elif isinstance(x, Bar):
        ...
    else:
        assert_never(x)
```

#### Don't:

```python
X: TypeAlias = Foo | Bar

def f(x: X) -> None:
    if isinstance(x, Foo):
        ...
    else:
        # If X becomes Foo | Bar | Baz, this will silently break
        ...
```

**Note**: You can also use `assert_never` for unreachable code, e.g. when you have early returns
that should always return a value first.

* * *

### Use `T_Whatever` format for meaningful type variables

When you need type variables that aren't just `T`, use the `T_Whatever` format.

#### Why:

Consistency across the codebase.

#### Do:

```python
T_User = TypeVar("T_User")
```

#### Don't:

* `UserT`
* `User`
* `UserType`

* * *

### Satisfy mypy and use explicit types as assertions

Prefer type inference but use explicit type annotations in three cases:

* Wherever types are required by mypy (function signatures, tricky inference)
* As assertions that the inferred type matches your intuition
* As documentation

#### Why:

Relying on type inference is concise, but sometimes the inferred type might not match intuition and
even mask an error.

#### Do:

```python
def myfun() -> int:
    a: int = foo()  # Assert that foo() returns int
    b = foo()       # Let it infer when safe
    return a + b
```

#### Don't:

```python
def myfun() -> int:
    a: int = 1  # Unnecessary, obviously int
    b: int = 2
    return a + b
```

* * *

### Use the type system to encode business logic constraints

Try to model business constraints in the type system, as long as it's practical.

#### Why:

The earlier we find mistakes, the less costly they are. Using the type system lets us find errors
even before writing tests.

#### Do:

```python
@dataclass(frozen=True, slots=True)
class AnonymousUser:
    id: int

@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    id: int
    name: str
    email: str

def process(user: AnonymousUser | AuthenticatedUser) -> None:
    ...
```

#### Don't:

```python
@dataclass(frozen=True, slots=True)
class User:
    id: int
    name: str | None
    email: str | None

def process(user: User) -> None:
    ...
```

* * *

### Use explicit types for variable declarations

Always provide explicit type hints for lists, dicts, and other collections, even when the values
make the type obvious.

#### Why:

* Serves as inline documentation
* Catches inference errors early
* Consistent with project style

#### Do:

```python
TEXT_COLUMNS: list[str] = [
    "token", "context", "description", "category",
]
ENUM_FIELDS: list[str] = [
    "category", "source", "model_kind",
]
```

#### Don't:

```python
TEXT_COLUMNS = ["token", "context", "description", "category"]
```

* * *

## Asserts

### Use `assert` for defensive coding and documentation

Whenever you assume something to be true, assert it explicitly with an `assert`.

#### Why:

`assert` serves two purposes:

* Surfacing broken assumptions early and explicitly
* Documenting the assumptions you're making

#### Do:

```python
def trim_nonempty_list(lst: list[T], n: int) -> list[T]:
    assert len(lst) > 0, "list is non-empty"
    assert 0 <= n <= len(lst), "n is within bounds"
    return lst[:n]
```

#### Don't:

```python
def trim_nonempty_list(lst: list[T], n: int) -> list[T]:
    return lst[:n]
```

* * *

### Assume that `assert`s are always run

We never run Python with the `-O` flag, so `assert` can be assumed to always run. Plan expensive
checks accordingly.

#### Why:

Many Python libraries use asserts to assert things that must always be true, including
safety-critical conditions. There is little performance benefit to disabling assertions. Being able
to assert things should be encouraged.

* * *

### Use positive assertion messages

Positive assertion messages make the intent clearer.

#### Why:

Clear communication about what is expected, not what went wrong.

#### Do:

```python
assert a.is_foobar(), "a is foobar"
assert isinstance(dog, Cat), "Expected type Cat, got Dog"
```

#### Don't:

* `assert a.is_foobar(), "Foobar error"`
* `assert a.is_foobar(), "a is not foobar"`

* * *

## Constants and Magic Strings

### Replace magic strings with named constants

**CRITICAL**: Never use hardcoded string literals for column names, field names, or comparison
values used in multiple places.

#### Why:

1. **Maintainability**: Update in only one place
2. **Type Safety**: Explicit type hints catch errors early
3. **Readability**: Self-documenting
4. **Refactoring**: IDE tools work better
5. **Consistency**: Prevents typos

#### Do:

```python
# In constants.py
STATUS_COMPLETED: str = "completed"
ITEM_ID_COLUMN: str = "item_id"
TOKEN_COLUMN: str = "token"
CATEGORY_COLUMN: str = "category"
CONTEXT_COLUMN: str = "context"
LABEL_COLUMN: str = "label"
ENUM_FIELDS: list[str] = [
    "category", "source", "model_kind",
]

# In usage
if task.status == STATUS_COMPLETED:
    ...

df[TOKEN_COLUMN]

for key in ENUM_FIELDS:
    ...
```

#### Don't:

```python
if task.status == "completed":
    ...

df["token"]

for key in ["category", "source", "model_kind"]:
    ...
```

* * *

### Centralize path constants in paths.py

**CRITICAL**: All file paths must be defined in `paths.py`. Keep business logic (like
`InputFilePath` construction) in the files where it's used.

#### Why:

1. **Single Source of Truth**: All paths in one place
2. **Easy Updates**: Change paths without touching business logic
3. **Clear Separation**: Constants vs. business logic are separate concerns
4. **Testability**: Easy to override paths in tests

#### Do:

```python
# paths.py
from pathlib import Path

DATA_DIR: Path = Path("data")
ANNOTATIONS_PATH: Path = DATA_DIR / "annotations.csv"
PREDICTIONS_PATH: Path = DATA_DIR / "predictions.csv"
CORPUS_PATH: Path = DATA_DIR / "corpus.jsonl"
RESULTS_DIR: Path = DATA_DIR / "results"
```

#### Don't:

```python
# Hardcoded paths scattered throughout files
df = pd.read_csv("data/annotations.csv")
```

* * *

## Function Calls and Parameters

### Use keyword arguments for functions with 2+ heterogeneous parameters

**CRITICAL**: When calling functions with two or more heterogeneous parameters, always use keyword
argument syntax.

#### Why:

* More resilient to refactorings and typos
* Easier to read
* Explicitly required by project style guide

#### Do:

```python
process_file(
    file_path=file_path,
    token_counter=token_counter,
    progress_bar=progress_bar,
)
```

#### Don't:

```python
process_file(file_path, token_counter, progress_bar)
```

**Exception**: Homogeneous parameters (all same type) don't require keyword arguments:

```python
combine_results(obj1, obj2, obj3)  # All same type, OK
```

* * *

### Use multi-line format for functions with 2+ parameters

When defining functions with more than two parameters, write each parameter on its own line with a
trailing comma.

#### Why:

* Better readability
* Easier diffs in version control
* Consistent formatting

#### Do:

```python
def process_file(
    file_path: Path,
    token_counter: Counter,
    progress_bar: tqdm,
) -> None:
    ...
```

#### Don't:

```python
def process_file(file_path: Path, token_counter: Counter, progress_bar: tqdm) -> None:
    ...
```

* * *

## Pydantic and Data Validation

### Use Pydantic BaseModel for JSON files with schemas you control

Use Pydantic `BaseModel` for reading and writing JSON files whose schema is defined by this project.
Do not use raw `json.loads()`/`json.dumps()` with manual dict validation for these files.

#### Why:

* **Validation**: Pydantic validates types and constraints automatically
* **Type safety**: IDE autocomplete and mypy work with model fields
* **Single source of truth**: The model definition *is* the schema
* **Error messages**: Clear, structured validation errors with field paths
* **Performance**: `model_validate_json()` parses and validates in one Rust-level pass

#### Do:

```python
from pathlib import Path
from pydantic import BaseModel

class TaskConfig(BaseModel):
    name: str
    threshold: float
    tags: list[str]

# Reading
config = TaskConfig.model_validate_json(
    Path("config.json").read_text(encoding="utf-8"),
)

# Writing
Path("config.json").write_text(
    config.model_dump_json(indent=2),
    encoding="utf-8",
)
```

#### Don't:

```python
import json

data = json.loads(Path("config.json").read_text())
# Manual validation scattered across the codebase
if not isinstance(data.get("name"), str):
    return None
```

#### Exceptions: when raw `json.loads` is correct

Use raw `json.loads()` in these cases:

* **Verificators** that must read potentially malformed files and report multiple individual
  diagnostics. Pydantic raises one `ValidationError` on the first problem; verificators need to
  check every field independently and report all violations at once.
* **External input** whose schema you do not control (e.g., JSON from `gh` CLI output, hook stdin
  from Claude Code). A Pydantic model would break when the external tool adds or changes fields,
  unless you use `extra="ignore"` which defeats the purpose.

```python
# Verificator: read raw, validate each field, report all problems
data: object = json.loads(raw)
if not isinstance(data, dict):
    diagnostics.append(error("top-level value is not a JSON object"))
    return diagnostics
if "name" not in data:
    diagnostics.append(error("required field 'name' is missing"))
if "status" not in data:
    diagnostics.append(error("required field 'status' is missing"))
# ... check all fields, report all problems

# External tool output: defensive .get() with fallbacks
prs: object = json.loads(gh_output)
if isinstance(prs, list) and len(prs) == 0:
    ...
```

* * *

### Use `model_validate_json()` instead of `model_validate(json.loads())`

Prefer `model_validate_json(raw_str)` over `model_validate(json.loads(raw_str))`.

#### Why:

`model_validate_json()` avoids constructing intermediate Python dicts, making it faster and more
memory-efficient.

#### Do:

```python
config = TaskConfig.model_validate_json(raw_json)
```

#### Don't:

```python
config = TaskConfig.model_validate(json.loads(raw_json))
```

* * *

### Pydantic at the edges, dataclasses inside

Use Pydantic `BaseModel` at I/O boundaries (JSON files, API responses, external data). Use stdlib
`@dataclass(frozen=True, slots=True)` for internal data passed between functions.

#### Why:

* Pydantic models are ~6-7x slower to instantiate than dataclasses
* Internal data is already validated — re-validating wastes cycles
* Dataclasses have zero external dependencies

#### Do:

```python
# Edge: reading from file
class PaperDetailsFile(BaseModel):
    paper_id: str
    title: str
    year: int

# Internal: passing between functions
@dataclass(frozen=True, slots=True)
class PaperInfoShort:
    paper_id: str
    title: str
    year: int
```

* * *

### Use `TypeAdapter` for validating lists and non-model types

When reading a JSON array or a non-model type, use `TypeAdapter`. **Always instantiate `TypeAdapter`
at module level** — instantiation builds a validator from scratch and is expensive.

#### Why:

`BaseModel.model_validate_json()` expects a JSON object at the top level. `TypeAdapter` handles any
type including `list[Model]`.

#### Do:

```python
from pydantic import TypeAdapter

# Module level — instantiate once
_TASK_LIST_ADAPTER: TypeAdapter[list[TaskConfig]] = TypeAdapter(
    list[TaskConfig],
)

def load_tasks(*, file_path: Path) -> list[TaskConfig]:
    return _TASK_LIST_ADAPTER.validate_json(
        file_path.read_bytes(),
    )
```

#### Don't:

```python
def load_tasks(*, file_path: Path) -> list[TaskConfig]:
    # Expensive: builds a new validator every call
    adapter = TypeAdapter(list[TaskConfig])
    return adapter.validate_json(file_path.read_bytes())
```

* * *

### Use `ConfigDict` for model configuration

Configure models using `model_config = ConfigDict(...)`. Prefer `frozen=True` for immutable models
and `extra="forbid"` to catch typos in JSON keys.

#### Do:

```python
from pydantic import BaseModel, ConfigDict

class PaperDetails(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    paper_id: str
    title: str
    year: int
```

* * *

### Keep Pydantic models as pure data structures

Keep Pydantic models as simple data containers. Put conversion/transformation logic in separate
standalone functions.

#### Why:

* **Separation of concerns**: Pydantic handles validation, conversion lives elsewhere
* **Testability**: Standalone functions easier to test
* **Reusability**: Conversion functions work without instantiating models
* **Clarity**: Distinction between "what the data is" vs "what we do with it"

#### Do:

```python
class AnnotationInput(BaseModel):
    pos_tag: str | None = None
    source_corpus: str | None = None

def _parse_pos(value: str | None) -> PartOfSpeech | None:
    if value is None or value == "":
        return None
    if result := try_to_enum(enum_cls=PartOfSpeech, value=value):
        return result
    return POS_ALIAS_MAP.get(value)

# Usage
parsed = _ParsedAnnotation(
    pos=_parse_pos(annotation.pos_tag),
)
```

#### Don't:

```python
class AnnotationInput(BaseModel):
    pos_tag: str | None = None

    def get_pos(self) -> PartOfSpeech | None:
        # Conversion logic mixed with data model
        ...

# Usage
parsed = _ParsedAnnotation(
    pos=annotation.get_pos(),
)
```

* * *

### Use Pydantic v2 API, never v1

Always use the v2 methods. The v1 API is deprecated.

| v1 (deprecated) | v2 (use this) |
| --- | --- |
| `parse_obj(data)` | `model_validate(data)` |
| `parse_raw(json_str)` | `model_validate_json(json_str)` |
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |
| `schema()` | `model_json_schema()` |
| `construct()` | `model_construct()` |

* * *

## Pandas-Specific Rules

### Always convert boolean columns to float64 before statistical operations

Boolean dtypes in pandas can produce integer results (0/1) instead of proper floats when aggregated.

#### Why:

Prevents mean calculations from returning exact 0.0 or 1.0 instead of intermediate floats like 0.37,
0.82.

#### Do:

```python
# Before any pivot_table or aggregation on boolean columns
df[IS_CORRECT_COLUMN] = df[IS_CORRECT_COLUMN].astype("float64")

# Then perform aggregations
result = df.pivot_table(
    index=GROUP_COLUMN,
    columns=CATEGORY_COLUMN,
    values=IS_CORRECT_COLUMN,
    aggfunc="mean",
)
```

#### Don't:

```python
# Direct aggregation on BooleanDtype without conversion
result = df.pivot_table(
    index=GROUP_COLUMN,
    columns=CATEGORY_COLUMN,
    values=IS_CORRECT_COLUMN,  # Still BooleanDtype
    aggfunc="mean",
)
```

* * *

### Always specify explicit dtypes for all CSV read operations

Pandas dtype inference is unpredictable and can cause inconsistent types, performance issues, and
subtle bugs.

#### Why:

* Type safety and consistency across pipeline stages
* Faster loading
* Predictable behavior

#### Do:

```python
# Define dtype specifications centrally
ANNOTATIONS_DTYPE: dict[str, dtype[Any] | ExtensionDtype] = {
    "instance_id": pd.UInt64Dtype(),
    "token": pd.StringDtype(),
    "category": pd.StringDtype(),
    # ... all columns
}

# Use in all CSV reads
df = pd.read_csv(
    filepath_or_buffer=path,
    dtype=ANNOTATIONS_DTYPE,
)
```

#### Don't:

```python
# Relying on pandas to infer dtypes
df = pd.read_csv(path)  # dtype inference can be wrong
```

* * *

### Use nullable dtypes, not native Python types

The pipeline uses pandas nullable dtypes throughout. Stick with them for consistency and correct NA
handling:

| Data kind | Use | Not |
| --- | --- | --- |
| Integer IDs | `pd.UInt64Dtype()` | `int` / `int64` |
| Small integers | `pd.Int8Dtype()` | `int` |
| Nullable ints | `pd.Int64Dtype()` | `float64` |
| Strings | `pd.StringDtype()` | `object` |
| Booleans | `pd.BooleanDtype()` | `bool` |
| Floats | `np.dtype("float64")` | - |

* * *

### Flatten MultiIndex columns after pivot_table

When using `pivot_table` with multiple aggfuncs, pandas returns MultiIndex columns. Convert them to
single-level:

#### Do:

```python
pivot = df.pivot_table(
    index=INSTANCE_ID_COLUMN,
    columns=MODEL_COLUMN,
    values=IS_CORRECT_COLUMN,
    aggfunc=["mean", "count"],
)

# Flatten MultiIndex columns
flat_columns: dict[tuple[str, Any], str] = {}
for agg_type, value in pivot.columns:
    flat_columns[(agg_type, value)] = f"{agg_type}_v{value}"

pivot.columns = [
    flat_columns[col] for col in pivot.columns
]
```

* * *

### Use `validate` parameter in merges

Always use `validate` in `pd.merge` to catch data integrity issues:

#### Do:

```python
# instances: one row per instance_id
# predictions: many rows per instance_id
df_merged = pd.merge(
    left=df_predictions,
    right=df_instances,
    on=INSTANCE_ID_COLUMN,
    how="left",
    validate="many_to_one",
)
```

* * *

## Multiprocessing Patterns

### Use batch-level parallelization

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

MAX_WORKERS: int = max(1, (cpu_count() or 4) - 3)

with ProcessPoolExecutor(
    max_workers=MAX_WORKERS,
) as executor:
    futures = [
        executor.submit(process_batch, batch=batch)
        for batch in batches
    ]
    results: list[BatchResult] = [
        f.result() for f in futures
    ]
```

* * *

## Resource Management

### Guarantee resource cleanup with try/finally for temporary files

If exceptions occur, temporary files may not be cleaned up, leading to disk space leaks.

#### Why:

Using try/finally ensures cleanup happens regardless of success or failure.

#### Do:

```python
temp_files: list[Path] = []

try:
    # Create and process temp files
    temp_files = create_temp_files()
    process_files(temp_files)
    return results
finally:
    # Guaranteed cleanup
    for temp_file in temp_files:
        if temp_file.exists():
            temp_file.unlink()
```

#### Don't:

```python
# Cleanup only at the end - won't run if exception occurs
temp_files = create_temp_files()
process_files(temp_files)

for temp_file in temp_files:
    temp_file.unlink()
```

* * *

## Imports

### Avoid `if TYPE_CHECKING:` blocks unless absolutely necessary

Import modules directly at the top level rather than conditionally importing them for type checking
only.

#### Why:

1. **Simplicity**: Reduces cognitive load and import complexity
2. **Runtime Safety**: Ensures imported types are available at runtime if needed
3. **Consistency**: Makes all imports visible in one place
4. **Circular Import Detection**: Forces you to fix circular dependencies properly

#### Do:

```python
from tasks.common.schemas import (
    ResultRecord,
    MetricRecord,
)
```

#### Don't:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tasks.common.schemas import (
        ResultRecord,
        MetricRecord,
    )
```

**Exception**: Only use `TYPE_CHECKING` blocks when there is a genuine circular import that cannot
be resolved through refactoring.

* * *

### Use absolute imports

Never use relative imports. Always use absolute imports from the project root.

#### Why:

1. Deep relative imports (like `from ...bar import f`) are confusing
2. Some tooling doesn't work well when mixing relative and absolute imports
3. Consistency across the codebase

#### Do:

```python
from tasks.common.schemas import (
    ResultRecord,
)
```

#### Don't:

```python
from .schemas import ResultRecord
```

#### Don't (sys.path hacks):

```python
import sys
sys.path.insert(0, str(Path(__file__).parent))
from wsd_loader import load_raganato_xml  # Fragile local import
```

### Task code imports use the full path from repo root

Task folders are Python packages (each has `__init__.py`). Always import task code using the full
absolute path from the repository root.

#### Why:

1. Task folder names are valid Python identifiers (`tNNNN_slug` format)
2. Each module has a globally unique path — no duplicate module conflicts
3. No `sys.path` manipulation needed
4. IDE autocomplete and mypy work correctly

#### Do:

```python
from tasks.t0012_build_wsd_data_loader_and_scorer.code.wsd_loader import (
    load_raganato_xml,
)
from tasks.t0012_build_wsd_data_loader_and_scorer.code.wsd_scorer import (
    score_micro_f1,
)
```

#### Don't:

```python
# Never use sys.path hacks
import sys
sys.path.insert(0, "tasks/t0012_build_wsd_data_loader_and_scorer/code")
from wsd_loader import load_raganato_xml

# Never use relative imports within task code
from .wsd_loader import load_raganato_xml
```

* * *

### Use direct imports with standard exceptions

Prefer direct imports (`from lib import f; f()`) except for standard libraries with conventional
aliases.

**Standard exceptions**:

* `import pandas as pd`
* `import numpy as np`
* `import polars as pl`

#### Why:

Missing module members throw errors during import, not later when accessed.

#### Do:

```python
from utils.metrics import compute_f1

compute_f1(...)
```

#### Don't:

```python
from utils import metrics

metrics.compute_f1(...)
```

* * *

## Documentation

### Avoid docstrings for simple dataclasses and helper functions

Don't add docstrings when the name and type hints make the purpose obvious. Only add docstrings for
non-obvious information.

#### Why:

1. **Noise Reduction**: Obvious documentation clutters code
2. **Maintenance Burden**: Docstrings need to stay in sync
3. **Type Hints Are Better**: For simple cases, type hints are self-documenting
4. **Focus on Non-Obvious**: Save documentation effort for complex logic

#### Do:

```python
@dataclass(frozen=True, slots=True)
class TestMetrics:
    total_questions: int
    answered_questions: int
    fast_clicks: int

def _count_lines(file_path: Path) -> int:
    with open(file=file_path, encoding="utf-8") as f:
        return sum(1 for _ in f)
```

#### Don't:

```python
@dataclass(frozen=True, slots=True)
class TestMetrics:
    """Metrics for a vocabulary test."""
    total_questions: int  # Total number of questions
    answered_questions: int  # Number of answered questions
    fast_clicks: int  # Number of fast clicks

def _count_lines(file_path: Path) -> int:
    """Counts the number of lines in a file."""
    with open(file=file_path, encoding="utf-8") as f:
        return sum(1 for _ in f)
```

* * *

## Command Line Tools

### Use tqdm for progress bars

Always use tqdm for long-running operations to provide user feedback.

### Use argparse for command line arguments

Use argparse for parsing command line arguments in scripts.

* * *

## Formatting Requirements

### Maximum line length: 100 characters

Keep all lines under 100 characters.

### PEP8 compliance

* No spaces in empty lines
* No trailing spaces
* Two empty lines between top-level functions
* One empty line at the end of the file

### Use Path instead of string paths

Use `pathlib.Path` for all file path operations, not string manipulation.

#### Do:

```python
from pathlib import Path

file_path = Path("data") / "results.csv"
```

#### Don't:

```python
import os

file_path = os.path.join("data", "results.csv")
```

* * *

## Python Version

Use Python 3.12+ syntax:

* `dict`, `list`, `tuple` (not `Dict`, `List`, `Tuple`)
* `type Word = str` (not `Word: TypeAlias = str`)
* PEP 695 style generics where applicable

* * *

## Checklist for New Task Scripts

When starting a new task script:

1. Define all input/output file paths as constants
2. Create `constants.py` with column names, dtype specs, and enums
3. Create typed `load_*()` functions that specify dtypes explicitly
4. Write analysis logic as pure functions in a separate module (no I/O mixed in)
5. Create `main.py` that orchestrates: load -> compute -> save
6. Use frozen dataclasses for all result containers
7. Add assertions after every load and merge

* * *

## Summary

The most commonly overlooked rules are:

1. **Always use dataclasses instead of tuples**
2. **Always use keyword arguments for 2+ heterogeneous parameters**
3. **Never return tuples from functions**
4. **Centralize all paths as constants**
5. **Use constants for all magic strings**
6. **Use `None` for missing data, never `0.0` or `""`**
7. **Use absolute imports, never relative imports**
8. **Always specify explicit dtypes for CSV reads**
9. **Use `validate` parameter in all pd.merge calls**

Follow these rules consistently to maintain code quality, type safety, and maintainability.
