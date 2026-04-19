from __future__ import annotations

import json
from dataclasses import asdict, dataclass

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tasks.t0004_generate_target_tuning_curve.code.paths import (
    DATASET_FILES_DIR,
    GENERATOR_PARAMS_JSON_PATH,
    MEAN_CSV_PATH,
    PLOT_PATH,
    RESULTS_IMAGES_DIR,
    TRIALS_CSV_PATH,
)


@dataclass(frozen=True, slots=True)
class GeneratorParams:
    theta_pref_deg: float
    r_base_hz: float
    r_peak_hz: float
    n: float
    n_angles: int
    n_trials: int
    noise_sd_hz: float
    random_seed: int


DEFAULT_PARAMS: GeneratorParams = GeneratorParams(
    theta_pref_deg=90.0,
    r_base_hz=2.0,
    r_peak_hz=32.0,
    n=2.0,
    n_angles=12,
    n_trials=20,
    noise_sd_hz=3.0,
    random_seed=42,
)


ANGLE_COLUMN: str = "angle_deg"
MEAN_RATE_COLUMN: str = "mean_rate_hz"
TRIAL_INDEX_COLUMN: str = "trial_index"
TRIAL_RATE_COLUMN: str = "rate_hz"

DSI_MIN: float = 0.6
DSI_MAX: float = 0.9


def compute_mean_curve(*, params: GeneratorParams) -> np.ndarray:
    angles_rad: np.ndarray = np.linspace(
        start=0.0,
        stop=2.0 * np.pi,
        num=params.n_angles,
        endpoint=False,
    )
    theta_pref_rad: float = float(np.deg2rad(params.theta_pref_deg))
    cos_term: np.ndarray = (1.0 + np.cos(angles_rad - theta_pref_rad)) / 2.0
    amplitude: float = params.r_peak_hz - params.r_base_hz
    mean_curve: np.ndarray = params.r_base_hz + amplitude * (cos_term**params.n)
    return mean_curve


def compute_dsi(*, params: GeneratorParams) -> float:
    amplitude: float = params.r_peak_hz - params.r_base_hz
    pref_rate: float = params.r_base_hz + amplitude * (1.0**params.n)
    null_rate: float = params.r_base_hz + amplitude * (0.0**params.n)
    return (pref_rate - null_rate) / (pref_rate + null_rate)


def sample_trials(
    *,
    mean_curve: np.ndarray,
    params: GeneratorParams,
) -> np.ndarray:
    rng: np.random.Generator = np.random.default_rng(seed=params.random_seed)
    noise: np.ndarray = rng.normal(
        loc=0.0,
        scale=params.noise_sd_hz,
        size=(params.n_angles, params.n_trials),
    )
    trials: np.ndarray = mean_curve[:, None] + noise
    return np.clip(trials, a_min=0.0, a_max=None)


def build_mean_dataframe(
    *,
    angles_deg: np.ndarray,
    mean_curve: np.ndarray,
) -> pd.DataFrame:
    return pd.DataFrame(
        data={
            ANGLE_COLUMN: angles_deg,
            MEAN_RATE_COLUMN: mean_curve,
        }
    )


def build_trials_dataframe(
    *,
    angles_deg: np.ndarray,
    trials: np.ndarray,
) -> pd.DataFrame:
    n_angles: int = trials.shape[0]
    n_trials: int = trials.shape[1]
    angle_col: np.ndarray = np.repeat(angles_deg, repeats=n_trials)
    trial_col: np.ndarray = np.tile(np.arange(n_trials), reps=n_angles)
    rate_col: np.ndarray = trials.reshape(-1)
    return pd.DataFrame(
        data={
            ANGLE_COLUMN: angle_col,
            TRIAL_INDEX_COLUMN: trial_col,
            TRIAL_RATE_COLUMN: rate_col,
        }
    )


