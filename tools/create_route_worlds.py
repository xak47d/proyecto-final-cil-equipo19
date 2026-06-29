#!/usr/bin/env python3
"""Create deterministic World 2 presets with route pose and tracking camera."""

from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "worlds" / "city_traffic_2025_02.wbt"
ROUTES = {
    "straight": {
        "translation": "52 236.4 0.4",
        "rotation": "0 0 1 3.14159",
        "description": "Torres residenciales del noreste a silos",
        "command": 0,
        "sumo_seed": 3,
        "traffic_start": 30.0,
        "camera_offset": (-24.0, -24.0, 24.0),
        "camera_rotation": "-0.2404644328450795 0.5805324950429454 0.7779195837203913 0.9785593071265875",
    },
    "right": {
        "translation": "39.6 25 0.4",
        "rotation": "0 0 1 -1.5708",
        "description": "Subway norte a iglesia",
        "command": 2,
        "sumo_seed": 1,
        # Preserve SUMO traffic while keeping the evidence turn clear; traffic
        # begins after the controlled stop and junction exit.
        "traffic_start": 70.0,
        "camera_offset": (-24.0, -24.0, 24.0),
        "camera_rotation": "-0.2404644328450795 0.5805324950429454 0.7779195837203913 0.9785593071265875",
    },
    "left": {
        "translation": "-50.4 120 0.4",
        "rotation": "0 0 1 -1.5708",
        "description": "Parque infantil a Subway norte",
        "command": 1,
        "sumo_seed": 7,
        "traffic_start": 25.0,
        "camera_offset": (24.0, -24.0, 24.0),
        "camera_rotation": "-0.2931397054911543 0.12142244168449097 0.948327846116487 2.3930066598587425",
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


def replace_tracking_viewpoint(text: str, translation: str) -> str:
    """Place a stable oblique camera above the ego car for a global tracking shot."""
    x, y, z = (float(value) for value in translation.split())
    position = f"{x - 24:g} {y - 24:g} {z + 24:g}"
    pattern = r"Viewpoint \{.*?\n\}"
    replacement = f"""Viewpoint {{
  fieldOfView 0.8
  orientation -0.2404644328450795 0.5805324950429454 0.7779195837203913 0.9785593071265875
  position {position}
  near 0.2
  follow \"vehicle\"
  followType \"Tracking Shot\"
  followSmoothness 0
  lensFlare LensFlare {{
  }}
}}"""
    result, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("No se encontro el Viewpoint del mundo")
    return result


def replace_evidence_camera_pose(
    text: str,
    translation: str,
    offset: tuple[float, float, float],
    rotation: str,
) -> str:
    x, y, z = (float(value) for value in translation.split())
    position = f"{x + offset[0]:g} {y + offset[1]:g} {z + offset[2]:g}"
    pattern = r"(DEF EVIDENCE_CAMERA Robot \{\n  translation )[^\n]+\n  rotation [^\n]+"
    replacement = rf"\g<1>{position}\n  rotation {rotation}"
    result, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise RuntimeError("No se encontro la camara global de evidencia")
    return result


def replace_sumo_seed(text: str, seed: int) -> str:
    pattern = r"(SumoInterface \{\n  gui FALSE\n  maxVehicles 30)(?:\n  seed \d+)?"
    result, count = re.subn(pattern, rf"\g<1>\n  seed {seed}", text, count=1)
    if count != 1:
        raise RuntimeError("No se encontro SumoInterface")
    return result


def select_route_traffic(route_file: Path, start_time: float, limit: int = 30) -> None:
    """Keep a bounded traffic window and avoid vehicles already blocking the route start."""
    text = route_file.read_text(encoding="utf-8")
    vehicle_pattern = re.compile(
        r'^    <vehicle id="[^"]+" depart="([0-9.]+)">\n.*?^    </vehicle>\n',
        flags=re.M | re.S,
    )
    selected = 0
    def keep_window(match: re.Match[str]) -> str:
        nonlocal selected
        if float(match.group(1)) >= start_time and selected < limit:
            selected += 1
            return match.group(0)
        return ""

    filtered = vehicle_pattern.sub(keep_window, text)
    if selected != limit:
        raise RuntimeError(
            f"Solo se encontraron {selected} vehiculos desde t={start_time}; se esperaban {limit}"
        )
    route_file.write_text(filtered, encoding="utf-8")


text = BASE.read_text(encoding="utf-8")
base_net = ROOT / "worlds" / "city_traffic_2025_02_net"
# Webots R2025a looks specifically for sumo.sumocfg; the teacher package used
# the nonstandard name sumo.sumocfg.xml, so provide the canonical alias.
shutil.copy2(base_net / "sumo.sumocfg.xml", base_net / "sumo.sumocfg")
for route, config in ROUTES.items():
    result = replace_ego_pose(text, config["translation"], config["rotation"])
    result = replace_tracking_viewpoint(result, config["translation"])
    result = replace_evidence_camera_pose(
        result,
        config["translation"],
        config["camera_offset"],
        config["camera_rotation"],
    )
    result = replace_sumo_seed(result, config["sumo_seed"])
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
    if config["traffic_start"] > 0:
        select_route_traffic(
            route_net / "sumo.rou.xml",
            config["traffic_start"],
        )
    print(output)
