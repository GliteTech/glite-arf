from pathlib import Path

from arf.scripts.verificators.common import paths
from arf.tests.fixtures.writers import write_json, write_text

DEFAULT_SPEC_VERSION: int = 1
DEFAULT_SHORT_DESCRIPTION: str = "A test category for unit testing."
DEFAULT_DETAILED_DESCRIPTION: str = (
    "This is a detailed description of the test category that provides"
    " enough context to meet the minimum character requirement for"
    " validation purposes."
)
DEFAULT_METRIC_DESCRIPTION: str = "A test metric measuring accuracy of disambiguation results."
DEFAULT_METRIC_UNIT: str = "f1"
DEFAULT_METRIC_VALUE_TYPE: str = "float"
DEFAULT_TASK_TYPE_SHORT_DESC: str = "A test task type for unit testing."
DEFAULT_TASK_TYPE_DETAILED_DESC: str = (
    "This is a detailed description of the test task type that provides"
    " enough context to meet the minimum character requirement for"
    " validation in the verificator scripts."
)


def build_category(
    *,
    repo_root: Path,
    category_slug: str,
    name: str | None = None,
    short_description: str = DEFAULT_SHORT_DESCRIPTION,
    detailed_description: str = DEFAULT_DETAILED_DESCRIPTION,
    overrides: dict[str, object] | None = None,
) -> Path:
    data: dict[str, object] = {
        "spec_version": DEFAULT_SPEC_VERSION,
        "name": name if name is not None else category_slug.replace("-", " ").title(),
        "short_description": short_description,
        "detailed_description": detailed_description,
    }
    if overrides is not None:
        data.update(overrides)

    desc_path: Path = paths.category_description_path(
        category_slug=category_slug,
    )
    write_json(path=desc_path, data=data)
    return desc_path


def build_metric(
    *,
    repo_root: Path,
    metric_key: str,
    name: str | None = None,
    description: str = DEFAULT_METRIC_DESCRIPTION,
    unit: str = DEFAULT_METRIC_UNIT,
    value_type: str = DEFAULT_METRIC_VALUE_TYPE,
    higher_is_better: bool | None = True,
    is_key: bool | None = None,
    emoji: str | None = None,
    overrides: dict[str, object] | None = None,
) -> Path:
    data: dict[str, object] = {
        "spec_version": DEFAULT_SPEC_VERSION,
        "name": name if name is not None else metric_key.replace("_", " ").title(),
        "description": description,
        "unit": unit,
        "value_type": value_type,
    }
    # Pass `higher_is_better=None` to deliberately omit the field so tests
    # can exercise the required-field-missing code path. Any bool writes
    # the field through.
    if higher_is_better is not None:
        data["higher_is_better"] = higher_is_better
    if is_key is not None:
        data["is_key"] = is_key
    if emoji is not None:
        data["emoji"] = emoji
    if overrides is not None:
        data.update(overrides)

    metric_path: Path = paths.metric_definition_path(
        metric_key=metric_key,
    )
    write_json(path=metric_path, data=data)
    return metric_path


DEFAULT_TASK_TYPE_SPEC_VERSION: int = 2
DEFAULT_TASK_TYPE_HAS_EXTERNAL_COSTS: bool = True


def build_task_type(
    *,
    repo_root: Path,
    task_type_slug: str,
    name: str | None = None,
    short_description: str = DEFAULT_TASK_TYPE_SHORT_DESC,
    detailed_description: str = DEFAULT_TASK_TYPE_DETAILED_DESC,
    optional_steps: list[str] | None = None,
    has_external_costs: bool = DEFAULT_TASK_TYPE_HAS_EXTERNAL_COSTS,
    overrides: dict[str, object] | None = None,
) -> Path:
    data: dict[str, object] = {
        "spec_version": DEFAULT_TASK_TYPE_SPEC_VERSION,
        "name": (name if name is not None else task_type_slug.replace("-", " ").title()),
        "short_description": short_description,
        "detailed_description": detailed_description,
        "optional_steps": (optional_steps if optional_steps is not None else []),
        "has_external_costs": has_external_costs,
    }
    if overrides is not None:
        data.update(overrides)

    desc_path: Path = paths.task_type_description_path(
        task_type_slug=task_type_slug,
    )
    write_json(path=desc_path, data=data)

    instruction_path: Path = paths.task_type_instruction_path(
        task_type_slug=task_type_slug,
    )
    instruction_content: str = (
        f"# {data['name']} Instructions\n"
        "\n"
        "## Planning Guidelines\n"
        "\n"
        "Follow the standard planning process for this task type."
        " Ensure all requirements are documented and cost estimates"
        " are included in the plan.\n"
        "\n"
        "## Implementation Guidelines\n"
        "\n"
        "Implement according to the approved plan. Log all steps and"
        " verify outputs against the verification criteria defined"
        " in the plan.\n"
    )
    write_text(path=instruction_path, content=instruction_content)
    return desc_path
