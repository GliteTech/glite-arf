"""Vast.ai GPU provisioning utilities."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_FILTERS: str = "rentable=true verified=true compute_cap<1200 cuda_max_good>=12.6"

GPU_SPEED_TIERS: dict[str, float] = {
    "GTX 1080 Ti": 0.35,
    "RTX 2080 Ti": 0.55,
    "RTX 3060": 0.40,
    "RTX 3070": 0.60,
    "RTX 3080": 0.80,
    "RTX 3090": 1.0,
    "RTX 4070": 0.90,
    "RTX 4070 Ti": 1.05,
    "RTX 4080": 1.30,
    "RTX 4090": 1.60,
    "RTX 5060 Ti": 1.00,
    "RTX 5070 Ti": 1.50,
    "RTX 5090": 2.50,
    "A100 40GB": 1.80,
    "A100 80GB": 2.00,
    "H100": 3.00,
    "H200": 3.50,
    "RTX PRO 6000 S": 2.80,
    "RTX PRO 6000 WS": 2.80,
}

RELIABILITY_THRESHOLDS: list[tuple[float, float]] = [
    (1.0, 0.95),
    (5.0, 0.98),
    (24.0, 0.995),
    (float("inf"), 0.999),
]

MAX_RETRY_OFFERS: int = 3
POLL_INTERVAL_SECONDS: float = 30.0
CREATION_TIMEOUT_SECONDS: float = 600.0

SIMILAR_SPEED_TOLERANCE: float = 0.20
DEFAULT_SPEED_TIER: float = 1.0


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SearchCriteria:
    gpu_name: str | None
    num_gpus: int
    min_gpu_ram: float | None
    min_cpu_ram: float | None
    min_disk: float | None
    min_reliability: float
    estimated_hours_reference: float
    extra_filters: str | None = None


@dataclass(frozen=True, slots=True)
class VastOffer:
    offer_id: int
    gpu: str
    gpu_count: int
    gpu_ram_gb: float
    cpu_ram_gb: float
    disk_gb: float
    price_per_hour: float
    reliability: float
    location: str
    compute_cap: int
    cuda_max_good: float


@dataclass(frozen=True, slots=True)
class FailedAttempt:
    offer_id: int
    instance_id: str | None
    gpu: str
    failure_reason: str
    failure_phase: str
    duration_seconds: float
    wasted_cost_usd: float
    timestamp: str


@dataclass(frozen=True, slots=True)
class ProvisionResult:
    instance_id: str
    offer: VastOffer
    ssh_host: str
    ssh_port: int
    gpu_verified: str
    cuda_version: str
    label: str
    created_at: str
    ready_at: str
    search_started_at: str
    total_provisioning_seconds: float
    failed_attempts: list[FailedAttempt]


@dataclass(frozen=True, slots=True)
class DestroyResult:
    instance_id: str
    destroyed_at: str
    total_duration_hours: float
    total_cost_usd: float


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def build_query_string(*, criteria: SearchCriteria) -> str:
    parts: list[str] = [DEFAULT_FILTERS]

    if criteria.gpu_name is not None:
        parts.append(f"gpu_name={criteria.gpu_name}")

    if criteria.num_gpus > 1:
        parts.append(f"num_gpus={criteria.num_gpus}")

    if criteria.min_gpu_ram is not None:
        parts.append(f"gpu_ram>={criteria.min_gpu_ram}")

    if criteria.min_cpu_ram is not None:
        parts.append(f"cpu_ram>={criteria.min_cpu_ram}")

    if criteria.min_disk is not None:
        parts.append(f"disk_space>={criteria.min_disk}")

    if criteria.min_reliability > 0.0:
        parts.append(f"reliability>={criteria.min_reliability}")

    if criteria.extra_filters is not None:
        parts.append(criteria.extra_filters)

    return " ".join(parts)


def _estimate_hours(
    *,
    offer: VastOffer,
    estimated_hours_reference: float,
) -> float:
    reference_speed: float = GPU_SPEED_TIERS.get("RTX 3090", DEFAULT_SPEED_TIER)
    offer_speed: float = GPU_SPEED_TIERS.get(offer.gpu, DEFAULT_SPEED_TIER)
    assert offer_speed > 0.0, "GPU speed tier is positive"
    return estimated_hours_reference * (reference_speed / offer_speed)


def rank_offers(
    *,
    offers: list[VastOffer],
    estimated_hours_reference: float,
) -> list[VastOffer]:
    decorated: list[tuple[float, float, VastOffer]] = []
    for offer in offers:
        est_hours: float = _estimate_hours(
            offer=offer,
            estimated_hours_reference=estimated_hours_reference,
        )
        decorated.append((est_hours, offer.price_per_hour, offer))

    decorated.sort(key=lambda t: (t[0], t[1]))

    result: list[VastOffer] = []
    for est_hours, price, offer in decorated:
        inserted: bool = False
        for i, existing in enumerate(result):
            existing_hours: float = _estimate_hours(
                offer=existing,
                estimated_hours_reference=estimated_hours_reference,
            )
            ratio: float = abs(est_hours - existing_hours) / max(existing_hours, 1e-9)
            if ratio <= SIMILAR_SPEED_TOLERANCE:
                if price < existing.price_per_hour:
                    result.insert(i, offer)
                    inserted = True
                    break
            elif est_hours < existing_hours:
                result.insert(i, offer)
                inserted = True
                break
        if not inserted:
            result.append(offer)

    return result


def reliability_threshold_for(*, estimated_hours: float) -> float:
    for max_hours, threshold in RELIABILITY_THRESHOLDS:
        if estimated_hours <= max_hours:
            return threshold
    return RELIABILITY_THRESHOLDS[-1][1]


def label_instance(*, sdk: Any, instance_id: str, label: str) -> None:
    sdk.label_instance(
        id=instance_id,
        label=label,
    )


def destroy_and_confirm(
    *,
    sdk: Any,
    instance_id: str,
    created_at: str,
    price_per_hour: float,
) -> DestroyResult:
    sdk.destroy_instance(id=instance_id)

    now: datetime = datetime.now(tz=UTC)
    destroyed_at: str = now.isoformat()

    created_dt: datetime = datetime.fromisoformat(created_at)
    duration_seconds: float = (now - created_dt).total_seconds()
    duration_hours: float = duration_seconds / 3600.0
    total_cost: float = duration_hours * price_per_hour

    return DestroyResult(
        instance_id=instance_id,
        destroyed_at=destroyed_at,
        total_duration_hours=duration_hours,
        total_cost_usd=total_cost,
    )
