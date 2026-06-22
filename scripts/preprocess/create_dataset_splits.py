from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
META_PATH = PROJECT_ROOT / "data" / "synthetic_damage" / "metadata" / "metadata.csv"
LABEL_DIR = PROJECT_ROOT / "data" / "annotations" / "bbox_yolo"
IMAGE_DIR = PROJECT_ROOT / "data" / "synthetic_damage" / "masked_images"
SPLIT_DIR = PROJECT_ROOT / "data" / "splits"
MANIFEST_PATH = SPLIT_DIR / "split_manifest.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create train/val/test split manifests for synthetic damage data.")
    parser.add_argument("--train", type=float, default=0.7)
    parser.add_argument("--val", type=float, default=0.15)
    parser.add_argument("--test", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def load_rows() -> list[dict[str, str]]:
    if not META_PATH.exists():
        return []
    with META_PATH.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def assign_splits(source_images: list[str], train_ratio: float, val_ratio: float, seed: int) -> dict[str, str]:
    randomizer = random.Random(seed)
    shuffled = source_images[:]
    randomizer.shuffle(shuffled)
    total = len(shuffled)
    if total == 0:
        return {}

    train_count = max(1, int(round(total * train_ratio)))
    val_count = int(round(total * val_ratio))
    if total >= 3 and val_count == 0:
        val_count = 1
    if train_count + val_count > total:
        val_count = max(0, total - train_count)
    test_count = total - train_count - val_count
    if total >= 3 and test_count == 0 and train_count > 1:
        train_count -= 1
        test_count = 1

    train_end = train_count
    val_end = train_count + val_count

    mapping: dict[str, str] = {}
    for index, source_image in enumerate(shuffled):
        if index < train_end:
            mapping[source_image] = "train"
        elif index < val_end:
            mapping[source_image] = "val"
        else:
            mapping[source_image] = "test"
    return mapping


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["image_id", "source_image", "split", "damage_type", "mask_ratio", "image_path", "label_path"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    total_ratio = round(args.train + args.val + args.test, 6)
    if total_ratio != 1.0:
        raise SystemExit("Split ratios must sum to 1.0.")

    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    if not rows:
        raise SystemExit(f"No synthetic metadata found at {META_PATH}")

    source_images = sorted({row["source_image"] for row in rows})
    split_map = assign_splits(source_images, args.train, args.val, args.seed)

    manifest_rows: list[dict[str, str]] = []
    split_buckets = {"train": [], "val": [], "test": []}
    for row in rows:
        split = split_map[row["source_image"]]
        record = {
            "image_id": row["image_id"],
            "source_image": row["source_image"],
            "split": split,
            "damage_type": row["damage_type"],
            "mask_ratio": row["mask_ratio"],
            "image_path": (IMAGE_DIR / row["masked_image_file"]).relative_to(PROJECT_ROOT).as_posix(),
            "label_path": (LABEL_DIR / f"{row['image_id']}.txt").relative_to(PROJECT_ROOT).as_posix(),
        }
        manifest_rows.append(record)
        split_buckets[split].append(record)

    write_csv(MANIFEST_PATH, manifest_rows)
    for split, split_rows in split_buckets.items():
        write_csv(SPLIT_DIR / f"{split}.csv", split_rows)

    print(f"Split manifest saved to: {MANIFEST_PATH}")
    print(f"Train: {len(split_buckets['train'])}")
    print(f"Val: {len(split_buckets['val'])}")
    print(f"Test: {len(split_buckets['test'])}")


if __name__ == "__main__":
    main()
