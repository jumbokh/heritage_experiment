# External Dependencies

This directory is reserved for local, non-versioned external repositories and
artifacts.

## YOLOv5

Clone YOLOv5 separately instead of committing it into this repository:

```powershell
git clone https://github.com/ultralytics/yolov5 D:\src\yolov5
```

Then use one of the following when training:

- `python scripts\detection\train_yolov5.py --repo D:\src\yolov5`
- set `YOLOV5_REPO=D:\src\yolov5`

Local clones placed under `external/` are ignored by Git.
