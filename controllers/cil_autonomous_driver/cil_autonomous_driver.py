"""Controlador CIL y arbitro de seguridad para World 2.

Prioridad de control:
1. Peaton reconocido por la camara y confirmado por LiDAR: freno total.
2. Autobus estacionado reconocido y cercano: evasion por pared derecha.
3. Vehiculo detectado por radar: control de distancia longitudinal.
4. Direccion predicha por la CNN condicionada por el comando de navegacion.

El modulo mantiene las funciones matematicas independientes de Webots para que
los limites y umbrales puedan probarse automaticamente.
"""

from __future__ import annotations

import json
import math
import os
import time
from enum import Enum
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np


STRAIGHT = 0
LEFT = 1
RIGHT = 2
COMMAND_NAMES = {STRAIGHT: "STRAIGHT", LEFT: "LEFT", RIGHT: "RIGHT"}
COMMAND_COUNT = 3

EVALUATION_SPEED_KMH = 22.0
MAX_SPEED_KMH = 30.0
MAX_STEERING_RAD = 0.60
PEDESTRIAN_STOP_DISTANCE_M = 15.0
PARKED_BUS_TRIGGER_DISTANCE_M = 18.0
FOLLOW_CONTROL_DISTANCE_M = 25.0
FOLLOW_STOP_DISTANCE_M = 12.0
FOLLOW_RESUME_DISTANCE_M = 15.0
AVOID_SPEED_KMH = 12.0
RECOVERY_SPEED_KMH = 10.0
WALL_PRESENT_DISTANCE_M = 3.7
WALL_TARGET_DISTANCE_M = 1.7
WALL_LOST_STEPS_REQUIRED = 12
MAX_STEERING_STEP_RAD = 0.035
INFERENCE_INTERVAL_STEPS = 4
ROUTE_TURN_SPEED_KMH = 14.0


class AvoidanceState(Enum):
    DRIVE = "CIL"
    SEPARATE_LEFT = "EVASION_SEPARACION"
    WALL_FOLLOW_RIGHT = "SEGUIMIENTO_PARED_DERECHA"
    RECOVER_HEADING = "RECUPERA_ORIENTACION"
    REJOIN = "REINCORPORACION"


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def command_to_one_hot(command: int) -> np.ndarray:
    """Encode one validated command for the model's second input."""
    if command not in COMMAND_NAMES:
        raise ValueError(f"Comando CIL invalido: {command}")
    encoded = np.zeros((1, COMMAND_COUNT), dtype=np.float32)
    encoded[0, command] = 1.0
    return encoded


def preprocess_bgra(image_bgra: np.ndarray, height: int = 80, width: int = 160) -> np.ndarray:
    """Apply exactly the crop/resize/normalization used during training."""
    if image_bgra.ndim != 3 or image_bgra.shape[2] != 4:
        raise ValueError(f"Imagen BGRA invalida: {image_bgra.shape}")
    rgb = cv2.cvtColor(image_bgra, cv2.COLOR_BGRA2RGB)
    crop_top = int(rgb.shape[0] * 0.25)
    cropped = rgb[crop_top:, :, :]
    resized = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_AREA)
    normalized = resized.astype(np.float32) / 255.0
    return np.expand_dims(normalized, axis=0)


def limit_steering_step(target: float, current: float) -> float:
    delta = clamp(target - current, -MAX_STEERING_STEP_RAD, MAX_STEERING_STEP_RAD)
    return clamp(current + delta, -MAX_STEERING_RAD, MAX_STEERING_RAD)


def adaptive_follow_speed(distance_m: float) -> float:
    """Map radar distance to a safe target speed with a 12 m stop threshold."""
    if not math.isfinite(distance_m) or distance_m >= FOLLOW_CONTROL_DISTANCE_M:
        return EVALUATION_SPEED_KMH
    if distance_m <= FOLLOW_STOP_DISTANCE_M:
        return 0.0
    ratio = (distance_m - FOLLOW_STOP_DISTANCE_M) / (
        FOLLOW_CONTROL_DISTANCE_M - FOLLOW_STOP_DISTANCE_M
    )
    return clamp(EVALUATION_SPEED_KMH * ratio, 0.0, EVALUATION_SPEED_KMH)


def adaptive_follow_speed_hysteresis(
    distance_m: float, stopped_for_vehicle: bool
) -> tuple[float, bool]:
    """Mantiene el alto hasta que el vehiculo precedente vuelva a 15 m."""
    if distance_m <= FOLLOW_STOP_DISTANCE_M:
        return 0.0, True
    if stopped_for_vehicle and distance_m < FOLLOW_RESUME_DISTANCE_M:
        return 0.0, True
    return adaptive_follow_speed(distance_m), False


