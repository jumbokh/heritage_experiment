# Heritage Experiment Skeleton

This project contains a minimal Python skeleton for the optical-image-only
heritage experiment workflow.

Included scripts:

- `scripts/init_project.py`
  Create the folder structure used by the experiment.
- `scripts/preprocess/preprocess_and_inventory.py`
  Build the raw image inventory and export normalized preprocessing outputs.
- `scripts/generate_synthetic_damage.py`
  Read intact mural images, generate synthetic defects, and export masks,
  masked images, and metadata.
- `scripts/annotations/generate_yolo_templates.py`
  Derive YOLO bounding boxes from synthetic defect masks and create label files.
- `scripts/preprocess/create_dataset_splits.py`
  Split synthetic samples into train/val/test manifests.
- `scripts/assemble_detection_dataset.py`
  Assemble a YOLO-style detection dataset and export `dataset.yaml`.
- `scripts/assemble_mixed_detection_dataset.py`
  Assemble a mixed real/synthetic YOLO dataset with conservative sampling rules.
- `scripts/detection/import_real_yolo_samples.py`
  Validate real YOLO labels and register ready rows into a real-sample manifest.
- `scripts/detection/import_real_to_mixed.ps1`
  Run preprocess, real-manifest import, and mixed-dataset assembly in one step.
- `scripts/detection/train_yolov5.py`
  Validate dataset readiness and generate a YOLOv5 training command or launch note.
- `scripts/validation/check_annotation_specs.py`
  Validate YOLO, PNG mask, and LabelMe annotation consistency.
- `scripts/run_experiments.py`
  Run the preprocessing, synthesis, dataset preparation, and validation stages
  from one entrypoint.

Suggested usage:

```powershell
python scripts/init_project.py
python scripts/preprocess/preprocess_and_inventory.py
python scripts/generate_synthetic_damage.py --input data/raw/dunhuang_original/D1_intact --limit 5
python scripts/annotations/generate_yolo_templates.py
python scripts/preprocess/create_dataset_splits.py
python scripts/assemble_detection_dataset.py
python scripts/detection/import_real_yolo_samples.py
powershell -ExecutionPolicy Bypass -File scripts/detection/import_real_to_mixed.ps1
python scripts/assemble_mixed_detection_dataset.py --clean
python scripts/detection/train_yolov5.py --dataset-type mixed
python scripts/validation/check_annotation_specs.py
python scripts/run_experiments.py --stage all
```

Outputs:

- `data/raw/image_inventory.csv`
- `data/processed/resized/`
- `data/processed/grayscale/`
- `data/processed/edge_maps/`
- `data/synthetic_damage/images/`
- `data/synthetic_damage/masks/`
- `data/synthetic_damage/masked_images/`
- `data/synthetic_damage/metadata/metadata.csv`
- `data/splits/split_manifest.csv`
- `data/datasets/yolo_detection/`
- `data/datasets/yolo_detection_mixed/`
- `data/annotations/real_ready/real_detection_manifest.csv`
- `results/logs/annotation_report.csv`
