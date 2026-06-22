# Launch Notes Transition

This folder previously stored YOLOv5 launch notes generated when the project
still vendored `external/yolov5_official/` inside the repository.

Those historical notes were removed from the tracked tree because they pointed
to an outdated dependency layout and could mislead current users.

## What Changed

- YOLOv5 is no longer committed into this repository.
- Training now requires an external YOLOv5 clone.
- Use `--repo <path-to-yolov5>` or `YOLOV5_REPO=<path-to-yolov5>` when running
  `scripts/detection/train_yolov5.py`.

## Current Recommended Flow

```powershell
git clone https://github.com/ultralytics/yolov5 D:\src\yolov5
python -m pip install -r D:\src\yolov5\requirements.txt
python scripts\detection\train_yolov5.py --dataset-type mixed --repo D:\src\yolov5
```

## Historical Backup

The original launch notes were backed up locally before cleanup under:

- `experiments/exp02_detection/configs.bak-20260622-launch-notes/`

That backup is intended for local historical reference and is not part of the
tracked repository state.
