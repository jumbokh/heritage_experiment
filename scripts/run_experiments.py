from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "results" / "logs"

STAGES = {
    "preprocess": [sys.executable, str(PROJECT_ROOT / "scripts" / "preprocess" / "preprocess_and_inventory.py")],
    "synth": [sys.executable, str(PROJECT_ROOT / "scripts" / "generate_synthetic_damage.py")],
    "yolo": [sys.executable, str(PROJECT_ROOT / "scripts" / "annotations" / "generate_yolo_templates.py")],
    "split": [sys.executable, str(PROJECT_ROOT / "scripts" / "preprocess" / "create_dataset_splits.py")],
    "assemble": [sys.executable, str(PROJECT_ROOT / "scripts" / "assemble_detection_dataset.py"), "--clean"],
    "import-real": [sys.executable, str(PROJECT_ROOT / "scripts" / "detection" / "import_real_yolo_samples.py")],
    "mix": [sys.executable, str(PROJECT_ROOT / "scripts" / "assemble_mixed_detection_dataset.py"), "--clean"],
    "validate": [sys.executable, str(PROJECT_ROOT / "scripts" / "validation" / "check_annotation_specs.py")],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run experiment stages from one entrypoint.")
    parser.add_argument(
        "--stage",
        choices=("preprocess", "synth", "yolo", "split", "assemble", "import-real", "mix", "validate", "all"),
        default="all",
    )
    parser.add_argument("--limit", type=int, default=0, help="Passed to the synth stage only.")
    return parser.parse_args()


def build_commands(stage: str, limit: int) -> list[tuple[str, list[str]]]:
    names = list(STAGES) if stage == "all" else [stage]
    commands: list[tuple[str, list[str]]] = []
    for name in names:
        cmd = list(STAGES[name])
        if name == "synth" and limit > 0:
            cmd.extend(["--limit", str(limit)])
        commands.append((name, cmd))
    return commands


def main() -> None:
    args = parse_args()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = LOG_DIR / f"runner_{timestamp}.log"

    commands = build_commands(args.stage, args.limit)
    with log_path.open("w", encoding="utf-8") as log_handle:
        for name, cmd in commands:
            header = f"=== Stage: {name} ==="
            print(header)
            log_handle.write(header + "\n")
            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.stdout:
                print(result.stdout.rstrip())
                log_handle.write(result.stdout)
                if not result.stdout.endswith("\n"):
                    log_handle.write("\n")
            if result.stderr:
                print(result.stderr.rstrip())
                log_handle.write(result.stderr)
                if not result.stderr.endswith("\n"):
                    log_handle.write("\n")
            if result.returncode != 0:
                raise SystemExit(f"Stage '{name}' failed with exit code {result.returncode}. See {log_path}")

    print(f"Runner log saved to: {log_path}")


if __name__ == "__main__":
    main()
