import types
from pathlib import Path

import pytest

import arf.scripts.overview.format_metrics as format_metrics_module
import meta.asset_types.dataset.format_overview as format_datasets_module
from arf.scripts.verificators.common import paths as verificator_paths
from arf.tests.test_overview_dates import _configure_repo_paths

REAL_REPO_ROOT: Path = verificator_paths.REPO_ROOT

TARGET_MODULES: list[types.ModuleType] = [
    format_datasets_module,
    format_metrics_module,
]

EXPLICIT_CONSTANTS: list[tuple[types.ModuleType, str]] = [
    (format_datasets_module, "DATASETS_README"),
    (format_datasets_module, "DATASETS_BY_DATE_DIR"),
    (format_datasets_module, "DATASETS_BY_DATE_README"),
    (format_datasets_module, "DATASETS_BY_CATEGORY_DIR"),
    (format_metrics_module, "METRICS_README"),
]


def _path_is_under(*, candidate: Path, ancestor: Path) -> bool:
    if candidate == ancestor:
        return True
    return ancestor in candidate.parents


def _collect_leaky_path_attrs(
    *,
    module: types.ModuleType,
    ancestor: Path,
) -> dict[str, Path]:
    leaky: dict[str, Path] = {}
    for attr_name in dir(module):
        if attr_name.startswith("_"):
            continue
        value: object = getattr(module, attr_name)
        if not isinstance(value, Path):
            continue
        if _path_is_under(candidate=value, ancestor=ancestor):
            leaky[attr_name] = value
    return leaky


@pytest.mark.parametrize(
    argnames=("module", "attr_name"),
    argvalues=EXPLICIT_CONSTANTS,
    ids=[f"{module.__name__}.{attr_name}" for module, attr_name in EXPLICIT_CONSTANTS],
)
def test_explicit_constant_redirected_under_tmp_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    module: types.ModuleType,
    attr_name: str,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    post_value: object = getattr(module, attr_name)
    assert isinstance(post_value, Path), (
        f"{module.__name__}.{attr_name} is not a Path after _configure_repo_paths"
    )
    assert _path_is_under(candidate=post_value, ancestor=tmp_path), (
        f"{module.__name__}.{attr_name} = {post_value} is not under tmp_path {tmp_path}; "
        "_configure_repo_paths did not redirect it"
    )


def test_no_materializer_path_constant_leaks_to_real_repo_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pre_leaky: dict[str, dict[str, Path]] = {}
    for module in TARGET_MODULES:
        pre_leaky[module.__name__] = _collect_leaky_path_attrs(
            module=module,
            ancestor=REAL_REPO_ROOT,
        )

    assert any(len(attrs) > 0 for attrs in pre_leaky.values()), (
        "Expected at least one Path constant in materializer modules to resolve under the real "
        "REPO_ROOT before _configure_repo_paths runs"
    )

    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)

    unredirected: list[str] = []
    for module in TARGET_MODULES:
        for attr_name in pre_leaky[module.__name__]:
            post_value: object = getattr(module, attr_name)
            assert isinstance(post_value, Path), (
                f"{module.__name__}.{attr_name} is not a Path after _configure_repo_paths"
            )
            if not _path_is_under(candidate=post_value, ancestor=tmp_path):
                unredirected.append(
                    f"{module.__name__}.{attr_name} = {post_value} (not under {tmp_path})"
                )

    assert len(unredirected) == 0, (
        "_configure_repo_paths failed to redirect these materializer path constants to tmp_path: "
        + "; ".join(unredirected)
    )
