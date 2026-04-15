FRONTMATTER_FIELD_TASK_ID: str = "task_id"
FRONTMATTER_FIELD_STATUS: str = "status"

STATUS_PARTIAL: str = "partial"

# ---------------------------------------------------------------------------
# Task lifecycle constants (shared across verificators)
# ---------------------------------------------------------------------------

TASK_BRANCH_PREFIX: str = "task/"

COMPLETED_TASK_STATUSES: set[str] = {"completed", "cancelled", "permanently_failed"}
FINISHED_STEP_STATUSES: set[str] = {"completed", "skipped", "failed"}

MANDATORY_DIRS: list[str] = [
    "plan",
    "research",
    "results",
    "logs",
    "logs/steps",
    "logs/commands",
    "logs/searches",
    "logs/sessions",
]

MANDATORY_RESULT_FILES: list[str] = [
    "results/results_summary.md",
    "results/results_detailed.md",
    "results/metrics.json",
    "results/suggestions.json",
]

# Files allowed to be modified outside the task folder on a task branch.
ALLOWED_OUTSIDE_FILES: list[str] = [
    "pyproject.toml",
    "uv.lock",
    "ruff.toml",
    ".gitignore",
    "mypy.ini",
    ".gitattributes",
    "overview/",
    "arf/scripts/",
    "tasks/",
]

# All asset type verificators are now discovered dynamically from
# meta/asset_types/<type>/verificator.py via the asset registry.
# No hardcoded module paths remain.


def build_asset_type_verificator_modules() -> dict[str, str]:
    """Build the verificator module map from the asset type registry.

    Scans ``meta/asset_types/*/verificator.py`` and returns a dict mapping
    each asset type slug to its verificator's dotted module path.
    """
    from arf.scripts.common.asset_registry import build_verificator_module_map

    return build_verificator_module_map()


ASSET_TYPE_VERIFICATOR_MODULES: dict[str, str] = build_asset_type_verificator_modules()
