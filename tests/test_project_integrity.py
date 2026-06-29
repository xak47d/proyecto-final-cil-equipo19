import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProjectIntegrityTests(unittest.TestCase):
    def test_dataset_has_exact_schema_and_references(self):
        with (ROOT / "dataset" / "driving_log.csv").open(newline="") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(reader.fieldnames, ["image", "steering_angle", "command"])
            rows = list(reader)
        self.assertEqual(len(rows), 6129)
        self.assertEqual({int(row["command"]) for row in rows}, {0, 1, 2})
        images = {path.name for path in (ROOT / "dataset" / "images").glob("*.png")}
        self.assertEqual(images, {row["image"] for row in rows})

    def test_notebook_clones_public_repo_and_has_no_drive_mount(self):
        notebook = json.loads((ROOT / "Proyecto_Final_Equipo19.ipynb").read_text())
        source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])
        self.assertIn("git clone https://github.com/xak47d/proyecto-final-cil-equipo19.git", source)
        self.assertNotIn("drive.mount", source)
        self.assertIn("train_test_split", source)
        self.assertIn("source_id", source)

    def test_world_two_contains_required_sensors_and_limits(self):
        world = (ROOT / "worlds" / "city_traffic_2025_02.wbt").read_text()
        for token in (
            "maxVehicles 30",
            'name "front_radar"',
            "SickLms291",
            "recognition Recognition",
            'name "ds_right_front"',
            'name "ds_right_middle"',
            'name "ds_right_rear"',
            "RecognizablePedestrian",
            "fieldOfView 1\n      width 320\n      height 160",
            'followType "Tracking Shot"',
            "followSmoothness 0",
            "supervisor TRUE",
            'name "global_evidence_camera"',
            "width 1920\n      height 1080",
        ):
            self.assertIn(token, world)

    def test_three_route_presets_exist(self):
        for route in ("straight", "left", "right"):
            path = ROOT / "worlds" / f"city_traffic_2025_02_route_{route}.wbt"
            self.assertTrue(path.exists(), path)
            self.assertIn('controller "<extern>"', path.read_text())


if __name__ == "__main__":
    unittest.main()
