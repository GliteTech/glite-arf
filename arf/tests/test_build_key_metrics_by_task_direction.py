from arf.scripts.aggregators.aggregate_metric_results import (
    MetricResultEntry,
    MetricResultsFull,
)
from arf.scripts.overview.format_tasks import TaskKeyMetric
from arf.scripts.overview.materialize import _build_key_metrics_by_task

TASK_A: str = "t_a"
METRIC_QWK: str = "qwk"
METRIC_MSE: str = "mse"


def _make_entry(*, task_id: str, value: float) -> MetricResultEntry:
    return MetricResultEntry(
        task_id=task_id,
        variant_id="",
        variant_label=None,
        value=value,
    )


def test_picks_max_when_higher_is_better_true() -> None:
    qwk_results: MetricResultsFull = MetricResultsFull(
        metric_key=METRIC_QWK,
        metric_name="Quadratic Weighted Kappa",
        unit="kappa",
        value_type="float",
        is_key=True,
        emoji=None,
        higher_is_better=True,
        result_count=2,
        entries=[
            _make_entry(task_id=TASK_A, value=0.8),
            _make_entry(task_id=TASK_A, value=0.9),
        ],
    )

    result: dict[str, list[TaskKeyMetric]] = _build_key_metrics_by_task(
        metric_results=[qwk_results],
    )
    assert TASK_A in result
    task_metrics: list[TaskKeyMetric] = result[TASK_A]
    assert len(task_metrics) == 1
    assert task_metrics[0].value == 0.9


def test_picks_min_when_higher_is_better_false() -> None:
    mse_results: MetricResultsFull = MetricResultsFull(
        metric_key=METRIC_MSE,
        metric_name="Mean Squared Error",
        unit="mse",
        value_type="float",
        is_key=True,
        emoji=None,
        higher_is_better=False,
        result_count=2,
        entries=[
            _make_entry(task_id=TASK_A, value=0.3),
            _make_entry(task_id=TASK_A, value=0.5),
        ],
    )

    result: dict[str, list[TaskKeyMetric]] = _build_key_metrics_by_task(
        metric_results=[mse_results],
    )
    assert TASK_A in result
    task_metrics: list[TaskKeyMetric] = result[TASK_A]
    assert len(task_metrics) == 1
    assert task_metrics[0].value == 0.3


def test_picks_both_correctly_in_mixed_input() -> None:
    qwk_results: MetricResultsFull = MetricResultsFull(
        metric_key=METRIC_QWK,
        metric_name="Quadratic Weighted Kappa",
        unit="kappa",
        value_type="float",
        is_key=True,
        emoji=None,
        higher_is_better=True,
        result_count=2,
        entries=[
            _make_entry(task_id=TASK_A, value=0.8),
            _make_entry(task_id=TASK_A, value=0.9),
        ],
    )
    mse_results: MetricResultsFull = MetricResultsFull(
        metric_key=METRIC_MSE,
        metric_name="Mean Squared Error",
        unit="mse",
        value_type="float",
        is_key=True,
        emoji=None,
        higher_is_better=False,
        result_count=2,
        entries=[
            _make_entry(task_id=TASK_A, value=0.3),
            _make_entry(task_id=TASK_A, value=0.5),
        ],
    )

    result: dict[str, list[TaskKeyMetric]] = _build_key_metrics_by_task(
        metric_results=[qwk_results, mse_results],
    )
    assert TASK_A in result
    task_metrics: list[TaskKeyMetric] = result[TASK_A]
    values_by_name: dict[str, object] = {m.metric_name: m.value for m in task_metrics}
    assert values_by_name["Quadratic Weighted Kappa"] == 0.9
    assert values_by_name["Mean Squared Error"] == 0.3
