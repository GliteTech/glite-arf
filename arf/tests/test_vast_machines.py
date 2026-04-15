"""Tests for arf.scripts.utils.vast_machines module.

Tests written before implementation to define the expected contract
for Vast.ai GPU provisioning utilities.
"""

from dataclasses import FrozenInstanceError
from typing import Any
from unittest.mock import MagicMock

import pytest

from arf.scripts.utils.vast_machines import (
    CREATION_TIMEOUT_SECONDS,
    DEFAULT_FILTERS,
    GPU_SPEED_TIERS,
    MAX_RETRY_OFFERS,
    POLL_INTERVAL_SECONDS,
    RELIABILITY_THRESHOLDS,
    DestroyResult,
    FailedAttempt,
    ProvisionResult,
    SearchCriteria,
    VastOffer,
    build_query_string,
    destroy_and_confirm,
    label_instance,
    rank_offers,
    reliability_threshold_for,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_criteria(**overrides: Any) -> SearchCriteria:
    defaults: dict[str, Any] = {
        "gpu_name": None,
        "num_gpus": 1,
        "min_gpu_ram": None,
        "min_cpu_ram": None,
        "min_disk": None,
        "min_reliability": 0.95,
        "estimated_hours_reference": 2.0,
        "extra_filters": None,
    }
    defaults.update(overrides)
    return SearchCriteria(**defaults)


def _make_offer(**overrides: Any) -> VastOffer:
    defaults: dict[str, Any] = {
        "offer_id": 1,
        "gpu": "RTX 3090",
        "gpu_count": 1,
        "gpu_ram_gb": 24.0,
        "cpu_ram_gb": 64.0,
        "disk_gb": 100.0,
        "price_per_hour": 0.30,
        "reliability": 0.99,
        "location": "US",
        "compute_cap": 860,
        "cuda_max_good": 12.6,
    }
    defaults.update(overrides)
    return VastOffer(**defaults)


# ---------------------------------------------------------------------------
# 1. test_default_filters_constant
# ---------------------------------------------------------------------------


def test_default_filters_constant() -> None:
    assert "compute_cap<1200" in DEFAULT_FILTERS
    assert "cuda_max_good>=12.6" in DEFAULT_FILTERS


# ---------------------------------------------------------------------------
# 2. test_build_query_string_includes_default_filters
# ---------------------------------------------------------------------------


def test_build_query_string_includes_default_filters() -> None:
    criteria: SearchCriteria = _make_criteria()
    query: str = build_query_string(criteria=criteria)
    assert DEFAULT_FILTERS in query


# ---------------------------------------------------------------------------
# 3. test_build_query_string_includes_gpu_name
# ---------------------------------------------------------------------------


def test_build_query_string_includes_gpu_name() -> None:
    criteria: SearchCriteria = _make_criteria(gpu_name="RTX_4090")
    query: str = build_query_string(criteria=criteria)
    assert "gpu_name=RTX_4090" in query


# ---------------------------------------------------------------------------
# 4. test_build_query_string_omits_null_gpu_name
# ---------------------------------------------------------------------------


def test_build_query_string_omits_null_gpu_name() -> None:
    criteria: SearchCriteria = _make_criteria(gpu_name=None)
    query: str = build_query_string(criteria=criteria)
    assert "gpu_name" not in query


# ---------------------------------------------------------------------------
# 5. test_rank_offers_fastest_first
# ---------------------------------------------------------------------------


def test_rank_offers_fastest_first() -> None:
    slow: VastOffer = _make_offer(
        offer_id=1,
        gpu="RTX 3090",
        price_per_hour=0.30,
    )
    medium: VastOffer = _make_offer(
        offer_id=2,
        gpu="RTX 4090",
        price_per_hour=0.50,
    )
    fast: VastOffer = _make_offer(
        offer_id=3,
        gpu="H100",
        price_per_hour=2.00,
    )
    ranked: list[VastOffer] = rank_offers(
        offers=[slow, fast, medium],
        estimated_hours_reference=10.0,
    )
    gpu_order: list[str] = [o.gpu for o in ranked]
    assert gpu_order.index("H100") < gpu_order.index("RTX 4090")
    assert gpu_order.index("RTX 4090") < gpu_order.index("RTX 3090")


# ---------------------------------------------------------------------------
# 6. test_rank_offers_prefers_cheaper_when_similar_speed
# ---------------------------------------------------------------------------


def test_rank_offers_prefers_cheaper_when_similar_speed() -> None:
    cheap: VastOffer = _make_offer(
        offer_id=1,
        gpu="RTX 3090",
        price_per_hour=0.20,
    )
    expensive: VastOffer = _make_offer(
        offer_id=2,
        gpu="RTX 3090",
        price_per_hour=0.50,
    )
    ranked: list[VastOffer] = rank_offers(
        offers=[expensive, cheap],
        estimated_hours_reference=2.0,
    )
    assert ranked[0].offer_id == cheap.offer_id


# ---------------------------------------------------------------------------
# 7. test_reliability_threshold_short_job
# ---------------------------------------------------------------------------


def test_reliability_threshold_short_job() -> None:
    threshold: float = reliability_threshold_for(estimated_hours=0.5)
    assert threshold == pytest.approx(0.95)


# ---------------------------------------------------------------------------
# 8. test_reliability_threshold_medium_job
# ---------------------------------------------------------------------------


def test_reliability_threshold_medium_job() -> None:
    threshold: float = reliability_threshold_for(estimated_hours=3.0)
    assert threshold == pytest.approx(0.98)


# ---------------------------------------------------------------------------
# 9. test_reliability_threshold_long_job
# ---------------------------------------------------------------------------


def test_reliability_threshold_long_job() -> None:
    threshold: float = reliability_threshold_for(estimated_hours=10.0)
    assert threshold == pytest.approx(0.995)


# ---------------------------------------------------------------------------
# 10. test_reliability_threshold_very_long_job
# ---------------------------------------------------------------------------


def test_reliability_threshold_very_long_job() -> None:
    threshold: float = reliability_threshold_for(estimated_hours=30.0)
    assert threshold == pytest.approx(0.999)


# ---------------------------------------------------------------------------
# 11. test_gpu_speed_tiers_has_reference_gpu
# ---------------------------------------------------------------------------


def test_gpu_speed_tiers_has_reference_gpu() -> None:
    assert "RTX 3090" in GPU_SPEED_TIERS
    assert GPU_SPEED_TIERS["RTX 3090"] == 1.0


# ---------------------------------------------------------------------------
# 12. test_failed_attempt_dataclass_frozen
# ---------------------------------------------------------------------------


def test_failed_attempt_dataclass_frozen() -> None:
    attempt: FailedAttempt = FailedAttempt(
        offer_id=1,
        instance_id=None,
        gpu="RTX 3090",
        failure_reason="timeout",
        failure_phase="creation",
        duration_seconds=120.0,
        wasted_cost_usd=0.02,
        timestamp="2026-04-12T00:00:00Z",
    )
    with pytest.raises(FrozenInstanceError):
        attempt.offer_id = 2  # type: ignore[misc]  # noqa: B003


# ---------------------------------------------------------------------------
# 13. test_provision_result_has_timing_fields
# ---------------------------------------------------------------------------


def test_provision_result_has_timing_fields() -> None:
    result: ProvisionResult = ProvisionResult(
        instance_id="123",
        offer=_make_offer(),
        ssh_host="1.2.3.4",
        ssh_port=22,
        gpu_verified="RTX 3090",
        cuda_version="12.6",
        label="test-label",
        created_at="2026-04-12T00:00:00Z",
        ready_at="2026-04-12T00:05:00Z",
        search_started_at="2026-04-12T00:00:00Z",
        total_provisioning_seconds=300.0,
        failed_attempts=[],
    )
    assert result.search_started_at == "2026-04-12T00:00:00Z"
    assert result.total_provisioning_seconds == 300.0


# ---------------------------------------------------------------------------
# 14. test_label_instance_calls_sdk
# ---------------------------------------------------------------------------


def test_label_instance_calls_sdk() -> None:
    mock_sdk: MagicMock = MagicMock()
    label_instance(
        sdk=mock_sdk,
        instance_id="12345",
        label="my-task",
    )
    mock_sdk.label_instance.assert_called_once_with(
        id="12345",
        label="my-task",
    )


# ---------------------------------------------------------------------------
# 15. test_destroy_and_confirm_returns_cost
# ---------------------------------------------------------------------------


def test_destroy_and_confirm_returns_cost() -> None:
    mock_sdk: MagicMock = MagicMock()
    mock_sdk.destroy_instance.return_value = {"success": True}
    mock_sdk.show_instances.return_value = []

    result: DestroyResult = destroy_and_confirm(
        sdk=mock_sdk,
        instance_id="12345",
        created_at="2026-04-12T00:00:00Z",
        price_per_hour=0.50,
    )
    assert result.instance_id == "12345"
    assert isinstance(result.destroyed_at, str)
    assert len(result.destroyed_at) > 0
    assert isinstance(result.total_duration_hours, float)
    assert isinstance(result.total_cost_usd, float)
    mock_sdk.destroy_instance.assert_called_once()


# ---------------------------------------------------------------------------
# Constants sanity checks
# ---------------------------------------------------------------------------


def test_constants_values() -> None:
    assert MAX_RETRY_OFFERS == 3
    assert pytest.approx(30.0) == POLL_INTERVAL_SECONDS
    assert pytest.approx(600.0) == CREATION_TIMEOUT_SECONDS
    assert len(RELIABILITY_THRESHOLDS) == 4
