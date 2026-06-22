# Real Image Annotation Import SOP

## 目的

將真實缺陷影像與其 YOLO 標註安全匯入目前的研究流程，使其能被納入：

- `data/raw/image_inventory.csv`
- `data/annotations/real_ready/real_detection_manifest.csv`
- `data/datasets/yolo_detection_mixed/`

## 適用資料來源

- `data/raw/dunhuang_original/D2_real_defect/`
  敦煌真實缺陷影像
- `data/raw/mobile_capture/screen_capture/`
  手機螢幕翻拍影像
- `data/raw/mobile_capture/print_capture/`
  紙本列印翻拍影像

在 mixed dataset 組裝流程中，只有下列 `group` 會被視為真實資料候選：

- `D2`
- `MOBILE_SCREEN`
- `MOBILE_PRINT`

## 命名要求

原始影像檔名建議使用英文小寫、數字與底線，避免空白與中文，例如：

- `d2_flake_001.jpg`
- `mobile_screen_crack_002.png`
- `mobile_print_stain_003.jpg`

完成前處理後，系統會依資料來源自動產生 `image_id`，例如：

- `D2_0001_d2_flake_001`
- `MOBILE_SCREEN_0001_mobile_screen_crack_002`

YOLO 標註檔名稱必須和 `image_id` 完全一致，例如：

- `D2_0001_d2_flake_001.txt`
- `MOBILE_SCREEN_0001_mobile_screen_crack_002.txt`

## 標註要求

YOLO 標註檔需放在：

- `data/annotations/bbox_yolo/`

每一行格式固定為：

```text
class_id center_x center_y width height
```

限制如下：

- 每一行必須只有 5 個欄位
- `center_x`, `center_y`, `width`, `height` 必須是 `0` 到 `1` 之間的小數
- 單張影像目前只接受單一缺陷類別

目前支援的類別如下：

- `0` = crack
- `1` = pigment_loss
- `2` = stain

如果同一張圖混入多個 `class_id`，匯入時會被標記為 `multi_class_per_image`。

## 作業流程

### 一次完成流程

```powershell
powershell -ExecutionPolicy Bypass -File scripts/detection/import_real_to_mixed.ps1
```

### 分步流程

1. 將真實影像放到對應原始資料夾
2. 執行前處理，建立 `image_inventory.csv` 與 resized 影像
3. 依 `image_id` 建立對應的 YOLO `.txt`
4. 執行真實標註匯入
5. 重新組裝 mixed dataset

```powershell
python scripts/preprocess/preprocess_and_inventory.py
python scripts/detection/import_real_yolo_samples.py
python scripts/assemble_mixed_detection_dataset.py --clean
```

## 匯入成功的必要條件

對於每一筆真實樣本，系統會檢查：

- `data/processed/resized/<image_id>.png` 是否存在
- `data/annotations/bbox_yolo/<image_id>.txt` 是否存在
- YOLO 格式是否正確
- 是否只包含單一類別

全部通過後，該筆資料才會在 `real_detection_manifest.csv` 中被標記為 `ready`。

## 匯入後檢查

請確認下列檔案已更新：

- `data/raw/image_inventory.csv`
- `data/annotations/real_ready/real_detection_manifest.csv`
- `data/datasets/yolo_detection_mixed/mixed_manifest.csv`

若匯入成功，可在 `real_detection_manifest.csv` 中看到：

- `group` 為 `D2`、`MOBILE_SCREEN` 或 `MOBILE_PRINT`
- `status` 為 `ready`
- `image_path` 與 `label_path` 已填入

## 常見狀態碼

- `missing_processed_image`
  尚未先執行前處理
- `missing_label`
  找不到對應的 YOLO `.txt`
- `empty_label`
  標註檔存在但內容為空
- `invalid_yolo_format`
  某一行不是 5 欄格式
- `unknown_class_id`
  類別不在目前支援清單內
- `non_numeric_label`
  座標欄位含非數字內容
- `out_of_range_label`
  YOLO 座標超出 `0` 到 `1`
- `multi_class_per_image`
  同一張圖混入多種缺陷類別

## 建議做法

- 研究初期可用 synthetic-only 或 mixed dataset 做 warm-up
- 正式評估時，盡量保留真實資料給 `val/test`
- 若真實標註樣本太少，mixed dataset 可能退化成以 synthetic 為主，這可用於除錯，但不適合正式報告
