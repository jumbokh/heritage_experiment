# YOLOv5 Dataset Usage

## Available Datasets

- `data/datasets/yolo_detection/`
  Synthetic-only detection dataset built from generated masks.
- `data/datasets/yolo_detection_mixed/`
  Mixed real/synthetic detection dataset. Real samples are included only when
  matching resized images and YOLO labels already exist.

## External YOLOv5 Setup

This repository no longer vendors YOLOv5. Clone it separately before training:

```powershell
git clone https://github.com/ultralytics/yolov5 D:\src\yolov5
python -m pip install -r D:\src\yolov5\requirements.txt
```

Training can then find YOLOv5 by:

- passing `--repo D:\src\yolov5`
- setting `YOLOV5_REPO=D:\src\yolov5`

## Recommended Order

1. `python scripts/preprocess/preprocess_and_inventory.py`
2. `python scripts/generate_synthetic_damage.py --limit 0`
3. `python scripts/annotations/generate_yolo_templates.py --overwrite`
4. `python scripts/preprocess/create_dataset_splits.py`
5. `python scripts/assemble_detection_dataset.py --clean`
6. `python scripts/detection/import_real_yolo_samples.py`
7. `python scripts/assemble_mixed_detection_dataset.py --clean`
8. `python scripts/detection/train_yolov5.py --dataset-type mixed`

## Training Launcher

The launcher script does three things before training:

- validates that the dataset YAML exists,
- counts `train/val/test` images,
- writes a launch note under `experiments/exp02_detection/configs/`.

Example:

```powershell
python scripts\detection\train_yolov5.py `
  --dataset-type mixed `
  --repo D:\src\yolov5 `
  --weights yolov5n.pt `
  --imgsz 960 `
  --batch 8 `
  --epochs 100 `
  --device 0
```

If the YOLOv5 repository is not found, the script still writes the launch note
and prints a message asking you to set `--repo` or `YOLOV5_REPO`.

PowerShell launchers:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/detection/launch_yolov5_synth.ps1
powershell -ExecutionPolicy Bypass -File scripts/detection/launch_yolov5_mixed.ps1
```
