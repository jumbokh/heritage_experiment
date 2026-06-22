# 從零開始操作手冊

本手冊提供一條最短可行路徑，讓你從空白環境開始，完成專案初始化、資料整理、資料集組裝與 YOLOv5 訓練前準備。

## 1. 取得專案

```powershell
git clone https://github.com/jumbokh/heritage_experiment.git
cd heritage_experiment
```

## 2. 建立執行環境

### 方法 A：使用 venv

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 方法 B：使用 Conda

```powershell
conda env create -f environment.yml
conda activate heritage-experiment
```

## 3. 另外安裝 YOLOv5

本專案不再內建 YOLOv5，請先另外 clone：

```powershell
git clone https://github.com/ultralytics/yolov5 D:\src\yolov5
python -m pip install -r D:\src\yolov5\requirements.txt
```

之後訓練時可用兩種方式指定：

- `--repo D:\src\yolov5`
- 設定環境變數 `YOLOV5_REPO=D:\src\yolov5`

## 4. 初始化專案資料夾

```powershell
python scripts/init_project.py
```

建立後，你至少會看到這些目錄：

- `data/`
- `docs/`
- `experiments/`
- `results/`

## 5. 準備原始資料

請把資料放到對應位置，例如：

- `data/raw/dunhuang_original/D1_intact/`
- `data/raw/dunhuang_original/D2_real_defect/`
- `data/raw/mobile_capture/screen_capture/`
- `data/raw/mobile_capture/print_capture/`

如果你是第一次跑流程，至少需要：

- 一批完整壁畫影像，用於合成缺陷
- 若要做 mixed dataset，還需要真實影像與對應 YOLO 標註

## 6. 跑前處理

```powershell
python scripts/preprocess/preprocess_and_inventory.py
```

這一步會建立：

- `data/raw/image_inventory.csv`
- `data/processed/resized/`
- `data/processed/grayscale/`
- `data/processed/edge_maps/`

## 7. 產生合成缺陷

```powershell
python scripts/generate_synthetic_damage.py --input data/raw/dunhuang_original/D1_intact --limit 5
```

執行後會輸出：

- `data/synthetic_damage/images/`
- `data/synthetic_damage/masks/`
- `data/synthetic_damage/masked_images/`
- `data/synthetic_damage/metadata/metadata.csv`

## 8. 建立標註與資料切分

```powershell
python scripts/annotations/generate_yolo_templates.py
python scripts/preprocess/create_dataset_splits.py
python scripts/assemble_detection_dataset.py
```

這一步會建立 synthetic-only YOLO detection dataset。

## 9. 匯入真實標註並組 mixed dataset

如果你有真實影像與 YOLO 標註，執行：

```powershell
python scripts/detection/import_real_yolo_samples.py
powershell -ExecutionPolicy Bypass -File scripts/detection/import_real_to_mixed.ps1
python scripts/assemble_mixed_detection_dataset.py --clean
```

注意：

- 真實標註檔要放在 `data/annotations/bbox_yolo/`
- 檔名要和系統產生的 `image_id` 一致
- 目前單張圖建議只標單一缺陷類別

## 10. 驗證資料格式

```powershell
python scripts/validation/check_annotation_specs.py
```

若格式正確，之後才能更穩定地進入訓練。

## 11. 產生訓練指令或直接訓練

### 先產生訓練指令

```powershell
python scripts/detection/train_yolov5.py --dataset-type mixed --repo D:\src\yolov5
```

### synthetic-only 訓練

```powershell
python scripts/detection/train_yolov5.py --dataset-type synthetic --repo D:\src\yolov5
```

### 直接執行訓練

```powershell
python scripts/detection/train_yolov5.py --dataset-type mixed --repo D:\src\yolov5 --execute
```

訓練相關輸出會寫到：

- `experiments/exp02_detection/configs/`
- `experiments/exp02_detection/runs/`

## 12. 一次跑完整流程

如果你想用單一入口執行主流程：

```powershell
python scripts/run_experiments.py --stage all
```

建議先單步確認每個階段都正常，再使用整體入口。

## 13. 常見問題

### 找不到 YOLOv5 repo

表示你尚未提供外部 YOLOv5 路徑。

處理方式：

- 確認 `D:\src\yolov5` 是否存在
- 或加上 `--repo <path>`
- 或設定 `YOLOV5_REPO`

### `torch` 不可用

表示目前 Python 環境沒有可用的 PyTorch。

處理方式：

- 先安裝 YOLOv5 的 `requirements.txt`
- 確認使用的是正確的 Python 環境

### `missing_processed_image`

表示真實資料還沒有跑完前處理。

處理方式：

- 先執行 `python scripts/preprocess/preprocess_and_inventory.py`

### `missing_label`

表示真實影像對應的 YOLO 標註檔不存在。

處理方式：

- 確認 `data/annotations/bbox_yolo/` 中有對應 `image_id.txt`

## 14. 建議閱讀順序

若你要更深入理解流程，建議接著看：

- `README.md`
- `docs/real_image_annotation_import_sop.md`
- `docs/annotation_guideline.md`
- `docs/real_synthetic_mixing_rules.md`
- `docs/yolov5_dataset_usage.md`
