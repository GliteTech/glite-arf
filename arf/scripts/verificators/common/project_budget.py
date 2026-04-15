"""Shared project budget models and helpers."""

import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from arf.scripts.verificators.common.paths import PROJECT_BUDGET_PATH

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TOTAL_BUDGET_FIELD: str = "total_budget"
CURRENCY_FIELD: str = "currency"
PER_TASK_DEFAULT_LIMIT_FIELD: str = "per_task_default_limit"
AVAILABLE_SERVICES_FIELD: str = "available_services"
ALERTS_FIELD: str = "alerts"
WARN_AT_PERCENT_FIELD: str = "warn_at_percent"
STOP_AT_PERCENT_FIELD: str = "stop_at_percent"

_CURRENCY_PATTERN: re.Pattern[str] = re.compile(r"^[A-Z]{3}$")
_NON_ALNUM_PATTERN: re.Pattern[str] = re.compile(r"[^a-z0-9]+")

KNOWN_SERVICE_ALIASES: dict[str, tuple[str, ...]] = {
    "openai_api": ("openai", "gpt"),
    "anthropic_api": ("anthropic", "claude"),
    "vast_ai": ("vast-ai", "vastai"),
}


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class BudgetAlertsModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    warn_at_percent: int = Field(ge=0, le=100)
    stop_at_percent: int = Field(ge=0, le=100)

    @model_validator(mode="after")
    def _validate_threshold_order(self) -> "BudgetAlertsModel":
        if self.stop_at_percent < self.warn_at_percent:
            raise ValueError("stop_at_percent must be greater than or equal to warn_at_percent")
        return self


class ProjectBudgetModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    total_budget: float = Field(ge=0.0)
    currency: str
    per_task_default_limit: float = Field(ge=0.0)
    available_services: list[str]
    alerts: BudgetAlertsModel

    @field_validator(CURRENCY_FIELD)
    @classmethod
    def _validate_currency(cls, value: str) -> str:
        if not _CURRENCY_PATTERN.fullmatch(value):
            raise ValueError("currency must be a 3-letter uppercase ISO 4217 code")
        return value

    @field_validator(AVAILABLE_SERVICES_FIELD)
    @classmethod
    def _validate_available_services(
        cls,
        value: list[str],
    ) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in value:
            if len(item.strip()) == 0:
                raise ValueError("available_services entries must be non-empty strings")
            if item in seen:
                raise ValueError(f"available_services contains a duplicate entry: {item}")
            seen.add(item)
            cleaned.append(item)
        return cleaned


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def budget_threshold_usd(
    *,
    total_budget: float,
    threshold_percent: int,
) -> float:
    return total_budget * threshold_percent / 100.0


def load_project_budget(
    *,
    file_path: Path = PROJECT_BUDGET_PATH,
) -> ProjectBudgetModel | None:
    try:
        raw: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    try:
        return ProjectBudgetModel.model_validate_json(raw)
    except ValidationError:
        return None


def normalize_service_key(*, value: str) -> str:
    lowered: str = value.lower()
    return _NON_ALNUM_PATTERN.sub("", lowered)


def service_aliases(*, service: str) -> list[str]:
    aliases: list[str] = [service]

    if service.endswith("_api"):
        aliases.append(service.removesuffix("_api"))
    if service.endswith("-api"):
        aliases.append(service.removesuffix("-api"))

    aliases.extend(KNOWN_SERVICE_ALIASES.get(service, ()))

    deduped: list[str] = []
    seen: set[str] = set()
    for alias in aliases:
        normalized: str = normalize_service_key(value=alias)
        if len(normalized) == 0 or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(alias)
    return deduped
