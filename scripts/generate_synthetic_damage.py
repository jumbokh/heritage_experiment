from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data/raw/dunhuang_original/D1_intact"
OUTPUT_IMAGES = PROJECT_ROOT / "data/synthetic_damage/images"
OUTPUT_MASKS = PROJECT_ROOT / "data/synthetic_damage/masks"
OUTPUT_MASKED = PROJECT_ROOT / "data/synthetic_damage/masked_images"
OUTPUT_META = PROJECT_ROOT / "data/synthetic_damage/metadata/metadata.csv"

DAMAGE_TYPES = ("CRK", "PLS", "STN")
RATIOS = (0.05, 0.10, 0.20)
VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic defect data.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--limit", type=int, default=0, help="0 means no limit.")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def list_images(folder: Path) -> list[Path]:
    return sorted([p for p in folder.iterdir() if p.suffix.lower() in VALID_EXTENSIONS])


def clamp_point(x: int, y: int, width: int, height: int) -> tuple[int, int]:
    return max(0, min(x, width - 1)), max(0, min(y, height - 1))


def create_crack_mask(width: int, height: int, ratio: float, rng: random.Random) -> Image.Image:
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    target = int(width * height * ratio)
    covered = 0
    while covered < target:
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)
        points = [(x, y)]
        segments = rng.randint(8, 18)
        for _ in range(segments):
            x += rng.randint(-width // 12, width // 12)
            y += rng.randint(-height // 12, height // 12)
            points.append(clamp_point(x, y, width, height))
        line_width = max(1, int(min(width, height) * rng.uniform(0.002, 0.008)))
        draw.line(points, fill=255, width=line_width)
        covered = np.count_nonzero(np.array(mask))
    return mask


def create_pigment_loss_mask(width: int, height: int, ratio: float, rng: random.Random) -> Image.Image:
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    target = int(width * height * ratio)
    covered = 0
    while covered < target:
        cx = rng.randint(0, width - 1)
        cy = rng.randint(0, height - 1)
        rx = rng.randint(max(8, width // 30), max(16, width // 10))
        ry = rng.randint(max(8, height // 30), max(16, height // 10))
        vertices = []
        num_vertices = rng.randint(8, 14)
        for i in range(num_vertices):
            angle = 2 * np.pi * i / num_vertices
            dx = int(rx * rng.uniform(0.6, 1.2) * np.cos(angle))
            dy = int(ry * rng.uniform(0.6, 1.2) * np.sin(angle))
            vertices.append(clamp_point(cx + dx, cy + dy, width, height))
        draw.polygon(vertices, fill=255)
        covered = np.count_nonzero(np.array(mask))
    return mask


def create_stain_mask(width: int, height: int, ratio: float, rng: random.Random) -> Image.Image:
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    target = int(width * height * ratio)
    covered = 0
    while covered < target:
        cx = rng.randint(0, width - 1)
        cy = rng.randint(0, height - 1)
        radius = rng.randint(max(10, min(width, height) // 20), max(20, min(width, height) // 7))
        bbox = [
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
        ]
        draw.ellipse(bbox, fill=255)
        covered = np.count_nonzero(np.array(mask))
    return mask


def create_mask(width: int, height: int, damage_type: str, ratio: float, rng: random.Random) -> Image.Image:
    if damage_type == "CRK":
        return create_crack_mask(width, height, ratio, rng)
    if damage_type == "PLS":
        return create_pigment_loss_mask(width, height, ratio, rng)
    if damage_type == "STN":
        return create_stain_mask(width, height, ratio, rng)
    raise ValueError(f"Unsupported damage type: {damage_type}")


def apply_damage(image: Image.Image, mask: Image.Image, damage_type: str) -> Image.Image:
    base = np.array(image.convert("RGB")).astype(np.uint8)
    mask_np = np.array(mask) > 0
    damaged = base.copy()

    if damage_type == "CRK":
        damaged[mask_np] = np.clip(damaged[mask_np] * 0.25, 0, 255).astype(np.uint8)
    elif damage_type == "PLS":
        damaged[mask_np] = np.array([230, 225, 210], dtype=np.uint8)
    elif damage_type == "STN":
        stain_color = np.array([135, 105, 75], dtype=np.uint8)
        damaged[mask_np] = (
            damaged[mask_np].astype(np.float32) * 0.55 + stain_color.astype(np.float32) * 0.45
        ).astype(np.uint8)

    return Image.fromarray(damaged)


def normalize_image_id(index: int) -> str:
    return f"DH_SYN_{index:04d}"


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    for folder in (OUTPUT_IMAGES, OUTPUT_MASKS, OUTPUT_MASKED, OUTPUT_META.parent):
        folder.mkdir(parents=True, exist_ok=True)

    images = list_images(args.input)
    if args.limit > 0:
        images = images[: args.limit]

    if not images:
        print(f"No images found in: {args.input}")
        return

    rows = []
    image_counter = 1

    for source_path in images:
        source_img = Image.open(source_path).convert("RGB")
        width, height = source_img.size
        source_id = normalize_image_id(image_counter)

        for damage_type in DAMAGE_TYPES:
            for ratio in RATIOS:
                local_seed = rng.randint(0, 10_000_000)
                local_rng = random.Random(local_seed)
                mask = create_mask(width, height, damage_type, ratio, local_rng)
                masked = apply_damage(source_img, mask, damage_type)

                ratio_label = f"{int(ratio * 100):02d}"
                base_name = f"{source_id}_{damage_type}_{ratio_label}"
                clean_name = f"{base_name}_clean.png"
                mask_name = f"{base_name}_mask.png"
                damaged_name = f"{base_name}.png"

                source_img.save(OUTPUT_IMAGES / clean_name)
                mask.save(OUTPUT_MASKS / mask_name)
                masked.save(OUTPUT_MASKED / damaged_name)

                rows.append(
                    {
                        "image_id": base_name,
                        "source_image": source_path.name,
                        "damage_type": damage_type,
                        "mask_ratio": ratio,
                        "mask_file": mask_name,
                        "masked_image_file": damaged_name,
                        "seed": local_seed,
                    }
                )

        image_counter += 1

    with OUTPUT_META.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "image_id",
                "source_image",
                "damage_type",
                "mask_ratio",
                "mask_file",
                "masked_image_file",
                "seed",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Processed {len(images)} source images.")
    print(f"Generated {len(rows)} synthetic samples.")
    print(f"Metadata saved to: {OUTPUT_META}")


if __name__ == "__main__":
    main()
