from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MASK_DIR = PROJECT_ROOT / "data" / "synthetic_damage" / "masks"
MASKED_DIR = PROJECT_ROOT / "data" / "synthetic_damage" / "masked_images"
OUTPUT_DIR = PROJECT_ROOT / "data" / "annotations" / "bbox_yolo"
META_PATH = PROJECT_ROOT / "data" / "synthetic_damage" / "metadata" / "metadata.csv"
VALID_DAMAGE_TYPES = {"CRK": 0, "PLS": 1, "STN": 2}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate YOLO labels from synthetic defect masks.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing YOLO txt files.")
    return parser.parse_args()


def load_metadata() -> list[dict[str, str]]:
    if not META_PATH.exists():
        return []
    with META_PATH.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def mask_to_bbox(mask_path: Path) -> tuple[int, int, int, int] | None:
    mask = Image.open(mask_path).convert("L")
    mask_np = np.array(mask) > 0
    if not mask_np.any():
        return None
    ys, xs = np.where(mask_np)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def to_yolo_line(bbox: tuple[int, int, int, int], width: int, height: int, class_id: int) -> str:
    x_min, y_min, x_max, y_max = bbox
    box_w = (x_max - x_min + 1) / width
    box_h = (y_max - y_min + 1) / height
    center_x = (x_min + x_max + 1) / 2 / width
    center_y = (y_min + y_max + 1) / 2 / height
    return f"{class_id} {center_x:.6f} {center_y:.6f} {box_w:.6f} {box_h:.6f}"


def main() -> None:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_metadata()
    generated = 0
    skipped = 0

    for row in rows:
        image_id = row["image_id"]
        damage_type = row["damage_type"]
        class_id = VALID_DAMAGE_TYPES.get(damage_type)
        if class_id is None:
            skipped += 1
            continue

        label_path = OUTPUT_DIR / f"{image_id}.txt"
        if label_path.exists() and not args.overwrite:
            skipped += 1
            continue

        mask_path = MASK_DIR / row["mask_file"]
        image_path = MASKED_DIR / row["masked_image_file"]
        if not mask_path.exists() or not image_path.exists():
            skipped += 1
            continue

        bbox = mask_to_bbox(mask_path)
        if bbox is None:
            label_path.write_text("", encoding="utf-8")
            generated += 1
            continue

        width, height = Image.open(image_path).size
        line = to_yolo_line(bbox, width, height, class_id)
        label_path.write_text(line + "\n", encoding="utf-8")
        generated += 1

    print(f"Generated YOLO labels: {generated}")
    print(f"Skipped: {skipped}")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
