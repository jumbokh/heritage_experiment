# Heritage Experiment

This repository contains a Python-based experimental pipeline for cultural
heritage image analysis, with a current focus on optical-image-only mural defect
detection. The workflow covers preprocessing, synthetic defect generation,
annotation template generation, dataset assembly, and YOLOv5 training
preparation.

## Scope

The repository is intended to support early-stage research iteration on:

- image inventory and preprocessing,
- synthetic damage generation from intact mural images,
- YOLO detection label generation from masks,
- synthetic-only and mixed real/synthetic dataset assembly,
- training launch preparation and experiment record keeping.

This repository does not include the full research dataset, trained weights,
runtime outputs, or large intermediate artifacts.

## Environment Setup

Recommended baseline:

- Python 3.11
- Windows PowerShell for the provided `.ps1` launchers

Install the main dependencies with:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Or create a Conda environment:

```powershell
conda env create -f environment.yml
conda activate heritage-experiment
```

For YOLOv5 training, clone YOLOv5 separately and install its own dependencies:

```powershell
git clone https://github.com/ultralytics/yolov5 D:\src\yolov5
python -m pip install -r D:\src\yolov5\requirements.txt
```

Then point the training wrapper to that clone with `--repo` or `YOLOV5_REPO`.

## Repository Layout

```text
.
|-- docs/
|-- experiments/
|   `-- exp02_detection/
|       |-- configs/
|       `-- runs/                 # ignored by Git
|-- scripts/
|   |-- annotations/
|   |-- detection/
|   |-- preprocess/
|   `-- validation/
|-- external/                     # optional local clones, ignored by Git
|-- data/                         # local-only inputs and outputs, ignored by Git
`-- results/                      # local-only outputs, ignored by Git
```

## Main Scripts

- `scripts/init_project.py`
  Create the expected local folder structure for the experiment.
- `scripts/preprocess/preprocess_and_inventory.py`
  Build an image inventory and export normalized preprocessing outputs.
- `scripts/generate_synthetic_damage.py`
  Generate synthetic defects, masks, masked images, and metadata from intact
  mural images.
- `scripts/annotations/generate_yolo_templates.py`
  Convert defect masks into YOLO detection label templates.
- `scripts/preprocess/create_dataset_splits.py`
  Build train/val/test split manifests.
- `scripts/assemble_detection_dataset.py`
  Assemble a synthetic-only YOLO detection dataset.
- `scripts/detection/import_real_yolo_samples.py`
  Validate and register real annotated samples for mixed training.
- `scripts/assemble_mixed_detection_dataset.py`
  Assemble a mixed real/synthetic YOLO dataset using conservative sampling
  rules.
- `scripts/detection/train_yolov5.py`
  Validate dataset readiness and generate a YOLOv5 training launch note.
- `scripts/validation/check_annotation_specs.py`
  Validate consistency between YOLO labels, PNG masks, and annotation outputs.
- `scripts/run_experiments.py`
  Provide a single entrypoint for the full pipeline.

## Recommended Workflow

### 1. Initialize local structure

```powershell
python scripts/init_project.py
```

### 2. Run preprocessing

```powershell
python scripts/preprocess/preprocess_and_inventory.py
```

### 3. Generate synthetic defects

```powershell
python scripts/generate_synthetic_damage.py --input data/raw/dunhuang_original/D1_intact --limit 5
```

### 4. Build labels and splits

```powershell
python scripts/annotations/generate_yolo_templates.py
python scripts/preprocess/create_dataset_splits.py
python scripts/assemble_detection_dataset.py
```

### 5. Import real labels and build mixed dataset

```powershell
python scripts/detection/import_real_yolo_samples.py
powershell -ExecutionPolicy Bypass -File scripts/detection/import_real_to_mixed.ps1
python scripts/assemble_mixed_detection_dataset.py --clean
```

### 6. Validate and prepare training

```powershell
python scripts/validation/check_annotation_specs.py
python scripts/detection/train_yolov5.py --dataset-type mixed
```

### 7. Run the full pipeline from one entrypoint

```powershell
python scripts/run_experiments.py --stage all
```

## Local Data Expectations

The pipeline expects local data under `data/`, for example:

- `data/raw/dunhuang_original/D1_intact/`
- `data/raw/dunhuang_original/D2_real_defect/`
- `data/raw/mobile_capture/screen_capture/`
- `data/raw/mobile_capture/print_capture/`

Generated local artifacts include:

- `data/raw/image_inventory.csv`
- `data/processed/`
- `data/synthetic_damage/`
- `data/splits/split_manifest.csv`
- `data/datasets/yolo_detection/`
- `data/datasets/yolo_detection_mixed/`
- `data/annotations/real_ready/real_detection_manifest.csv`
- `results/logs/annotation_report.csv`

These directories are intentionally excluded from Git so the repository remains
lightweight and shareable.

## External Dependency

YOLOv5 is now treated as an external dependency rather than vendored source.
The training workflow expects one of the following:

- `--repo <path-to-yolov5>`
- `YOLOV5_REPO=<path-to-yolov5>`
- a local clone under `D:\src\yolov5`

This keeps the repository lighter and separates project code from upstream
training framework code.

## Documentation

- `docs/getting_started_zh_tw.md`
  Traditional Chinese step-by-step getting started guide.
- `docs/annotation_guideline.md`
  Annotation notes and class-level guidance.
- `docs/real_image_annotation_import_sop.md`
  SOP for importing real annotated images into the mixed dataset pipeline.
- `docs/real_synthetic_mixing_rules.md`
  Mixing strategy and evaluation guardrails for real and synthetic data.
- `docs/yolov5_dataset_usage.md`
  Dataset build order and YOLOv5 training launcher notes.
- `docs/experiment_log.md`
  Manual log for major experiment runs.
- `docs/naming_rules.md`
  Naming conventions for experiment assets.

## Current Limitations

- No fully locked environment file is provided yet.
- Large local datasets and outputs are not versioned in this repository.
- Mixed-dataset evaluation quality still depends on the amount and quality of
  real labeled data available locally.
- Some documentation files may still need cleanup or normalization.
- YOLOv5 must be cloned separately before training.

## Next Recommended Improvements

- Add `requirements-lock.txt`.
- Normalize document encodings and wording.
- Add sample metadata or a small public demo subset if sharing with others.
