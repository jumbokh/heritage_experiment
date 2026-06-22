from __future__ import annotations

import argparse
import csv
import random
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = PROJECT_ROOT / "data" / "raw" / "image_inventory.csv"
SYNTH_MANIFEST = PROJECT_ROOT / "data" / "splits" / "split_manifest.csv"
REAL_MANIFEST = PROJECT_ROOT / "data" / "annotations" / "real_ready" / "real_detection_manifest.csv"
LABEL_DIR = PROJECT_ROOT / "data" / "annotations" / "bbox_yolo"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "resized"
DATASET_ROOT = PROJECT_ROOT / "data" / "datasets" / "yolo_detection_mixed"
MANIFEST_PATH = DATASET_ROOT / "mixed_manifest.csv"
DATASET_YAML = DATASET_ROOT / "dataset.yaml"
CLASS_MAP = {"0": "CRK", "1": "PLS", "2": "STN"}
CLASS_NAMES = ["crack", "pigment_loss", "stain"]
REAL_GROUPS = {"D2", "MOBILE_SCREEN", "MOBILE_PRINT"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble a mixed real/synthetic YOLO detection dataset.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train", type=float, default=0.7)
    parser.add_argument("--val", type=float, default=0.15)
    parser.add_argument("--test", type=float, default=0.15)
    parser.add_argument("--synthetic-multiplier", type=int, default=3)
    parser.add_argument("--clean", action="store_true")
    return parser.parse_args()


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def assign_splits(keys: list[str], train_ratio: float, val_ratio: float, seed: int) -> dict[str, str]:
    randomizer = random.Random(seed)
    shuffled = keys[:]
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
    for index, key in enumerate(shuffled):
        if index < train_end:
            mapping[key] = "train"
        elif index < val_end:
            mapping[key] = "val"
        else:
            mapping[key] = "test"
    return mapping


def infer_damage_type(label_path: Path) -> str | None:
    if not label_path.exists():
        return None
    lines = [line.strip() for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return None
    class_id = lines[0].split()[0]
    return CLASS_MAP.get(class_id)


def collect_real_rows(seed: int, train_ratio: float, val_ratio: float) -> list[dict[str, str]]:
    manifest_rows = load_csv(REAL_MANIFEST)
    if manifest_rows:
        eligible = [
            {
                "image_id": row["image_id"],
                "source_image": row["source_image"],
                "damage_type": row["damage_type"],
                "image_path": row["image_path"],
                "label_path": row["label_path"],
            }
            for row in manifest_rows
            if row.get("status", "").lower() == "ready"
        ]
        split_map = assign_splits([row["image_id"] for row in eligible], train_ratio, val_ratio, seed)
        for row in eligible:
            row["split"] = split_map[row["image_id"]]
            row["domain"] = "real"
        return eligible

    inventory_rows = load_csv(INVENTORY_PATH)
    eligible: list[dict[str, str]] = []
    for row in inventory_rows:
        if row["group"] not in REAL_GROUPS:
            continue
        image_id = row["image_id"]
        image_path = PROCESSED_DIR / f"{image_id}.png"
        label_path = LABEL_DIR / f"{image_id}.txt"
        damage_type = infer_damage_type(label_path)
        if not image_path.exists() or not label_path.exists() or damage_type is None:
            continue
        eligible.append(
            {
                "image_id": image_id,
                "source_image": row["file_name"],
                "damage_type": damage_type,
                "image_path": image_path.relative_to(PROJECT_ROOT).as_posix(),
                "label_path": label_path.relative_to(PROJECT_ROOT).as_posix(),
            }
        )

    split_map = assign_splits([row["image_id"] for row in eligible], train_ratio, val_ratio, seed)
    for row in eligible:
        row["split"] = split_map[row["image_id"]]
        row["domain"] = "real"
    return eligible


def sample_synthetic_rows(rows: list[dict[str, str]], train_cap: int, seed: int) -> list[dict[str, str]]:
    if train_cap <= 0 or len(rows) <= train_cap:
        return rows

    randomizer = random.Random(seed)
    buckets: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        buckets.setdefault(row["damage_type"], []).append(row)

    sampled: list[dict[str, str]] = []
    ordered_types = sorted(buckets)
    while len(sampled) < train_cap and any(buckets.values()):
        for damage_type in ordered_types:
            bucket = buckets[damage_type]
            if not bucket:
                continue
            choice_index = randomizer.randrange(len(bucket))
            sampled.append(bucket.pop(choice_index))
            if len(sampled) >= train_cap:
                break
    return sampled


def collect_mixed_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    synth_rows = load_csv(SYNTH_MANIFEST)
    real_rows = collect_real_rows(args.seed, args.train, args.val)
    synth_by_split = {"train": [], "val": [], "test": []}
    for row in synth_rows:
        row = dict(row)
        row["domain"] = "synthetic"
        synth_by_split[row["split"]].append(row)

    real_train_count = sum(1 for row in real_rows if row["split"] == "train")
    if real_train_count > 0:
        train_cap = max(real_train_count * args.synthetic_multiplier, len(CLASS_NAMES))
        synth_by_split["train"] = sample_synthetic_rows(synth_by_split["train"], train_cap, args.seed)

    mixed_rows = []
    mixed_rows.extend(real_rows)
    mixed_rows.extend(synth_by_split["train"])

    real_has_val = any(row["split"] == "val" for row in real_rows)
    real_has_test = any(row["split"] == "test" for row in real_rows)
    mixed_rows.extend(row for row in synth_by_split["val"] if not real_has_val)
    mixed_rows.extend(row for row in synth_by_split["test"] if not real_has_test)

    for row in mixed_rows:
        row.setdefault("mask_ratio", "")
    return mixed_rows


def prepare_dataset_dirs(clean: bool) -> None:
    for split in ("train", "val", "test"):
        for kind in ("images", "labels"):
            folder = DATASET_ROOT / kind / split
            folder.mkdir(parents=True, exist_ok=True)
            if clean:
                for item in folder.iterdir():
                    if item.is_file():
                        item.unlink()
    if clean:
        # Remove stale YOLO cache artifacts at the labels root to avoid
        # Windows rename collisions when train.cache.npy is promoted.
        labels_root = DATASET_ROOT / "labels"
        for pattern in ("*.cache", "*.cache.npy"):
            for cache_file in labels_root.glob(pattern):
                if cache_file.is_file():
                    cache_file.unlink()


def copy_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    dataset_rows: list[dict[str, str]] = []
    for row in rows:
        split = row["split"]
        image_src = PROJECT_ROOT / Path(row["image_path"].replace("/", "\\"))
        label_src = PROJECT_ROOT / Path(row["label_path"].replace("/", "\\"))
        image_target = DATASET_ROOT / "images" / split / image_src.name
        label_target = DATASET_ROOT / "labels" / split / label_src.name
        if not image_src.exists() or not label_src.exists():
            continue
        shutil.copy2(image_src, image_target)
        shutil.copy2(label_src, label_target)
        dataset_rows.append(
            {
                "image_id": row["image_id"],
                "source_image": row["source_image"],
                "split": split,
                "damage_type": row["damage_type"],
                "mask_ratio": row.get("mask_ratio", ""),
                "domain": row["domain"],
                "image_target": image_target.relative_to(PROJECT_ROOT).as_posix(),
                "label_target": label_target.relative_to(PROJECT_ROOT).as_posix(),
            }
        )
    return dataset_rows


def write_manifest(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "image_id",
        "source_image",
        "split",
        "damage_type",
        "mask_ratio",
        "domain",
        "image_target",
        "label_target",
    ]
    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_dataset_yaml() -> None:
    lines = [
        f"path: {DATASET_ROOT.as_posix()}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "",
        "names:",
    ]
    for index, name in enumerate(CLASS_NAMES):
        lines.append(f"  {index}: {name}")
    DATASET_YAML.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    if round(args.train + args.val + args.test, 6) != 1.0:
        raise SystemExit("Split ratios must sum to 1.0.")

    prepare_dataset_dirs(args.clean)
    mixed_rows = collect_mixed_rows(args)
    dataset_rows = copy_rows(mixed_rows)
    write_manifest(dataset_rows)
    write_dataset_yaml()

    counts = {"train": 0, "val": 0, "test": 0, "real": 0, "synthetic": 0}
    for row in dataset_rows:
        counts[row["split"]] += 1
        counts[row["domain"]] += 1

    print(f"Mixed dataset assembled at: {DATASET_ROOT}")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Train: {counts['train']}")
    print(f"Val: {counts['val']}")
    print(f"Test: {counts['test']}")
    print(f"Real: {counts['real']}")
    print(f"Synthetic: {counts['synthetic']}")


if __name__ == "__main__":
    main()
