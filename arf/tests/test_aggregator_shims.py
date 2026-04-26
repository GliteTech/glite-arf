"""Tests for aggregator shim modules under arf.scripts.aggregators.

Every asset-type aggregator lives in ``meta.asset_types.<kind>.aggregator``.
For ergonomics and consistency with the other aggregators, each asset-type
aggregator must also be reachable as
``arf.scripts.aggregators.aggregate_<kind>``. The shim must:

1. Import cleanly.
2. Re-export ``main`` as the *same function object* as the real aggregator
   (true identity via ``is``, not merely equal).
3. Work when invoked as a module via ``python -m``.
"""

import importlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT: Path = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class ShimPair:
    shim_module: str
    real_module: str
    top_level_key: str


SHIM_PAIRS: list[ShimPair] = [
    ShimPair(
        shim_module="arf.scripts.aggregators.aggregate_answers",
        real_module="meta.asset_types.answer.aggregator",
        top_level_key="answers",
    ),
    ShimPair(
        shim_module="arf.scripts.aggregators.aggregate_papers",
        real_module="meta.asset_types.paper.aggregator",
        top_level_key="papers",
    ),
    ShimPair(
        shim_module="arf.scripts.aggregators.aggregate_datasets",
        real_module="meta.asset_types.dataset.aggregator",
        top_level_key="datasets",
    ),
    ShimPair(
        shim_module="arf.scripts.aggregators.aggregate_libraries",
        real_module="meta.asset_types.library.aggregator",
        top_level_key="libraries",
    ),
    ShimPair(
        shim_module="arf.scripts.aggregators.aggregate_models",
        real_module="meta.asset_types.model.aggregator",
        top_level_key="models",
    ),
    ShimPair(
        shim_module="arf.scripts.aggregators.aggregate_predictions",
        real_module="meta.asset_types.predictions.aggregator",
        top_level_key="predictions",
    ),
]


@pytest.mark.parametrize(
    "pair",
    SHIM_PAIRS,
    ids=[p.shim_module.rsplit(".", 1)[-1] for p in SHIM_PAIRS],
)
def test_shim_imports_cleanly(pair: ShimPair) -> None:
    shim: ModuleType = importlib.import_module(pair.shim_module)
    real: ModuleType = importlib.import_module(pair.real_module)
    assert shim is not None
    assert real is not None


@pytest.mark.parametrize(
    "pair",
    SHIM_PAIRS,
    ids=[p.shim_module.rsplit(".", 1)[-1] for p in SHIM_PAIRS],
)
def test_shim_main_is_real_main_object(pair: ShimPair) -> None:
    shim: ModuleType = importlib.import_module(pair.shim_module)
    real: ModuleType = importlib.import_module(pair.real_module)

    assert hasattr(shim, "main"), f"shim {pair.shim_module} missing 'main'"
    assert hasattr(real, "main"), f"real {pair.real_module} missing 'main'"
    assert shim.main is real.main, (
        f"shim {pair.shim_module}.main is not the same object as {pair.real_module}.main"
    )


@pytest.mark.parametrize(
    "pair",
    SHIM_PAIRS,
    ids=[p.shim_module.rsplit(".", 1)[-1] for p in SHIM_PAIRS],
)
def test_shim_runs_as_module_and_emits_json(pair: ShimPair) -> None:
    result: subprocess.CompletedProcess[str] = subprocess.run(
        args=[
            sys.executable,
            "-u",
            "-m",
            pair.shim_module,
            "--format",
            "json",
            "--detail",
            "short",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"Running shim {pair.shim_module} failed with code "
        f"{result.returncode}; stderr={result.stderr!r}"
    )

    payload: object = json.loads(result.stdout)
    assert isinstance(payload, dict), (
        f"Shim {pair.shim_module} JSON output must be an object; got {type(payload).__name__}"
    )
    assert pair.top_level_key in payload, (
        f"Shim {pair.shim_module} JSON output missing expected top-level "
        f"key {pair.top_level_key!r}; got keys={list(payload.keys())}"
    )
