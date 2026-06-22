# Real and Synthetic Mixing Rules

## Goal

Use synthetic samples to bootstrap detector learning without letting synthetic
appearance dominate evaluation.

## Default Rules Implemented

The script `scripts/assemble_mixed_detection_dataset.py` applies these rules:

1. Real data candidates are limited to inventory groups `D2`,
   `MOBILE_SCREEN`, and `MOBILE_PRINT`.
2. A real sample is included only when both files already exist:
   - `data/processed/resized/<image_id>.png`
   - `data/annotations/bbox_yolo/<image_id>.txt`
   - and `scripts/detection/import_real_yolo_samples.py` marks the row as `ready`
3. Real samples are split first into `train/val/test`.
4. Synthetic training samples are capped by
   `synthetic_multiplier * real_train_count`.
5. Validation and test prefer real samples.
   If no real `val/test` exist, the script backfills with synthetic rows.
6. If no eligible real samples exist, the mixed dataset degrades safely to a
   synthetic-only dataset.

## Recommended Practice

- Early-stage bootstrap:
  use synthetic-only or mixed data for coarse detector warm-up.
- Formal reporting:
  reserve real labeled images for `val/test` whenever possible.
- Domain control:
  never evaluate only on synthetic data when the paper claim concerns real
  cultural-heritage defects.

## Current Limitation

With only one source image or no real labels, `val/test` may remain empty or be
filled by synthetic data only. This is acceptable for pipeline debugging but
not for final experimental reporting.