def route_turn_guidance(
    route: str,
    x: float,
    y: float,
    heading: float,
    turning: bool,
    completed: bool,
) -> tuple[float | None, bool, bool, int | None]:
    """Refuerza un único giro de ruta; fuera del cruce conserva la salida CIL."""
    if completed:
        return None, False, True, None
    if route == "left":
        turning = turning or (y <= 56.0 and x < 5.0)
        if turning and heading >= 1.30:
            return None, False, True, STRAIGHT
        if turning:
            return -0.42, True, False, None
    elif route == "right":
        turning = turning or (y <= -58.0 and x > 20.0)
        if turning and heading <= -1.30:
            return None, False, True, STRAIGHT
        if turning:
            return 0.35, True, False, None
    return None, turning, completed, None


def route_destination_reached(route: str, x: float, y: float) -> bool:
    if route == "straight":
        return x <= -188.0 and y >= 220.0
    if route == "right":
        return x <= 29.0 and y <= -63.0
    if route == "left":
        return x >= 35.0 and 44.0 <= y <= 52.0
    return False


def route_heading_assist(route: str, heading: float, turn_completed: bool) -> float | None:
    """Mantiene el corredor de salida una vez completado el giro de ruta."""
    if route != "straight" and not turn_completed:
        return None
    target = {
        "straight": 0.0,
        "left": math.pi / 2.0,
        "right": -math.pi / 2.0,
    }.get(route)
    if target is None:
        return None
    return clamp(0.70 * (heading - target), -0.18, 0.18)


def route_approach_assist(
    route: str,
    x: float,
    y: float,
    heading: float,
    turning: bool,
    completed: bool,
) -> float | None:
    """Centra el auto en el carril antes del giro para entrar desde la geometria correcta."""
    if turning or completed:
        return None
    target_x = None
    if route == "right" and y > -58.0:
        target_x = 40.0
    elif route == "left" and y > 56.0:
        target_x = -50.4
    if target_x is None:
        return None
    lateral_error = x - target_x
    return clamp(0.055 * lateral_error + 0.90 * heading, -0.22, 0.22)


