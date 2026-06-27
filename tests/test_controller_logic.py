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


if __name__ == "__main__":
    unittest.main()
