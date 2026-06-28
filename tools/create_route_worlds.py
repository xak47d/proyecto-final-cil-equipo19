#!/usr/bin/env python3
"""Create deterministic World 2 route presets by changing only ego pose."""

from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "worlds" / "city_traffic_2025_02.wbt"
ROUTES = {
    "straight": {
        "translation": "40 236.4 0.4",
        "rotation": "0 0 1 3.14159",
        "description": "Torres residenciales del noreste a silos",
        "command": 0,
    },
    "right": {
        "translation": "39.6 25 0.4",
        "rotation": "0 0 1 -1.5708",
        "description": "Subway norte a iglesia",
        "command": 2,
    },
    "left": {
        "translation": "-50.4 120 0.4",
        "rotation": "0 0 1 -1.5708",
        "description": "Parque infantil a Subway norte",
        "command": 1,
    },
}


def replace_ego_pose(text: str, translation: str, rotation: str) -> str:
    pattern = r"(DEF WEBOTS_VEHICLE0 BmwX5 \{.*?\n)(.*?)(\n  controller \"<extern>\")"
    match = re.search(pattern, text, flags=re.S)
    if not match:
        raise RuntimeError("No se encontro el vehiculo autonomo")
    prefix, fields, suffix = match.groups()
    fields = re.sub(r"\n  translation [^\n]+", "", fields)
    fields = re.sub(r"\n  rotation [^\n]+", "", fields)
    pose = f"  translation {translation}\n  rotation {rotation}"
    return text[: match.start()] + prefix + pose + suffix + text[match.end() :]


text = BASE.read_text(encoding="utf-8")
base_net = ROOT / "worlds" / "city_traffic_2025_02_net"
# Webots R2025a looks specifically for sumo.sumocfg; the teacher package used
# the nonstandard name sumo.sumocfg.xml, so provide the canonical alias.
shutil.copy2(base_net / "sumo.sumocfg.xml", base_net / "sumo.sumocfg")
for route, config in ROUTES.items():
    result = replace_ego_pose(text, config["translation"], config["rotation"])
    if route == "right":
        # Coloca un cruce peatonal reproducible 15 m delante del inicio.
        result = result.replace(
            "translation 33.9653 -26.9963 1.27",
            "translation 39.6 10 1.27",
            1,
        ).replace(
            '"--trajectory=34 -27, 56 -27"',
            '"--trajectory=34 10, 56 10"\n    "--speed=2.0"\n    "--once"',
            1,
        )
    banner = (
        f"# Route preset: {route} | {config['description']} | "
        f"CIL_INITIAL_COMMAND={config['command']}\n"
    )
    output = ROOT / "worlds" / f"city_traffic_2025_02_route_{route}.wbt"
    output.write_text(result.replace("#VRML_SIM R2025a utf8\n", "#VRML_SIM R2025a utf8\n\n" + banner, 1), encoding="utf-8")
    source_net = ROOT / "worlds" / "city_traffic_2025_02_net"
    route_net = ROOT / "worlds" / f"city_traffic_2025_02_route_{route}_net"
    if route_net.exists():
        shutil.rmtree(route_net)
    shutil.copytree(source_net, route_net)
    print(output)
