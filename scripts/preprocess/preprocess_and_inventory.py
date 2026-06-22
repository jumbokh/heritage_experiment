from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
INVENTORY_PATH = RAW_ROOT / "image_inventory.csv"
RESIZED_DIR = PROJECT_ROOT / "data" / "processed" / "resized"
GRAYSCALE_DIR = PROJECT_ROOT / "data" / "processed" / "grayscale"
EDGE_DIR = PROJECT_ROOT / "data" / "processed" / "edge_maps"
VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}

GROUP_SPECS = (
    ("D1", RAW_ROOT / "dunhuang_original" / "D1_intact", "dunhuang_open", "mural_fragment", "no"),
    ("D2", RAW_ROOT / "dunhuang_original" / "D2_real_defect", "dunhuang_open", "damaged_mural", "yes"),
    ("MOBILE_SCREEN", RAW_ROOT / "mobile_capture" / "screen_capture", "mobile_capture", "screen_reproduction", "unknown"),
    ("MOBILE_PRINT", RAW_ROOT / "mobile_capture" / "print_capture", "mobile_capture", "print_reproduction", "unknown"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess raw images and refresh inventory.")
    parser.add_argument("--max-size", type=int, default=1280, help="Longest side after resize.")
    return parser.parse_args()


def ensure_directories() -> None:
    for folder in (RESIZED_DIR, GRAYSCALE_DIR, EDGE_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def iter_images(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS)


def resize_with_aspect(image: Image.Image, max_size: int) -> Image.Image:
    resized = image.copy()
    resized.thumbnail((max_size, max_size))
    return resized


def normalize_name(group: str, source_path: Path, index: int) -> str:
    stem = source_path.stem.replace(" ", "_")
    return f"{group}_{index:04d}_{stem}"


def build_rows(max_size: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for group, folder, source, subject_type, has_real_defect in GROUP_SPECS:
        files = iter_images(folder)
        for index, file_path in enumerate(files, start=1):
            image = Image.open(file_path).convert("RGB")
            base_name = normalize_name(group, file_path, index)
            resized = resize_with_aspect(image, max_size)
            grayscale = ImageOps.grayscale(resized)
            edges = grayscale.filter(ImageFilter.FIND_EDGES)

            resized.save(RESIZED_DIR / f"{base_name}.png")
            grayscale.save(GRAYSCALE_DIR / f"{base_name}.png")
            edges.save(EDGE_DIR / f"{base_name}.png")

            width, height = resized.size
            rows.append(
                {
                    "image_id": base_name,
                    "group": group,
                    "source": source,
                    "subject_type": subject_type,
                    "has_real_defect": has_real_defect,
                    "width": str(width),
                    "height": str(height),
                    "file_name": file_path.name,
                    "relative_path": file_path.relative_to(PROJECT_ROOT).as_posix(),
                    "notes": "",
                }
            )
    return rows


def write_inventory(rows: list[dict[str, str]]) -> None:
    INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "image_id",
        "group",
        "source",
        "subject_type",
        "has_real_defect",
        "width",
        "height",
        "file_name",
        "relative_path",
        "notes",
    ]
    with INVENTORY_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parsed = parse_args()
    ensure_directories()
    rows = build_rows(parsed.max_size)
    write_inventory(rows)
    print(f"Inventory saved to: {INVENTORY_PATH}")
    print(f"Indexed {len(rows)} images.")
    print(f"Resized outputs: {RESIZED_DIR}")
    print(f"Grayscale outputs: {GRAYSCALE_DIR}")
    print(f"Edge maps: {EDGE_DIR}")


if __name__ == "__main__":
    main()
