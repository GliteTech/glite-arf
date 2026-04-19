from arf.scripts.overview.format_dashboard import (
    _sort_key_for_value as _sort_key_for_value_dashboard,
)
from arf.scripts.overview.format_metric_results import (
    _sort_key_for_value as _sort_key_for_value_metric_results,
)


def test_metric_results_descending_when_higher_is_better() -> None:
    values: list[float] = [1.0, 3.0, 2.0]
    result: list[float] = sorted(
        values,
        key=lambda v: _sort_key_for_value_metric_results(
            value=v,
            higher_is_better=True,
        ),
    )
    assert result == [3.0, 2.0, 1.0]


def test_metric_results_ascending_when_lower_is_better() -> None:
    values: list[float] = [1.0, 3.0, 2.0]
    result: list[float] = sorted(
        values,
        key=lambda v: _sort_key_for_value_metric_results(
            value=v,
            higher_is_better=False,
        ),
    )
    assert result == [1.0, 2.0, 3.0]


def test_metric_results_none_ranks_last_when_higher_is_better() -> None:
    values: list[object] = [1.0, None, 3.0, 2.0]
    result: list[object] = sorted(
        values,
        key=lambda v: _sort_key_for_value_metric_results(
            value=v,
            higher_is_better=True,
        ),
    )
    assert result[-1] is None
    assert result[:-1] == [3.0, 2.0, 1.0]


def test_metric_results_none_ranks_last_when_lower_is_better() -> None:
    values: list[object] = [1.0, None, 3.0, 2.0]
    result: list[object] = sorted(
        values,
        key=lambda v: _sort_key_for_value_metric_results(
            value=v,
            higher_is_better=False,
        ),
    )
    assert result[-1] is None
    assert result[:-1] == [1.0, 2.0, 3.0]


def test_dashboard_descending_when_higher_is_better() -> None:
    values: list[float] = [1.0, 3.0, 2.0]
    result: list[float] = sorted(
        values,
        key=lambda v: _sort_key_for_value_dashboard(
            value=v,
            higher_is_better=True,
        ),
    )
    assert result == [3.0, 2.0, 1.0]


def test_dashboard_ascending_when_lower_is_better() -> None:
    values: list[float] = [1.0, 3.0, 2.0]
    result: list[float] = sorted(
        values,
        key=lambda v: _sort_key_for_value_dashboard(
            value=v,
            higher_is_better=False,
        ),
    )
    assert result == [1.0, 2.0, 3.0]


def test_dashboard_none_ranks_last_when_higher_is_better() -> None:
    values: list[object] = [1.0, None, 3.0, 2.0]
    result: list[object] = sorted(
        values,
        key=lambda v: _sort_key_for_value_dashboard(
            value=v,
            higher_is_better=True,
        ),
    )
    assert result[-1] is None


def test_dashboard_none_ranks_last_when_lower_is_better() -> None:
    values: list[object] = [1.0, None, 3.0, 2.0]
    result: list[object] = sorted(
        values,
        key=lambda v: _sort_key_for_value_dashboard(
            value=v,
            higher_is_better=False,
        ),
    )
    assert result[-1] is None
