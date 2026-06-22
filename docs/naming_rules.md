# Naming Rules

## 目的

統一原始影像、衍生資料、標註檔與實驗輸出的命名，降低人工整理與自動腳本對接時的錯誤。

## 一般原則

- 優先使用英文小寫、數字與底線
- 避免空白、中文、特殊符號
- 同一批資料使用固定前綴與流水號
- 命名應能反映資料來源與缺陷類型

## 原始影像建議格式

- `d2_flake_001.jpg`
- `mobile_screen_crack_002.png`
- `mobile_print_stain_003.jpg`

建議元素：

- 資料來源
- 缺陷簡述
- 三位以上流水號

## 系統生成的 image_id

前處理後，系統會產生帶有群組前綴的 `image_id`，例如：

- `D1_0001_some_source_name`
- `D2_0001_d2_flake_001`
- `MOBILE_SCREEN_0001_mobile_screen_crack_002`
- `MOBILE_PRINT_0001_mobile_print_stain_003`

後續多數衍生檔案都應以 `image_id` 為主鍵。

## 標註檔命名

YOLO 標註檔命名必須與 `image_id` 一致：

- `D2_0001_d2_flake_001.txt`
- `MOBILE_SCREEN_0001_mobile_screen_crack_002.txt`

標註檔放置位置：

- `data/annotations/bbox_yolo/`

## 衍生資料命名

以下資料建議直接沿用 `image_id`：

- `data/processed/resized/<image_id>.png`
- `data/processed/grayscale/<image_id>.png`
- `data/processed/edge_maps/<image_id>.png`
- `data/annotations/mask_png/<image_id>.png`

## 合成缺陷資料命名

合成樣本通常包含基底影像編號與缺陷代碼，例如：

- `DH_SYN_0010_CRK_20.png`

建議保留：

- synthetic 前綴
- 基底樣本流水號
- 缺陷類型代碼
- 強度或變體代碼

## 實驗輸出命名

訓練或配置輸出應包含模型、資料集類型與時間戳，例如：

- `yolov5_launch_20260621-154015.md`
- `mixed_yolov5n_20260621_154015`
- `synthetic_yolov5n_20260621_153417`

## 不建議做法

- 同資料夾中混用多種命名風格
- 用人工改名破壞 `image_id` 和標註檔的一致性
- 在檔名中加入空白、括號或中文
- 省略流水號，導致同名覆蓋
