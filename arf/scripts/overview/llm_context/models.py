"""Typed models for overview LLM context archives."""

from dataclasses import dataclass, field

from arf.scripts.aggregators.aggregate_categories import CategoryInfo
from arf.scripts.aggregators.aggregate_costs import CostAggregationFull
from arf.scripts.aggregators.aggregate_metrics import MetricInfoFull
from arf.scripts.aggregators.aggregate_suggestions import SuggestionInfoFull
from arf.scripts.aggregators.aggregate_task_types import TaskTypeInfo
from arf.scripts.aggregators.aggregate_tasks import TaskInfoFull
from meta.asset_types.answer.aggregator import AnswerInfoFull
from meta.asset_types.dataset.aggregator import DatasetInfoFull
from meta.asset_types.library.aggregator import LibraryInfoFull
from meta.asset_types.model.aggregator import ModelInfoFull
from meta.asset_types.paper.aggregator import PaperInfoFull
from meta.asset_types.predictions.aggregator import PredictionsInfoFull


@dataclass(frozen=True, slots=True)
class LLMContextWindow:
    label: str
    max_tokens: int


@dataclass(frozen=True, slots=True)
class ArchiveSection:
    section_id: str
    title: str
    source_kind: str
    source_name: str
    source_ids: list[str]
    repo_paths: list[str]
    content: str


@dataclass(frozen=True, slots=True)
class PresetOptions:
    include_completed_task_details: bool
    include_planned_task_long_descriptions: bool
    include_research_documents: bool
    include_suggestions: bool
    suggestion_limit: int | None
    include_papers: bool
    paper_limit: int | None
    include_datasets: bool
    include_libraries: bool
    include_metrics: bool
    include_full_answers: bool


@dataclass(frozen=True, slots=True)
class PresetContentDetail:
    content_type: str
    coverage: str


@dataclass(frozen=True, slots=True)
class PresetDefinition:
    preset_id: str
    title: str
    file_name: str
    description: str
    use_case: str
    included_content: list[str]
    options: PresetOptions
    short_name: str | None = None
    featured_rank: int | None = None
    content_details: list[PresetContentDetail] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ProjectSnapshot:
    project_description: str
    tasks: list[TaskInfoFull]
    answers: list[AnswerInfoFull]
    papers: list[PaperInfoFull]
    datasets: list[DatasetInfoFull]
    libraries: list[LibraryInfoFull]
    metrics: list[MetricInfoFull]
    suggestions: list[SuggestionInfoFull]
    models: list[ModelInfoFull] = field(default_factory=list)
    predictions: list[PredictionsInfoFull] = field(default_factory=list)
    categories: list[CategoryInfo] = field(default_factory=list)
    task_types: list[TaskTypeInfo] = field(default_factory=list)
    costs: CostAggregationFull | None = None


@dataclass(frozen=True, slots=True)
class LLMContextArchiveSummary:
    preset_id: str
    title: str
    file_name: str
    description: str
    use_case: str
    included_content: list[str]
    section_count: int
    char_count: int
    byte_count: int
    estimated_tokens: int
    compatibility_labels: list[str]
    short_name: str | None = None
    featured_rank: int | None = None
    content_details: list[PresetContentDetail] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class RenderedArchive:
    preset: PresetDefinition
    sections: list[ArchiveSection]
    content: str
    summary: LLMContextArchiveSummary


@dataclass(frozen=True, slots=True)
class TypeArchiveDefinition:
    type_id: str
    title: str
    file_name: str
    description: str
    included_content: list[str]


@dataclass(frozen=True, slots=True)
class TypeArchiveSummary:
    type_id: str
    title: str
    file_name: str
    description: str
    included_content: list[str]
    section_count: int
    char_count: int
    byte_count: int
    estimated_tokens: int
    compatibility_labels: list[str]


@dataclass(frozen=True, slots=True)
class RenderedTypeArchive:
    definition: TypeArchiveDefinition
    sections: list[ArchiveSection]
    content: str
    summary: TypeArchiveSummary
