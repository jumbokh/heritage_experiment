# Experiment Log

## 使用方式

本文件用來手動記錄重要實驗，特別是下列情境：

- 資料集版本有明顯變更
- 訓練參數有調整
- 評估策略改動
- 需要和論文、簡報或報告對應的實驗

建議每次重要執行新增一個區塊，並填入可重現資訊。

## Log Template

```text
Date:
Operator:
Experiment ID:
Goal:

Data:
- inventory source:
- dataset type:
- train/val/test notes:

Command:

Key parameters:
- weights:
- imgsz:
- batch:
- epochs:
- device:

Outputs:
- config note:
- run directory:
- metrics file:

Observations:
- 

Next action:
- 
```

## Example Entry

```text
Date: 2026-06-22
Operator: jumbo
Experiment ID: exp02_detection_mixed_baseline
Goal: Verify mixed real/synthetic detection pipeline end to end.

Data:
- inventory source: data/raw/image_inventory.csv
- dataset type: mixed
- train/val/test notes: validation and test should prefer real samples

Command:
python scripts/detection/train_yolov5.py --dataset-type mixed

Key parameters:
- weights: yolov5n.pt
- imgsz: 960
- batch: 8
- epochs: 100
- device: 0

Outputs:
- config note: experiments/exp02_detection/configs/
- run directory: experiments/exp02_detection/runs/
- metrics file: results/metrics_csv/

Observations:
- Training launcher generated the note successfully.

Next action:
- Compare mixed and synthetic-only baselines.
```
