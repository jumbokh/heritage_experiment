from __future__ import annotations

import argparse
import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = PROJECT_ROOT / "data" / "raw" / "image_inventory.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "resized"
LABEL_DIR = PROJECT_ROOT / "data" / "annotations" / "bbox_yolo"
MANIFEST_PATH = PROJECT_ROOT / "data" / "annotations" / "real_ready" / "real_detection_manifest.csv"
REAL_GROUPS = {"D2", "MOBILE_SCREEN", "MOBILE_PRINT"}
CLASS_MAP = {"0": "CRK", "1": "PLS", "2": "STN"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and import real YOLO samples into the mixed-dataset manifest.")
    parser.add_argument("--include-groups", nargs="*", default=sorted(REAL_GROUPS))
    parser.add_argument("--only-ready", action="store_true", help="Write only rows with status=ready.")
    return parser.parse_args()


def load_inventory() -> list[dict[str, str]]:
    if not INVENTORY_PATH.exists():
        return []
    with INVENTORY_PATH.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def normalize_yolo_label(path: Path) -> tuple[list[str], str]:
    if not path.exists():
        return [], "missing_label"

    lines = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not lines:
        return [], "empty_label"

    normalized: list[str] = []
    for line in lines:
        parts = line.split()
        if len(parts) != 5:
            return [], "invalid_yolo_format"
        class_id = parts[0].lstrip("\ufeff")
        if class_id not in CLASS_MAP:
            return [], "unknown_class_id"
        try:
            coords = [float(value) for value in parts[1:]]
        except ValueError:
            return [], "non_numeric_label"
        if any(value < 0.0 or value > 1.0 for value in coords):
            return [], "out_of_range_label"
        normalized.append(
            f"{class_id} {coords[0]:.6f} {coords[1]:.6f} {coords[2]:.6f} {coords[3]:.6f}"
        )

    path.write_text("\n".join(normalized) + "\n", encoding="ascii")
    return normalized, "ready"


def infer_damage_type(label_path: Path) -> tuple[str, str]:
    lines, status = normalize_yolo_label(label_path)
    if status != "ready":
        return "", status
    class_ids: set[str] = set()
    for line in lines:
        parts = line.split()
        class_id = parts[0]
        class_ids.add(class_id)

    if len(class_ids) != 1:
        return "", "multi_class_per_image"
    only_class = next(iter(class_ids))
    return CLASS_MAP[only_class], "ready"


def build_rows(include_groups: set[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in load_inventory():
        group = row["group"]
        if group not in include_groups:
            continue

        image_id = row["image_id"]
        image_path = PROCESSED_DIR / f"{image_id}.png"
        label_path = LABEL_DIR / f"{image_id}.txt"
        damage_type, status = infer_damage_type(label_path)
        notes = ""
        if not image_path.exists():
            status = "missing_processed_image"
            notes = "Run preprocess_and_inventory.py first."
        elif status != "ready":
            notes = "Fix YOLO label before mixed-dataset assembly."

        rows.append(
            {
                "image_id": image_id,
                "source_image": row["file_name"],
                "group": group,
                "damage_type": damage_type,
                "image_path": image_path.relative_to(PROJECT_ROOT).as_posix() if image_path.exists() else "",
                "label_path": label_path.relative_to(PROJECT_ROOT).as_posix() if label_path.exists() else "",
                "status": status,
                "notes": notes,
            }
        )
    return rows


def write_manifest(rows: list[dict[str, str]]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["image_id", "source_image", "group", "damage_type", "image_path", "label_path", "status", "notes"]
    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    include_groups = set(args.include_groups)
    rows = build_rows(include_groups)
    output_rows = [row for row in rows if row["status"] == "ready"] if args.only_ready else rows
    write_manifest(output_rows)

    ready_count = sum(1 for row in rows if row["status"] == "ready")
    status_counts: dict[str, int] = {}
    group_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
        group_counts[row["group"]] = group_counts.get(row["group"], 0) + 1

    print(f"Real manifest saved to: {MANIFEST_PATH}")
    print(f"Rows scanned: {len(rows)}")
    print(f"Rows written: {len(output_rows)}")
    print(f"Ready rows: {ready_count}")
    for group_name in sorted(group_counts):
        print(f"Group {group_name}: {group_counts[group_name]}")
    for status_name in sorted(status_counts):
        print(f"Status {status_name}: {status_counts[status_name]}")


if __name__ == "__main__":
    main()
