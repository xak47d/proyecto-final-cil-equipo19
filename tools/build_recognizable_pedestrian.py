#!/usr/bin/env python3
"""Vendor Webots R2025a Pedestrian with Recognition and collision enabled."""

from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://raw.githubusercontent.com/cyberbotics/webots/R2025a/projects/humans/pedestrian/protos/"
source = urlopen(BASE + "Pedestrian.proto", timeout=30).read().decode("utf-8")
source = source.replace("PROTO Pedestrian [", "PROTO RecognizablePedestrian [")
source = source.replace(
    'EXTERNPROTO "',
    f'EXTERNPROTO "{BASE}',
)
source = source.replace(
    "field       SFBool     enableBoundingObject  FALSE",
    "field       SFBool     enableBoundingObject  TRUE",
)
output = ROOT / "protos" / "RecognizablePedestrian.proto"
output.write_text(source, encoding="utf-8")
print(output)

controller_url = (
    "https://raw.githubusercontent.com/cyberbotics/webots/R2025a/"
    "projects/humans/pedestrian/controllers/pedestrian/pedestrian.py"
)
controller_output = ROOT / "controllers" / "pedestrian" / "pedestrian.py"
controller_output.parent.mkdir(parents=True, exist_ok=True)
controller_output.write_bytes(urlopen(controller_url, timeout=30).read())
print(controller_output)
