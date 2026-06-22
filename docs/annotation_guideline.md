# Annotation Guideline

## 目的

本文件用於統一真實影像與衍生資料的缺陷標註方式，避免資料集在類別定義、標註範圍與檔名上出現不一致。

## 目前類別

- `0` = crack
- `1` = pigment_loss
- `2` = stain

## 類別判定原則

### crack

- 線狀、條狀、裂隙狀缺陷
- 幾何形態通常較細長，方向性明顯
- 若主要破壞表現為裂紋延伸，優先標為 `crack`

### pigment_loss

- 顏料或表層材料剝落、缺失
- 常見為塊狀、片狀的缺口
- 若主要表現為彩層缺失而非污漬，優先標為 `pigment_loss`

### stain

- 污漬、色斑、沉積、滲痕等非結構性髒污
- 若主要表現為色彩污染或附著痕跡，標為 `stain`

## 邊界框原則

- 使用最小可包覆缺陷區域的矩形框
- 避免把大面積背景一起包入
- 缺陷邊界不明顯時，以可重現的保守框為主
- 同類缺陷若彼此明顯分離，應分成多個框

## 目前流程限制

- 單張真實影像目前建議只標一種缺陷類別
- 若同圖含多種類別，`import_real_yolo_samples.py` 目前會標記為 `multi_class_per_image`
- 如需支援多類混合，需先同步修改匯入與 mixed dataset 流程

## YOLO 格式要求

每一行格式如下：

```text
class_id center_x center_y width height
```

檢查要點：

- 一行必須正好 5 欄
- 類別代碼必須在 `0`、`1`、`2`
- 座標值必須在 `0` 到 `1`
- 文字編碼應為 UTF-8 或 ASCII

## 標註前檢查

- 確認對應影像已完成前處理並生成 `image_id`
- 確認標註檔名稱與 `image_id` 一致
- 確認標註類別與研究定義一致

## 標註後檢查

- 以文字方式檢查欄位數與數值範圍
- 執行 `python scripts/detection/import_real_yolo_samples.py`
- 若有錯誤狀態，先修正再進入 mixed dataset 組裝
