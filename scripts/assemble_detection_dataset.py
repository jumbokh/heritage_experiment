from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPLIT_MANIFEST = PROJECT_ROOT / "data" / "splits" / "split_manifest.csv"
DATASET_ROOT = PROJECT_ROOT / "data" / "datasets" / "yolo_detection"
DATASET_MANIFEST = DATASET_ROOT / "dataset_manifest.csv"
DATASET_YAML = DATASET_ROOT / "dataset.yaml"
CLASS_NAMES = ["crack", "pigment_loss", "stain"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble YOLO detection dataset from split manifest.")
    parser.add_argument("--clean", action="store_true", help="Clean target dataset folders before copy.")
    return parser.parse_args()


def load_manifest() -> list[dict[str, str]]:
    if not SPLIT_MANIFEST.exists():
        return []
    with SPLIT_MANIFEST.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def prepare_dirs(clean: bool) -> None:
    for split in ("train", "val", "test"):
        for kind in ("images", "labels"):
            folder = DATASET_ROOT / kind / split
            folder.mkdir(parents=True, exist_ok=True)
            if clean:
                for item in folder.iterdir():
                    if item.is_file():
                        item.unlink()


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


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


def write_dataset_manifest(rows: list[dict[str, str]]) -> None:
    fieldnames = ["image_id", "split", "image_target", "label_target"]
    with DATASET_MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    manifest_rows = load_manifest()
    if not manifest_rows:
        raise SystemExit(f"Split manifest missing or empty: {SPLIT_MANIFEST}")

    prepare_dirs(args.clean)
    dataset_rows: list[dict[str, str]] = []

    for row in manifest_rows:
        split = row["split"]
        image_src = PROJECT_ROOT / Path(row["image_path"].replace("/", "\\"))
        label_src = PROJECT_ROOT / Path(row["label_path"].replace("/", "\\"))
        image_target = DATASET_ROOT / "images" / split / image_src.name
        label_target = DATASET_ROOT / "labels" / split / label_src.name

        if not image_src.exists():
            raise SystemExit(f"Missing image file: {image_src}")
        if not label_src.exists():
            raise SystemExit(f"Missing label file: {label_src}")

        copy_file(image_src, image_target)
        copy_file(label_src, label_target)

        dataset_rows.append(
            {
                "image_id": row["image_id"],
                "split": split,
                "image_target": image_target.relative_to(PROJECT_ROOT).as_posix(),
                "label_target": label_target.relative_to(PROJECT_ROOT).as_posix(),
            }
        )

    write_dataset_manifest(dataset_rows)
    write_dataset_yaml()
    print(f"Dataset assembled at: {DATASET_ROOT}")
    print(f"Samples copied: {len(dataset_rows)}")
    print(f"Dataset manifest: {DATASET_MANIFEST}")
    print(f"Dataset YAML: {DATASET_YAML}")


if __name__ == "__main__":
    main()
