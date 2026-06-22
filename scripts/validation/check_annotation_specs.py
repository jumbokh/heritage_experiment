from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = PROJECT_ROOT / "data" / "raw" / "image_inventory.csv"
BBOX_DIR = PROJECT_ROOT / "data" / "annotations" / "bbox_yolo"
MASK_DIR = PROJECT_ROOT / "data" / "annotations" / "mask_png"
LABELME_DIR = PROJECT_ROOT / "data" / "annotations" / "labelme_json"
REPORT_PATH = PROJECT_ROOT / "results" / "logs" / "annotation_report.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate annotation files against raw inventory.")
    return parser.parse_args()


def load_inventory() -> list[dict[str, str]]:
    if not INVENTORY_PATH.exists():
        return []
    with INVENTORY_PATH.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def add_issue(issues: list[dict[str, str]], level: str, category: str, image_id: str, file_path: Path, message: str) -> None:
    issues.append(
        {
            "level": level,
            "category": category,
            "image_id": image_id,
            "file_path": file_path.relative_to(PROJECT_ROOT).as_posix() if file_path.exists() else file_path.as_posix(),
            "message": message,
        }
    )


def validate_yolo(path: Path, image_id: str, issues: list[dict[str, str]]) -> None:
    if not path.exists():
        add_issue(issues, "warning", "bbox_yolo", image_id, path, "Missing YOLO annotation file.")
        return

    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        add_issue(issues, "warning", "bbox_yolo", image_id, path, "YOLO annotation file is empty.")
        return

    for line_no, line in enumerate(lines, start=1):
        parts = line.split()
        if len(parts) != 5:
            add_issue(issues, "error", "bbox_yolo", image_id, path, f"Line {line_no} must contain 5 tokens.")
            continue
        try:
            class_id = int(parts[0])
            coords = [float(value) for value in parts[1:]]
        except ValueError:
            add_issue(issues, "error", "bbox_yolo", image_id, path, f"Line {line_no} contains non-numeric values.")
            continue

        if class_id < 0:
            add_issue(issues, "error", "bbox_yolo", image_id, path, f"Line {line_no} has negative class id.")
        if any(value < 0.0 or value > 1.0 for value in coords):
            add_issue(issues, "error", "bbox_yolo", image_id, path, f"Line {line_no} has coordinates outside [0, 1].")


def validate_mask(path: Path, image_path: Path, image_id: str, issues: list[dict[str, str]]) -> None:
    if not path.exists():
        add_issue(issues, "warning", "mask_png", image_id, path, "Missing mask PNG file.")
        return
    if not image_path.exists():
        add_issue(issues, "warning", "mask_png", image_id, image_path, "Source image path from inventory is missing.")
        return

    mask = Image.open(path)
    image = Image.open(image_path)
    if mask.size != image.size:
        add_issue(issues, "error", "mask_png", image_id, path, "Mask size does not match source image size.")

    unique_values = set(mask.convert("L").getdata())
    if not unique_values.issubset({0, 255}):
        add_issue(issues, "warning", "mask_png", image_id, path, "Mask is not strictly binary (0/255).")


def validate_labelme(path: Path, image_id: str, issues: list[dict[str, str]]) -> None:
    if not path.exists():
        add_issue(issues, "warning", "labelme_json", image_id, path, "Missing LabelMe JSON file.")
        return

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        add_issue(issues, "error", "labelme_json", image_id, path, "Invalid JSON format.")
        return

    shapes = payload.get("shapes")
    if not isinstance(shapes, list) or not shapes:
        add_issue(issues, "warning", "labelme_json", image_id, path, "LabelMe JSON does not contain shapes.")


def write_report(issues: list[dict[str, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["level", "category", "image_id", "file_path", "message"],
        )
        writer.writeheader()
        writer.writerows(issues)


def main() -> None:
    _ = parse_args()
    inventory_rows = load_inventory()
    issues: list[dict[str, str]] = []

    if not inventory_rows:
        add_issue(issues, "warning", "inventory", "", INVENTORY_PATH, "Inventory is missing or empty.")

    for row in inventory_rows:
        image_id = row["image_id"]
        relative_path = row["relative_path"]
        image_path = PROJECT_ROOT / Path(relative_path.replace("/", "\\"))
        validate_yolo(BBOX_DIR / f"{image_id}.txt", image_id, issues)
        validate_mask(MASK_DIR / f"{image_id}.png", image_path, image_id, issues)
        validate_labelme(LABELME_DIR / f"{image_id}.json", image_id, issues)

    write_report(issues)
    error_count = sum(1 for issue in issues if issue["level"] == "error")
    warning_count = sum(1 for issue in issues if issue["level"] == "warning")
    print(f"Annotation report saved to: {REPORT_PATH}")
    print(f"Checked {len(inventory_rows)} inventory rows.")
    print(f"Warnings: {warning_count}")
    print(f"Errors: {error_count}")


if __name__ == "__main__":
    main()
