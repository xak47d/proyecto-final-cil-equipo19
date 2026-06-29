"""Camara global Full HD que mantiene el vehiculo autonomo en cuadro."""

from pathlib import Path
import os

from controller import Supervisor


CAMERA_CONFIGS = {
    "default": (
        (-24.0, -24.0, 24.0),
        (-0.2404644328450795, 0.5805324950429454, 0.7779195837203913, 0.9785593071265875),
    ),
    "left": (
        (24.0, -24.0, 24.0),
        (-0.2931397054911543, 0.12142244168449097, 0.948327846116487, 2.3930066598587425),
    ),
}


def main() -> None:
    supervisor = Supervisor()
    timestep = int(supervisor.getBasicTimeStep())
    frames_dir_value = os.environ.get("CIL_RECORD_FRAMES_DIR", "").strip()
    if not frames_dir_value:
        return
    camera = supervisor.getDevice("global_evidence_camera")
    camera.enable(timestep)

    ego = supervisor.getFromDef("WEBOTS_VEHICLE0")
    if ego is None:
        raise RuntimeError("No se encontro DEF WEBOTS_VEHICLE0")
    route = os.environ.get("CIL_ROUTE", "").strip().lower()
    camera_offset, camera_rotation = CAMERA_CONFIGS.get(route, CAMERA_CONFIGS["default"])
    self_node = supervisor.getSelf()
    translation = self_node.getField("translation")
    self_node.getField("rotation").setSFRotation(list(camera_rotation))
    frames_dir = Path(frames_dir_value)
    frames_dir.mkdir(parents=True, exist_ok=True)

    frame = 0
    step_count = 0
    while supervisor.step(timestep) != -1:
        x, y, z = ego.getPosition()
        translation.setSFVec3f(
            [x + camera_offset[0], y + camera_offset[1], z + camera_offset[2]]
        )
        # The world advances at 62.5 Hz.  Saving every second step gives a
        # direct 31.25 fps source and avoids writing thousands of frames that
        # ffmpeg would immediately discard for the 30 fps deliverable.
        if step_count % 2 == 0:
            camera.saveImage(str(frames_dir / f"frame_{frame:06d}.jpg"), 95)
            frame += 1
        step_count += 1


if __name__ == "__main__":
    main()
