# 真實影像標註匯入 SOP

## 目的

將 `D2` 真實缺陷影像或手機拍攝影像匯入目前研究骨架，使其能自動進入：

1. `data/raw/image_inventory.csv`
2. `data/annotations/real_ready/real_detection_manifest.csv`
3. `data/datasets/yolo_detection_mixed/`

## 適用來源

- `D2` 真實缺陷影像
  放入 `data/raw/dunhuang_original/D2_real_defect/`
- 手機拍攝螢幕影像
  放入 `data/raw/mobile_capture/screen_capture/`
- 手機拍攝列印影像
  放入 `data/raw/mobile_capture/print_capture/`

## 檔名規則

- 影像檔可使用英數、底線，避免空白與中文標點
- 建議格式：
  - `d2_flake_001.jpg`
  - `mobile_screen_crack_002.png`
  - `mobile_print_stain_003.jpg`

系統在前處理後會自動轉成標準化 `image_id`，例如：

- `D2_0001_d2_flake_001`
- `MOBILE_SCREEN_0001_mobile_screen_crack_002`

## 標註規格

每張真實影像需有一個對應的 YOLO detection 標註檔，放在：

- `data/annotations/bbox_yolo/`

標註檔名稱必須與前處理後的 `image_id` 一致，例如：

- `D2_0001_d2_flake_001.txt`
- `MOBILE_SCREEN_0001_mobile_screen_crack_002.txt`

YOLO 每行格式：

```text
class_id center_x center_y width height
```

限制：

- 每行共 5 個欄位
- `class_id` 目前只接受：
  - `0` = crack
  - `1` = pigment_loss
  - `2` = stain
- 座標必須為 `0` 到 `1` 之間的小數
- 同一張圖目前建議只標同一類缺陷

## 操作步驟

1. 將真實影像放進對應資料夾
2. 執行前處理，產生標準化 `image_id`
3. 依照 `image_id` 建立對應 YOLO `.txt`
4. 執行 real manifest 匯入
5. 執行 mixed dataset 重組

## 建議命令

### 一鍵流程

```powershell
powershell -ExecutionPolicy Bypass -File scripts/detection/import_real_to_mixed.ps1
```

### 分步流程

```powershell
C:\Users\jumbo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe `
  scripts/preprocess/preprocess_and_inventory.py

C:\Users\jumbo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe `
  scripts/detection/import_real_yolo_samples.py

C:\Users\jumbo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe `
  scripts/assemble_mixed_detection_dataset.py --clean
```

## 匯入後檢查

檢查下列檔案：

- `data/raw/image_inventory.csv`
- `data/annotations/real_ready/real_detection_manifest.csv`
- `data/datasets/yolo_detection_mixed/mixed_manifest.csv`

如果匯入成功，`real_detection_manifest.csv` 內應看到：

- `group` 為 `D2`、`MOBILE_SCREEN` 或 `MOBILE_PRINT`
- `status` 為 `ready`

## 常見錯誤

- `missing_processed_image`
  - 尚未先跑前處理
- `missing_label`
  - 沒有放對應 YOLO `.txt`
- `invalid_yolo_format`
  - 標註檔不是 5 欄
- `out_of_range_label`
  - YOLO 座標超出 `0~1`
- `multi_class_per_image`
  - 同一張圖混入多個 class id

## 建議實務

- 真實資料優先保留給 `val/test`
- synthetic 資料主要用於 warm-up 與擴增
- 若是論文正式報告，請避免只用 synthetic `val/test`
