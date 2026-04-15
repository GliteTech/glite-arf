"""Helpers for normalizing task results metrics.json files."""

import re
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LEGACY_FORMAT_KIND: str = "legacy"
EXPLICIT_VARIANTS_FORMAT_KIND: str = "explicit_variants"

VARIANTS_FIELD: str = "variants"
VARIANT_ID_FIELD: str = "variant_id"
LABEL_FIELD: str = "label"
DIMENSIONS_FIELD: str = "dimensions"
METRICS_FIELD: str = "metrics"

IMPLICIT_VARIANT_ID: str = ""
ALLOWED_VARIANT_FIELDS: set[str] = {
    VARIANT_ID_FIELD,
    LABEL_FIELD,
    DIMENSIONS_FIELD,
    METRICS_FIELD,
}

VARIANT_ID_PATTERN: re.Pattern[str] = re.compile(
    r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$",
)
SNAKE_CASE_PATTERN: re.Pattern[str] = re.compile(
    r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$",
)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TaskMetricVariant:
    variant_id: str
    label: str | None
    dimensions: dict[str, object]
    metrics: dict[str, object]
    is_implicit: bool


@dataclass(frozen=True, slots=True)
class TaskMetricsDocument:
    format_kind: str
    variants: list[TaskMetricVariant]


class TaskMetricsFormatError(ValueError):
    """Raised when a task metrics payload cannot be normalized."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def is_scalar_metric_value(*, value: object) -> bool:
    if value is None:
        return True
    return isinstance(value, bool | int | float | str)


def normalize_task_metrics_data(*, data: dict[str, object]) -> TaskMetricsDocument:
    if VARIANTS_FIELD not in data:
        return TaskMetricsDocument(
            format_kind=LEGACY_FORMAT_KIND,
            variants=[
                TaskMetricVariant(
                    variant_id=IMPLICIT_VARIANT_ID,
                    label=None,
                    dimensions={},
                    metrics=dict(data),
                    is_implicit=True,
                ),
            ],
        )

    if set(data.keys()) != {VARIANTS_FIELD}:
        raise TaskMetricsFormatError(
            f"Explicit variant format only allows the top-level '{VARIANTS_FIELD}' field",
        )

    variants_value: object = data.get(VARIANTS_FIELD)
    if not isinstance(variants_value, list):
        raise TaskMetricsFormatError(f"'{VARIANTS_FIELD}' must be a list")
    if len(variants_value) == 0:
        raise TaskMetricsFormatError(
            f"'{VARIANTS_FIELD}' must contain at least one variant; use {{}} for no metrics",
        )

    seen_variant_ids: set[str] = set()
    variants: list[TaskMetricVariant] = []
    for index, raw_variant in enumerate(variants_value):
        if not isinstance(raw_variant, dict):
            raise TaskMetricsFormatError(f"Variant #{index + 1} is not a JSON object")
        if set(raw_variant.keys()) != ALLOWED_VARIANT_FIELDS:
            raise TaskMetricsFormatError(
                f"Variant #{index + 1} must define exactly: "
                f"{', '.join(sorted(ALLOWED_VARIANT_FIELDS))}",
            )

        variant_id: object = raw_variant.get(VARIANT_ID_FIELD)
        if not isinstance(variant_id, str) or len(variant_id) == 0:
            raise TaskMetricsFormatError(
                f"Variant #{index + 1} has an invalid '{VARIANT_ID_FIELD}'",
            )
        if VARIANT_ID_PATTERN.match(variant_id) is None:
            raise TaskMetricsFormatError(
                f"Variant '{variant_id}' has an invalid '{VARIANT_ID_FIELD}'",
            )
        if variant_id in seen_variant_ids:
            raise TaskMetricsFormatError(f"Duplicate variant_id '{variant_id}'")
        seen_variant_ids.add(variant_id)

        label: object = raw_variant.get(LABEL_FIELD)
        if not isinstance(label, str) or len(label.strip()) == 0:
            raise TaskMetricsFormatError(
                f"Variant '{variant_id}' has an invalid '{LABEL_FIELD}'",
            )

        dimensions: object = raw_variant.get(DIMENSIONS_FIELD)
        if not isinstance(dimensions, dict):
            raise TaskMetricsFormatError(
                f"Variant '{variant_id}' has an invalid '{DIMENSIONS_FIELD}'",
            )
        for key, value in dimensions.items():
            if not isinstance(key, str) or not is_scalar_metric_value(value=value):
                raise TaskMetricsFormatError(
                    f"Variant '{variant_id}' has a non-scalar '{DIMENSIONS_FIELD}' entry",
                )

        metrics: object = raw_variant.get(METRICS_FIELD)
        if not isinstance(metrics, dict):
            raise TaskMetricsFormatError(
                f"Variant '{variant_id}' has an invalid '{METRICS_FIELD}'",
            )
        for key, value in metrics.items():
            if not isinstance(key, str) or not is_scalar_metric_value(value=value):
                raise TaskMetricsFormatError(
                    f"Variant '{variant_id}' has a non-scalar '{METRICS_FIELD}' entry",
                )

        variants.append(
            TaskMetricVariant(
                variant_id=variant_id,
                label=label,
                dimensions=dict(dimensions),
                metrics=dict(metrics),
                is_implicit=False,
            ),
        )

    return TaskMetricsDocument(
        format_kind=EXPLICIT_VARIANTS_FORMAT_KIND,
        variants=variants,
    )
