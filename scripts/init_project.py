from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DIRECTORIES = [
    "data/raw/dunhuang_original/D1_intact",
    "data/raw/dunhuang_original/D2_real_defect",
    "data/raw/mobile_capture/screen_capture",
    "data/raw/mobile_capture/print_capture",
    "data/raw/mobile_capture/metadata",
    "data/processed/resized",
    "data/processed/registered",
    "data/processed/grayscale",
    "data/processed/edge_maps",
    "data/processed/texture_maps",
    "data/synthetic_damage/images",
    "data/synthetic_damage/masks",
    "data/synthetic_damage/masked_images",
    "data/synthetic_damage/metadata",
    "data/annotations/bbox_yolo",
    "data/annotations/mask_png",
    "data/annotations/labelme_json",
    "data/annotations/review_logs",
    "data/annotations/mask_png_refined",
    "data/annotations/real_ready",
    "data/splits",
    "data/datasets/yolo_detection/images/train",
    "data/datasets/yolo_detection/images/val",
    "data/datasets/yolo_detection/images/test",
    "data/datasets/yolo_detection/labels/train",
    "data/datasets/yolo_detection/labels/val",
    "data/datasets/yolo_detection/labels/test",
    "data/datasets/yolo_detection_mixed/images/train",
    "data/datasets/yolo_detection_mixed/images/val",
    "data/datasets/yolo_detection_mixed/images/test",
    "data/datasets/yolo_detection_mixed/labels/train",
    "data/datasets/yolo_detection_mixed/labels/val",
    "data/datasets/yolo_detection_mixed/labels/test",
    "experiments/exp01_registration",
    "experiments/exp02_detection",
    "experiments/exp02_detection/configs",
    "experiments/exp02_detection/runs",
    "experiments/exp03_segmentation",
    "experiments/exp04_mask_refinement",
    "experiments/exp05_inpainting",
    "experiments/exp06_reduced_order",
    "results/figures",
    "results/tables",
    "results/logs",
    "results/metrics_csv",
    "scripts/preprocess",
    "scripts/synth_damage",
    "scripts/annotations",
    "scripts/validation",
    "scripts/detection",
    "scripts/segmentation",
    "scripts/inpainting",
    "scripts/evaluation",
    "docs",
    "external",
]

CSV_TEMPLATES = {
    "data/raw/image_inventory.csv": (
        "image_id,group,source,subject_type,has_real_defect,width,height,file_name,relative_path,notes\n"
    ),
    "data/raw/mobile_capture/metadata/capture_log.csv": (
        "capture_id,source_image,mode,angle,light,distance,device,remarks\n"
    ),
    "data/annotations/review_logs/review_log.csv": (
        "image_id,mask_source,review_result,review_time_sec,notes\n"
    ),
    "data/annotations/real_ready/real_detection_manifest.csv": (
        "image_id,source_image,group,damage_type,image_path,label_path,status,notes\n"
    ),
    "data/splits/split_manifest.csv": (
        "image_id,source_image,split,damage_type,mask_ratio,image_path,label_path\n"
    ),
    "results/logs/annotation_report.csv": (
        "level,category,image_id,file_path,message\n"
    ),
    "results/metrics_csv/registration_metrics.csv": (
        "image_id,mse,ssim,feature_matches,notes\n"
    ),
    "results/metrics_csv/detection_metrics.csv": (
        "image_id,precision,recall,f1,map50,notes\n"
    ),
    "results/metrics_csv/segmentation_metrics.csv": (
        "image_id,dice,iou,boundary_f1,mask_area_error,notes\n"
    ),
    "results/metrics_csv/mask_refinement_metrics.csv": (
        "image_id,dice_before,dice_after,iou_before,iou_after,review_time_sec,review_result\n"
    ),
    "results/metrics_csv/inpainting_metrics.csv": (
        "image_id,method,psnr,ssim,mse,runtime_sec,notes\n"
    ),
    "results/metrics_csv/reduced_order_metrics.csv": (
        "image_id,dimension,runtime_sec,speedup,psnr,ssim,energy_retained,notes\n"
    ),
}

DOC_TEMPLATES = {
    "docs/annotation_guideline.md": "# Annotation Guideline\n\nFill in class-specific annotation notes here.\n",
    "docs/experiment_log.md": "# Experiment Log\n\nUse this file to record major experiment runs.\n",
    "docs/naming_rules.md": "# Naming Rules\n\nDocument final file naming decisions here.\n",
    "docs/yolov5_dataset_usage.md": "# YOLOv5 Dataset Usage\n\nFill in dataset preparation and training notes here.\n",
    "docs/real_synthetic_mixing_rules.md": "# Real and Synthetic Mixing Rules\n\nFill in mixing policy notes here.\n",
}


def ensure_file(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def main() -> None:
    for relative in DIRECTORIES:
        (PROJECT_ROOT / relative).mkdir(parents=True, exist_ok=True)

    for relative, content in CSV_TEMPLATES.items():
        ensure_file(PROJECT_ROOT / relative, content)

    for relative, content in DOC_TEMPLATES.items():
        ensure_file(PROJECT_ROOT / relative, content)

    print(f"Initialized project at: {PROJECT_ROOT}")
    print(f"Created {len(DIRECTORIES)} directories.")
    print(f"Prepared {len(CSV_TEMPLATES) + len(DOC_TEMPLATES)} template files.")


if __name__ == "__main__":
    main()
