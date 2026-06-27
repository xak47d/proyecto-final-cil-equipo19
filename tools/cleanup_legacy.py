#!/usr/bin/env python3
"""Aparta artefactos obsoletos y conserva una unica fuente canonica."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "archive" / "legacy_artifacts"
DEST.mkdir(parents=True, exist_ok=True)

LEGACY = [
    ROOT / "cil_model.h5",
    ROOT / "controllers" / "cil_model.h5",
    ROOT / "model" / "cil_model.h5",
    ROOT / "notebook" / "entrenamiento_CIL.ipynb",
    ROOT / "controllers" / "cil_autonomous_driver" / "cil_model_best.h5",
]

for source in LEGACY:
    if source.exists():
        target = DEST / source.relative_to(ROOT).as_posix().replace("/", "__")
        if target.exists():
            target.unlink()
        shutil.move(str(source), str(target))
        print(f"Archivado: {source.relative_to(ROOT)}")
