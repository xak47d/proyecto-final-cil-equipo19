#!/usr/bin/env python3
"""Vendor the Webots R2025a SUMO supervisor for reproducible diagnostics."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
WEBOTS_SOURCE = Path(
    "/Applications/Webots.app/Contents/projects/default/controllers/sumo_supervisor"
)
OUTPUT = ROOT / "controllers" / "sumo_supervisor"
OUTPUT.mkdir(parents=True, exist_ok=True)
for name in (
    "Objects.py",
    "SumoDisplay.py",
    "SumoSupervisor.py",
    "WebotsVehicle.py",
    "sumo_supervisor.py",
):
    shutil.copy2(WEBOTS_SOURCE / name, OUTPUT / name)
    print(OUTPUT / name)

entrypoint = OUTPUT / "sumo_supervisor.py"
text = entrypoint.read_text(encoding="utf-8")
text = text.replace(
    "FNULL = open(os.devnull, 'w')",
    "# Preserve SUMO diagnostics instead of discarding them.\nFNULL = None",
)
text = text.replace(
    "sumoProcess = subprocess.Popen(arguments, stdout=FNULL, stderr=subprocess.STDOUT)",
    "print('SUMO command: ' + ' '.join(arguments))\n"
    "sumoProcess = subprocess.Popen(arguments, stdout=FNULL, stderr=subprocess.STDOUT)",
)
entrypoint.write_text(text, encoding="utf-8")