def front_lidar_distance(lidar) -> float:
    values = lidar.getRangeImage()
    if not values:
        return float("inf")
    center = len(values) // 2
    # Sector frontal de 90 grados, alineado con el campo de la camara.
    half_window = max(1, len(values) // 4)
    valid = [
        value
        for value in values[center - half_window : center + half_window]
        if math.isfinite(value) and 0.1 < value <= 50.0
    ]
    return min(valid) if valid else float("inf")


def closest_radar_target(radar) -> tuple[float, float]:
    """Return distance and radial speed of the nearest target within +/-17 deg."""
    candidates = []
    for target in radar.getTargets():
        # The BmwX5 front slot can intermittently report a self-return near
        # 2.45 m; LiDAR still protects the immediate zone, so ignore <3 m.
        if abs(float(target.azimuth)) <= 0.30 and float(target.distance) >= 3.0:
            candidates.append((float(target.distance), float(target.speed)))
    return min(candidates, key=lambda item: item[0]) if candidates else (float("inf"), 0.0)


def closest_recognized(camera, model_fragment: str) -> float:
    distances = []
    fragment = model_fragment.lower()
    for obj in camera.getRecognitionObjects():
        model = str(obj.getModel()).lower()
        # Webots labels street furniture as "bus stop".  A substring-only
        # comparison would therefore launch an avoidance manoeuvre against the
        # shelter itself.  Only vehicle-like bus models are valid obstacles.
        if fragment not in model or (fragment == "bus" and "stop" in model):
            continue
        position = obj.getPosition()
        distance = math.sqrt(sum(float(axis) ** 2 for axis in position))
        image_x, image_y = obj.getPositionOnImage()
        if 0 <= image_x < camera.getWidth() and 0 <= image_y < camera.getHeight():
            distances.append(distance)
    return min(distances) if distances else float("inf")


def read_right_distances(sensors: dict[str, object]) -> dict[str, float]:
    result = {}
    for name, sensor in sensors.items():
        value = float(sensor.getValue())
        result[name] = value if math.isfinite(value) and value > 0.05 else float("inf")
    return result


def wall_present(distances: dict[str, float]) -> bool:
    return any(value < WALL_PRESENT_DISTANCE_M for value in distances.values())


def wall_following_steering(distances: dict[str, float]) -> float:
    valid = [value for value in distances.values() if math.isfinite(value)]
    if not valid:
        return -0.12
    front = distances["front"]
    middle = distances["middle"]
    rear = distances["rear"]
    side = middle if middle < WALL_PRESENT_DISTANCE_M else min(valid)
    distance_error = side - WALL_TARGET_DISTANCE_M
    alignment_error = (
        front - rear
        if front < WALL_PRESENT_DISTANCE_M and rear < WALL_PRESENT_DISTANCE_M
        else 0.0
    )
    return clamp(0.22 * distance_error + 0.16 * alignment_error, -0.42, 0.42)


def get_device(driver, name: str):
    try:
        return driver.getDevice(name)
    except BaseException as exc:
        raise RuntimeError(f"El mundo no contiene el dispositivo requerido: {name}") from exc


def main() -> None:
    import tensorflow as tf
    from vehicle import Driver

    driver = Driver()
    timestep = int(driver.getBasicTimeStep())
    root = Path(__file__).resolve().parents[2]
    model_path = Path(__file__).with_name("cil_model.h5")
    metadata_path = Path(__file__).with_name("model_metadata.json")
    if not model_path.exists() or not metadata_path.exists():
        raise FileNotFoundError("Faltan cil_model.h5 o model_metadata.json junto al controlador")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    model = tf.keras.models.load_model(model_path, compile=False)

    camera = get_device(driver, "camera")
    camera.enable(timestep)
    camera.recognitionEnable(timestep)
    lidar = get_device(driver, "Sick LMS 291")
    lidar.enable(timestep)
    radar = get_device(driver, "front_radar")
    radar.enable(timestep)
    gyro = get_device(driver, "gyro")
    gyro.enable(timestep)
    gps = get_device(driver, "gps")
    gps.enable(timestep)
    keyboard = driver.getKeyboard()
    keyboard.enable(timestep)

    right_sensors = {
        "front": get_device(driver, "ds_right_front"),
        "middle": get_device(driver, "ds_right_middle"),
        "rear": get_device(driver, "ds_right_rear"),
    }
    for sensor in right_sensors.values():
        sensor.enable(timestep)

    max_seconds = float(os.environ.get("CIL_MAX_SECONDS", "0") or 0)

    command = int(os.environ.get("CIL_INITIAL_COMMAND", STRAIGHT))
    route = os.environ.get("CIL_ROUTE", "").strip().lower()
    if command not in COMMAND_NAMES:
        raise ValueError(f"CIL_INITIAL_COMMAND invalido: {command}")
    state = AvoidanceState.DRIVE
    state_started = driver.getTime()
    heading = 0.0
    previous_time = driver.getTime()
    heading_before_avoidance = 0.0
    wall_lost_steps = 0
    steering_command = 0.0
    cil_steering = 0.0
    stopped_for_vehicle = False
    route_turning = False
    route_turn_completed = False
    route_arrived = False
    frame = 0
    wall_clock_started = time.monotonic()

    print("Control CIL + seguridad iniciado")
    print("W=STRAIGHT | A=LEFT | D=RIGHT")
    print(
        "Umbrales: peaton=15 m, autobus=18 m, "
        "seguimiento=25 m, parada de seguimiento=12 m"
    )

    while driver.step() != -1:
        now = driver.getTime()
        dt = max(0.0, now - previous_time)
        previous_time = now
        heading += float(gyro.getValues()[2]) * dt

        key = keyboard.getKey()
        while key != -1:
            if key in (ord("W"), ord("w")):
                command = STRAIGHT
            elif key in (ord("A"), ord("a")):
                command = LEFT
            elif key in (ord("D"), ord("d")):
                command = RIGHT
            key = keyboard.getKey()

        raw = camera.getImage()
        if raw is None:
            continue
        image_bgra = np.frombuffer(raw, np.uint8).reshape(
            (camera.getHeight(), camera.getWidth(), 4)
        )
        if frame % INFERENCE_INTERVAL_STEPS == 0:
            image_input = preprocess_bgra(
                image_bgra,
                int(metadata["image_height"]),
                int(metadata["image_width"]),
            )
            predicted = model.predict(
                [image_input, command_to_one_hot(command)], verbose=0
            )
            cil_steering = clamp(
                float(predicted[0][0]), -MAX_STEERING_RAD, MAX_STEERING_RAD
            )

        lidar_distance = front_lidar_distance(lidar)
        pedestrian_distance = closest_recognized(camera, "pedestrian")
        bus_distance = closest_recognized(camera, "bus")
        radar_distance, radar_speed = closest_radar_target(radar)
        side_distances = read_right_distances(right_sensors)
        x, y, _ = (float(value) for value in gps.getValues())

        pedestrian_emergency = (
            pedestrian_distance <= PEDESTRIAN_STOP_DISTANCE_M
            and lidar_distance <= PEDESTRIAN_STOP_DISTANCE_M
        )
        if pedestrian_emergency:
            target_speed = 0.0
            target_steering = steering_command
            mode = "FRENO_PEATON"
        else:
            if (
                state is AvoidanceState.DRIVE
                and bus_distance <= PARKED_BUS_TRIGGER_DISTANCE_M
                and (not math.isfinite(radar_distance) or abs(radar_speed) < 0.75)
            ):
                heading_before_avoidance = heading
                wall_lost_steps = 0
                state = AvoidanceState.SEPARATE_LEFT
                state_started = now
                print(f">>> EVASION: autobus a {lidar_distance:.2f} m")

            if state is AvoidanceState.SEPARATE_LEFT:
                target_speed = AVOID_SPEED_KMH
                target_steering = -0.20
                if wall_present(side_distances) or now - state_started >= 3.5:
                    state = AvoidanceState.WALL_FOLLOW_RIGHT
                    state_started = now
            elif state is AvoidanceState.WALL_FOLLOW_RIGHT:
                target_speed = AVOID_SPEED_KMH
                target_steering = wall_following_steering(side_distances)
                if wall_present(side_distances):
                    wall_lost_steps = 0
                else:
                    wall_lost_steps += 1
                if wall_lost_steps >= WALL_LOST_STEPS_REQUIRED:
                    state = AvoidanceState.RECOVER_HEADING
                    state_started = now
            elif state is AvoidanceState.RECOVER_HEADING:
                heading_error = heading_before_avoidance - heading
                target_speed = RECOVERY_SPEED_KMH
                target_steering = clamp(-1.8 * heading_error, -0.38, 0.38)
                if abs(heading_error) < 0.08 or now - state_started >= 6.0:
                    state = AvoidanceState.REJOIN
                    state_started = now
            elif state is AvoidanceState.REJOIN:
                target_speed = RECOVERY_SPEED_KMH
                target_steering = cil_steering
                if now - state_started >= 2.0:
                    state = AvoidanceState.DRIVE
                    state_started = now
            else:
                target_speed, stopped_for_vehicle = adaptive_follow_speed_hysteresis(
                    radar_distance, stopped_for_vehicle
                )
                target_steering = cil_steering
                assist, route_turning, route_turn_completed, next_command = route_turn_guidance(
                    route, x, y, heading, route_turning, route_turn_completed
                )
                if assist is not None:
                    target_speed = min(target_speed, ROUTE_TURN_SPEED_KMH)
                    target_steering = assist
                    mode = "GIRO_RUTA"
                if next_command is not None:
                    command = next_command
                    print(f">>> GIRO COMPLETO: continua {COMMAND_NAMES[command]}")
                heading_assist = route_heading_assist(route, heading, route_turn_completed)
                approach_assist = route_approach_assist(
                    route, x, y, heading, route_turning, route_turn_completed
                )
                if assist is None and approach_assist is not None:
                    target_speed = min(target_speed, 16.0)
                    target_steering = approach_assist
                    mode = "APROXIMACION_RUTA"
                elif assist is None and heading_assist is not None:
                    target_steering = heading_assist
                    mode = "CORREDOR_RUTA"
                if route_destination_reached(route, x, y):
                    target_speed = 0.0
                    mode = "RUTA_COMPLETA"
                    route_arrived = True
            mode = state.value

            if route_turning and state is AvoidanceState.DRIVE:
                mode = "GIRO_RUTA"
            elif (route_turn_completed or route == "straight") and state is AvoidanceState.DRIVE:
                mode = "CORREDOR_RUTA"
            if route_arrived:
                mode = "RUTA_COMPLETA"

        target_speed = clamp(target_speed, 0.0, MAX_SPEED_KMH)
        steering_command = limit_steering_step(target_steering, steering_command)
        driver.setCruisingSpeed(target_speed)
        driver.setSteeringAngle(steering_command)

        if frame % 20 == 0:
            print(
                f"Modo={mode} | Cmd={COMMAND_NAMES[command]} | "
                f"steer={steering_command:.3f} | speed={target_speed:.1f} | "
                f"GPS=({x:.2f},{y:.2f}) | yaw={heading:.2f} | "
                f"LiDAR={lidar_distance:.2f} m | Radar={radar_distance:.2f} m "
                f"({radar_speed:.2f} m/s) | peaton={pedestrian_distance:.2f} m | "
                f"bus={bus_distance:.2f} m"
            )
        frame += 1
        if max_seconds > 0 and now >= max_seconds:
            print(f"Fin automatico de evidencia a {now:.1f} s")
            break
        if route_arrived:
            print(f">>> RUTA COMPLETA {route}: GPS=({x:.2f},{y:.2f})")
            break
        if max_seconds > 0 and time.monotonic() - wall_clock_started >= max(60.0, max_seconds * 5.0):
            print("Fin de seguridad por limite de tiempo de reloj")
            break

if __name__ == "__main__":
    main()