def plot_curve(
    *,
    angles_deg: np.ndarray,
    mean_curve: np.ndarray,
    trials: np.ndarray,
    dsi: float,
    params: GeneratorParams,
) -> None:
    RESULTS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    dense_angles_deg: np.ndarray = np.linspace(start=0.0, stop=360.0, num=361, endpoint=True)
    dense_angles_rad: np.ndarray = np.deg2rad(dense_angles_deg)
    theta_pref_rad: float = float(np.deg2rad(params.theta_pref_deg))
    amplitude: float = params.r_peak_hz - params.r_base_hz
    dense_curve: np.ndarray = params.r_base_hz + amplitude * (
        ((1.0 + np.cos(dense_angles_rad - theta_pref_rad)) / 2.0) ** params.n
    )

    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    ax.plot(
        dense_angles_deg,
        dense_curve,
        color="#1f77b4",
        linewidth=2.0,
        label="Closed-form target",
    )
    trial_means: np.ndarray = trials.mean(axis=1)
    trial_sds: np.ndarray = trials.std(axis=1, ddof=1)
    ax.errorbar(
        angles_deg,
        trial_means,
        yerr=trial_sds,
        fmt="o",
        color="#d62728",
        ecolor="#d62728",
        capsize=3.0,
        label=f"Mean ± SD over {params.n_trials} trials",
    )
    n_trials: int = trials.shape[1]
    scatter_angle: np.ndarray = np.repeat(angles_deg, repeats=n_trials)
    scatter_rate: np.ndarray = trials.reshape(-1)
    ax.scatter(
        scatter_angle,
        scatter_rate,
        color="#d62728",
        alpha=0.15,
        s=10.0,
        label="Individual trials",
    )
    ax.set_xlabel("Direction θ (deg)")
    ax.set_ylabel("Firing rate (Hz)")
    ax.set_xlim(0.0, 360.0)
    ax.set_ylim(0.0, params.r_peak_hz * 1.15)
    ax.set_xticks(np.arange(0, 361, 45))
    ax.set_title(
        f"Target direction tuning curve "
        f"(θ_pref={params.theta_pref_deg:.0f}°, "
        f"n={params.n:.1f}, DSI={dsi:.3f})"
    )
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(PLOT_PATH, dpi=150)
    plt.close(fig)


def write_generator_params_json(*, params: GeneratorParams) -> None:
    DATASET_FILES_DIR.mkdir(parents=True, exist_ok=True)
    payload: dict[str, float | int] = asdict(obj=params)
    GENERATOR_PARAMS_JSON_PATH.write_text(
        data=json.dumps(obj=payload, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    params: GeneratorParams = DEFAULT_PARAMS
    dsi: float = compute_dsi(params=params)
    assert DSI_MIN <= dsi <= DSI_MAX, (
        f"DSI {dsi:.3f} outside acceptance band [{DSI_MIN}, {DSI_MAX}]; adjust r_peak_hz"
    )

    mean_curve: np.ndarray = compute_mean_curve(params=params)
    angles_deg: np.ndarray = np.linspace(
        start=0.0,
        stop=360.0,
        num=params.n_angles,
        endpoint=False,
    )
    trials: np.ndarray = sample_trials(mean_curve=mean_curve, params=params)

    DATASET_FILES_DIR.mkdir(parents=True, exist_ok=True)

    df_mean: pd.DataFrame = build_mean_dataframe(
        angles_deg=angles_deg,
        mean_curve=mean_curve,
    )
    df_mean.to_csv(path_or_buf=MEAN_CSV_PATH, index=False)

    df_trials: pd.DataFrame = build_trials_dataframe(
        angles_deg=angles_deg,
        trials=trials,
    )
    df_trials.to_csv(path_or_buf=TRIALS_CSV_PATH, index=False)

    write_generator_params_json(params=params)
    plot_curve(
        angles_deg=angles_deg,
        mean_curve=mean_curve,
        trials=trials,
        dsi=dsi,
        params=params,
    )

    sample_mean: np.ndarray = trials.mean(axis=1)
    abs_bias: np.ndarray = np.abs(sample_mean - mean_curve)
    print(f"DSI={dsi:.4f}")
    print(
        f"rows: mean_csv={len(df_mean)} trials_csv={len(df_trials)} "
        f"(expected {params.n_angles} / {params.n_angles * params.n_trials})"
    )
    print(
        "per-angle mean |sample - closed|: "
        f"max={abs_bias.max():.3f} Hz, "
        f"mean={abs_bias.mean():.3f} Hz"
    )
    print(f"wrote: {MEAN_CSV_PATH}")
    print(f"wrote: {TRIALS_CSV_PATH}")
    print(f"wrote: {GENERATOR_PARAMS_JSON_PATH}")
    print(f"wrote: {PLOT_PATH}")


if __name__ == "__main__":
    main()
