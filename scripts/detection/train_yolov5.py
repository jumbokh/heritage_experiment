from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SYNTH_DATASET = PROJECT_ROOT / "data" / "datasets" / "yolo_detection" / "dataset.yaml"
DEFAULT_MIXED_DATASET = PROJECT_ROOT / "data" / "datasets" / "yolo_detection_mixed" / "dataset.yaml"
DEFAULT_REPO = PROJECT_ROOT / "external" / "yolov5_official"
CONFIG_DIR = PROJECT_ROOT / "experiments" / "exp02_detection" / "configs"
RUNS_DIR = PROJECT_ROOT / "experiments" / "exp02_detection" / "runs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch or preview YOLOv5 training commands.")
    parser.add_argument("--dataset-type", choices=("synthetic", "mixed"), default="synthetic")
    parser.add_argument("--dataset", type=Path, default=None)
    parser.add_argument("--repo", type=Path, default=None)
    parser.add_argument("--python", dest="python_exe", type=Path, default=Path(sys.executable))
    parser.add_argument("--weights", default="yolov5n.pt")
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--name", default=None)
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def choose_dataset(args: argparse.Namespace) -> Path:
    if args.dataset is not None:
        return args.dataset
    if args.dataset_type == "mixed":
        return DEFAULT_MIXED_DATASET
    return DEFAULT_SYNTH_DATASET


def resolve_repo(repo_arg: Path | None) -> Path | None:
    candidates: list[Path] = []
    if repo_arg is not None:
        candidates.append(repo_arg)
    yolo_env = os.environ.get("YOLOV5_REPO")
    if yolo_env:
        candidates.append(Path(yolo_env))
    candidates.extend(
        [
            DEFAULT_REPO,
            PROJECT_ROOT / "yolov5",
            PROJECT_ROOT.parent / "yolov5",
            Path("D:/src/yolov5"),
        ]
    )
    for candidate in candidates:
        train_py = candidate / "train.py"
        if candidate.exists() and train_py.exists():
            return candidate
    return None


def load_dataset_yaml(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Dataset YAML not found: {path}")
    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in {"path", "train", "val", "test"}:
            data[key] = value
    return data


def count_split_images(dataset_root: Path, relative_folder: str) -> int:
    folder = dataset_root / relative_folder
    if not folder.exists():
        return 0
    return len([path for path in folder.iterdir() if path.is_file()])


def detect_torch(python_exe: Path) -> bool:
    result = subprocess.run(
        [str(python_exe), "-c", "import importlib.util as u; print(bool(u.find_spec('torch')))"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip().lower() == "true"


def build_command(repo: Path, dataset_yaml: Path, args: argparse.Namespace, run_name: str) -> list[str]:
    return [
        str(args.python_exe),
        str(repo / "train.py"),
        "--img",
        str(args.imgsz),
        "--batch",
        str(args.batch),
        "--epochs",
        str(args.epochs),
        "--data",
        str(dataset_yaml),
        "--weights",
        args.weights,
        "--project",
        str(RUNS_DIR),
        "--name",
        run_name,
        "--device",
        args.device,
        "--workers",
        str(args.workers),
    ]


def write_launch_note(command: list[str], dataset_yaml: Path, dataset_summary: dict[str, int], repo: Path | None, run_name: str, python_exe: Path, torch_ready: bool) -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    note_path = CONFIG_DIR / f"yolov5_launch_{timestamp}.md"
    repo_text = str(repo) if repo is not None else "NOT_FOUND"
    lines = [
        f"# YOLOv5 Launch Note",
        "",
        f"- run_name: `{run_name}`",
        f"- dataset_yaml: `{dataset_yaml}`",
        f"- repo: `{repo_text}`",
        f"- python: `{python_exe}`",
        f"- torch_ready: `{torch_ready}`",
        f"- train_images: `{dataset_summary['train']}`",
        f"- val_images: `{dataset_summary['val']}`",
        f"- test_images: `{dataset_summary['test']}`",
        "",
        "## Command",
        "",
        "```powershell",
        " ".join(command),
        "```",
        "",
    ]
    if dataset_summary["val"] == 0:
        lines.extend(
            [
                "## Warning",
                "",
                "- Validation split is empty. Add more source images before formal training.",
                "",
            ]
        )
    if not torch_ready:
        lines.extend(
            [
                "## Runtime Warning",
                "",
                "- The selected Python environment does not expose `torch`.",
                "- Install training dependencies before using `--execute`.",
                "",
            ]
        )
    note_path.write_text("\n".join(lines), encoding="utf-8")
    return note_path


def main() -> None:
    args = parse_args()
    dataset_yaml = choose_dataset(args)
    dataset_config = load_dataset_yaml(dataset_yaml)
    if "path" not in dataset_config:
        raise SystemExit(f"Dataset YAML missing required 'path' entry: {dataset_yaml}")
    dataset_root = Path(dataset_config["path"])
    dataset_summary = {
        "train": count_split_images(dataset_root, "images/train"),
        "val": count_split_images(dataset_root, "images/val"),
        "test": count_split_images(dataset_root, "images/test"),
    }
    if dataset_summary["train"] == 0:
        raise SystemExit("Training split is empty. Build the dataset before launching training.")

    repo = resolve_repo(args.repo)
    run_name = args.name or f"{args.dataset_type}_yolov5n_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    command = build_command(repo if repo is not None else Path("yolov5"), dataset_yaml, args, run_name)
    torch_ready = detect_torch(args.python_exe)
    note_path = write_launch_note(command, dataset_yaml, dataset_summary, repo, run_name, args.python_exe, torch_ready)

    print(f"Launch note saved to: {note_path}")
    print(f"Train images: {dataset_summary['train']}")
    print(f"Val images: {dataset_summary['val']}")
    print(f"Test images: {dataset_summary['test']}")
    print(f"Torch ready: {torch_ready}")

    if repo is None:
        print("YOLOv5 repo not found. Set --repo or YOLOV5_REPO before executing training.")
        return
    if not torch_ready:
        print("Selected Python environment does not provide torch. Install dependencies or choose another Python before executing training.")
        print("Training command:")
        print(" ".join(command))
        return

    print("Training command:")
    print(" ".join(command))
    if args.execute:
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(command, cwd=repo, check=False)
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
