from pathlib import Path

TASK_ROOT: Path = Path(__file__).resolve().parent.parent
DATASET_ID: str = "target-tuning-curve"

DATASET_DIR: Path = TASK_ROOT / "assets" / "dataset" / DATASET_ID
DATASET_FILES_DIR: Path = DATASET_DIR / "files"

DETAILS_PATH: Path = DATASET_DIR / "details.json"
DESCRIPTION_PATH: Path = DATASET_DIR / "description.md"

MEAN_CSV_PATH: Path = DATASET_FILES_DIR / "curve_mean.csv"
TRIALS_CSV_PATH: Path = DATASET_FILES_DIR / "curve_trials.csv"
GENERATOR_PARAMS_JSON_PATH: Path = DATASET_FILES_DIR / "generator_params.json"

RESULTS_IMAGES_DIR: Path = TASK_ROOT / "results" / "images"
PLOT_PATH: Path = RESULTS_IMAGES_DIR / "target_tuning_curve.png"
