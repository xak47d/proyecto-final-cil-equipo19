import importlib.util
import math
import unittest
from pathlib import Path

import numpy as np


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "controllers"
    / "cil_autonomous_driver"
    / "cil_autonomous_driver.py"
)
spec = importlib.util.spec_from_file_location("cil_controller", MODULE_PATH)
controller = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(controller)


class ControllerLogicTests(unittest.TestCase):
    def test_bus_recognition_excludes_bus_stop_street_furniture(self):
        class RecognitionObject:
            def __init__(self, model, distance):
                self.model = model
                self.distance = distance

            def getModel(self):
                return self.model

            def getPosition(self):
                return (self.distance, 0.0, 0.0)

            def getPositionOnImage(self):
                return (10, 10)

        class Camera:
            def getRecognitionObjects(self):
                return [
                    RecognitionObject("bus stop", 2.0),
                    RecognitionObject("BusSimple", 14.0),
                ]

            def getWidth(self):
                return 100

            def getHeight(self):
                return 100

        self.assertEqual(controller.closest_recognized(Camera(), "bus"), 14.0)

    def test_commands_are_three_valid_one_hot_vectors(self):
        for command in (0, 1, 2):
            encoded = controller.command_to_one_hot(command)
            self.assertEqual(encoded.shape, (1, 3))
            self.assertEqual(float(encoded.sum()), 1.0)
            self.assertEqual(float(encoded[0, command]), 1.0)
        with self.assertRaises(ValueError):
            controller.command_to_one_hot(3)

    def test_preprocess_shape_and_range(self):
        image = np.full((160, 320, 4), 128, dtype=np.uint8)
        processed = controller.preprocess_bgra(image)
        self.assertEqual(processed.shape, (1, 80, 160, 3))
        self.assertGreaterEqual(float(processed.min()), 0.0)
        self.assertLessEqual(float(processed.max()), 1.0)

    def test_adaptive_follow_thresholds(self):
        self.assertEqual(controller.adaptive_follow_speed(12.0), 0.0)
        self.assertEqual(controller.adaptive_follow_speed(8.0), 0.0)
        self.assertEqual(
            controller.adaptive_follow_speed(25.0),
            controller.EVALUATION_SPEED_KMH,
        )
        middle = controller.adaptive_follow_speed(18.5)
        self.assertAlmostEqual(middle, controller.EVALUATION_SPEED_KMH / 2, places=4)
        self.assertEqual(
            controller.adaptive_follow_speed(float("inf")),
            controller.EVALUATION_SPEED_KMH,
        )

    def test_adaptive_follow_resume_hysteresis(self):
        speed, stopped = controller.adaptive_follow_speed_hysteresis(12.0, False)
        self.assertEqual((speed, stopped), (0.0, True))
        speed, stopped = controller.adaptive_follow_speed_hysteresis(14.99, True)
        self.assertEqual((speed, stopped), (0.0, True))
        speed, stopped = controller.adaptive_follow_speed_hysteresis(15.0, True)
        self.assertFalse(stopped)
        self.assertGreater(speed, 0.0)

    def test_steering_rate_and_absolute_limit(self):
        limited = controller.limit_steering_step(1.0, 0.0)
        self.assertAlmostEqual(limited, controller.MAX_STEERING_STEP_RAD)
        current = 0.0
        for _ in range(100):
            current = controller.limit_steering_step(1.0, current)
        self.assertEqual(current, controller.MAX_STEERING_RAD)

    def test_wall_following_is_bounded(self):
        steering = controller.wall_following_steering(
            {"front": 1.2, "middle": 1.5, "rear": 1.8}
        )
        self.assertTrue(math.isfinite(steering))
        self.assertLessEqual(abs(steering), 0.42)

    def test_route_turn_guidance_and_destinations(self):
        assist, turning, completed, next_command = controller.route_turn_guidance(
            "left", -20.0, 48.0, 0.4, False, False
        )
        self.assertEqual(assist, -0.42)
        self.assertTrue(turning)
        self.assertFalse(completed)
        self.assertIsNone(next_command)
        assist, turning, completed, next_command = controller.route_turn_guidance(
            "left", -18.0, 51.0, 1.31, True, False
        )
        self.assertIsNone(assist)
        self.assertFalse(turning)
        self.assertTrue(completed)
        self.assertEqual(next_command, controller.STRAIGHT)
        self.assertTrue(controller.route_destination_reached("left", 39.6, 40.0))
        self.assertTrue(controller.route_destination_reached("right", 28.0, -68.0))
        self.assertTrue(controller.route_destination_reached("straight", -190.0, 236.0))
        self.assertIsNone(controller.route_heading_assist("right", -1.0, False))
        self.assertGreater(controller.route_heading_assist("straight", 0.2, False), 0.0)
        self.assertGreater(controller.route_heading_assist("right", -1.0, True), 0.0)
        self.assertLess(controller.route_heading_assist("left", 1.0, True), 0.0)
        self.assertGreater(
            controller.route_corridor_assist("straight", 0.0, 229.5, 0.0, False),
            0.0,
        )
        self.assertGreater(
            controller.route_corridor_assist("left", 0.0, 47.0, 1.57, True),
            0.0,
        )
        self.assertTrue(
            controller.route_signal_stop_required(
                "right", 40.0, -30.0, False, False, False
            )
        )
        self.assertFalse(
            controller.route_signal_stop_required(
                "right", 40.0, -30.0, False, False, True
            )
        )
        self.assertTrue(controller.right_signal_is_green(12.0))
        self.assertFalse(controller.right_signal_is_green(25.0))
        self.assertTrue(controller.right_signal_is_green(54.0))
        self.assertGreater(
            controller.route_approach_assist("right", 44.0, -20.0, 0.1, False, False),
            0.0,
        )
        self.assertLess(
            controller.route_approach_assist("right", 36.0, -20.0, -0.1, False, False),
            0.0,
        )
        self.assertIsNone(
            controller.route_approach_assist("right", 40.0, -60.0, 0.0, True, False)
        )


if __name__ == "__main__":
    unittest.main()
