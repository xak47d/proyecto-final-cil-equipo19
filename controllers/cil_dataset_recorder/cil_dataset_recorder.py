"""Control manual y captura automatica del dataset CIL en World 1.

Comandos de navegacion:
    W -> STRAIGHT (0)
    A -> LEFT (1)
    D -> RIGHT (2)

Las flechas controlan el volante. La velocidad se conserva en 30 km/h, como
indica la actividad, y cada imagen se registra junto con el angulo de direccion
y el comando activo. Las rutas son relativas al proyecto para que el
controlador funcione en macOS, Windows o Linux sin editar el codigo.
"""

from __future__ import annotations

import csv
from pathlib import Path

from vehicle import Driver


STRAIGHT = 0
LEFT = 1
RIGHT = 2
COMMAND_NAMES = {STRAIGHT: "STRAIGHT", LEFT: "LEFT", RIGHT: "RIGHT"}

CRUISING_SPEED_KMH = 30.0
MAX_STEERING_RAD = 0.60
STEERING_STEP_RAD = 0.04
CAPTURE_PERIOD_MS = 100


def ensure_csv_header(csv_path: Path) -> None:
    """Create the log with the exact schema expected by the notebook."""
    if csv_path.exists() and csv_path.stat().st_size > 0:
        return
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerow(["image", "steering_angle", "command"])


def main() -> None:
    driver = Driver()
    timestep = int(driver.getBasicTimeStep())

    camera = driver.getDevice("camera")
    camera.enable(timestep)
    keyboard = driver.getKeyboard()
    keyboard.enable(timestep)

    project_root = Path(__file__).resolve().parents[2]
    images_dir = project_root / "dataset" / "images"
    csv_path = project_root / "dataset" / "driving_log.csv"
    images_dir.mkdir(parents=True, exist_ok=True)
    ensure_csv_header(csv_path)

    steering = 0.0
    command = STRAIGHT
    frame_index = 0
    elapsed_since_capture = CAPTURE_PERIOD_MS

    print("Captura CIL iniciada")
    print("Flechas: volante | W: recto | A: izquierda | D: derecha")
    print(f"Velocidad fija: {CRUISING_SPEED_KMH:.0f} km/h")

    while driver.step() != -1:
        key = keyboard.getKey()
        while key != -1:
            if key == keyboard.LEFT:
                steering -= STEERING_STEP_RAD
            elif key == keyboard.RIGHT:
                steering += STEERING_STEP_RAD
            elif key in (ord("W"), ord("w")):
                command = STRAIGHT
                print("COMANDO: STRAIGHT")
            elif key in (ord("A"), ord("a")):
                command = LEFT
                print("COMANDO: LEFT")
            elif key in (ord("D"), ord("d")):
                command = RIGHT
                print("COMANDO: RIGHT")
            key = keyboard.getKey()

        steering = max(-MAX_STEERING_RAD, min(MAX_STEERING_RAD, steering))
        steering *= 0.98  # retorno gradual del volante cuando se suelta la tecla
        driver.setCruisingSpeed(CRUISING_SPEED_KMH)
        driver.setSteeringAngle(steering)

        elapsed_since_capture += timestep
        if elapsed_since_capture < CAPTURE_PERIOD_MS:
            continue
        elapsed_since_capture = 0

        sim_ms = int(driver.getTime() * 1000)
        image_name = f"img_{sim_ms:010d}_{frame_index:06d}.png"
        image_path = images_dir / image_name
        camera.saveImage(str(image_path), 100)

        with csv_path.open("a", newline="", encoding="utf-8") as handle:
            csv.writer(handle).writerow(
                [image_name, f"{steering:.8f}", command]
            )

        if frame_index % 25 == 0:
            print(
                f"Captura {frame_index}: {image_name} | "
                f"steering={steering:.3f} | {COMMAND_NAMES[command]}"
            )
        frame_index += 1


if __name__ == "__main__":
    main()
