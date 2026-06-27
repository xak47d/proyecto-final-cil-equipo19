#!/usr/bin/env python3
"""Normalize the recorded CIL dataset to the three evaluated commands.

The original recorder was created with four labels, where label 3 meant
"lane recovery". Recovery is not a navigation command in this project, so
those rows are archived locally and excluded from the public training set.
The script is idempotent and never deletes the excluded source images.
"""

from __future__ import annotations

import csv
import json
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset"
CSV_PATH = DATASET / "driving_log.csv"
IMAGES = DATASET / "images"
ARCHIVE = ROOT / "archive" / "four_command_source"
ARCHIVE_IMAGES = ARCHIVE / "recovery_images"
VALID_COMMANDS = {0, 1, 2}
HEADER = ["image", "steering_angle", "command"]


def read_rows(path: Path) -> tuple[list[list[str]], bool]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        raise ValueError(f"CSV vacio: {path}")
    has_header = rows[0] == HEADER
    return (rows[1:] if has_header else rows), has_header


def main() -> None:
    ARCHIVE_IMAGES.mkdir(parents=True, exist_ok=True)
    rows, had_header = read_rows(CSV_PATH)

    original_backup = ARCHIVE / "driving_log_original_4_commands.csv"
    if not original_backup.exists():
        ARCHIVE.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CSV_PATH, original_backup)

    kept: list[list[str]] = []
    excluded: list[list[str]] = []
    for row_number, row in enumerate(rows, start=1):
        if len(row) != 3:
            raise ValueError(f"Fila {row_number} invalida: {row!r}")
        image_name, steering_text, command_text = row
        float(steering_text)
        command = int(command_text)
        source = IMAGES / image_name
        archived = ARCHIVE_IMAGES / image_name
        if not source.exists() and not archived.exists():
            raise FileNotFoundError(f"Imagen faltante: {image_name}")
        if command in VALID_COMMANDS:
            kept.append([image_name, steering_text, str(command)])
        else:
            excluded.append([image_name, steering_text, str(command)])
            if source.exists() and not archived.exists():
                shutil.move(str(source), str(archived))

    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        writer.writerows(kept)

    excluded_csv = ARCHIVE / "driving_log_recovery_excluded.csv"
    with excluded_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        writer.writerows(excluded)

    image_names = {path.name for path in IMAGES.glob("*.png")}
    referenced = {row[0] for row in kept}
    missing = sorted(referenced - image_names)
    unreferenced = sorted(image_names - referenced)
    if missing or unreferenced:
        raise RuntimeError(
            f"Integridad fallida: missing={missing[:5]}, unreferenced={unreferenced[:5]}"
        )

    commands = Counter(int(row[2]) for row in kept)
    manifest = {
        "schema": HEADER,
        "commands": {"0": "STRAIGHT", "1": "LEFT", "2": "RIGHT"},
        "source_had_header": had_header,
        "records": len(kept),
        "images": len(image_names),
        "excluded_recovery_records": len(excluded),
        "command_counts": {str(key): commands[key] for key in sorted(commands)},
        "missing_images": 0,
        "unreferenced_images": 0,
    }
    (DATASET / "dataset_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
