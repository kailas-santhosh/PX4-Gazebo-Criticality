import math
import sys
import os
import unittest

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from criticality_core.events.obstacle_event import ObstacleEvent


class TestObstacleCoordinates(unittest.TestCase):

    def setUp(self):

        self.vehicle_state = {
            "position": [10.0, 20.0, -3.0],
            "velocity": [1.0, 0.0, 0.0],
            "timestamp": 100.0,
            "current_timestamp": 100.1,
        }

        self.event = ObstacleEvent(
            trigger=None,
            model_file="critical_box.sdf",
            model_name="test_obstacle",
            x=None,
            y=None,
            z=None,
            vehicle_state_provider=lambda: self.vehicle_state,
            spawn_reference="direction_of_travel",
            forward=5.0,
            right=2.0,
            down=0.0,
        )

    def check_direction(self, velocity):

        self.vehicle_state["velocity"] = velocity

        return self.event.calculate_relative_spawn_position()

    def test_north(self):

        x, y, z = self.check_direction([1.0, 0.0, 0.0])

        self.assertAlmostEqual(x, 22.0)
        self.assertAlmostEqual(y, 15.0)
        self.assertAlmostEqual(z, 3.0)

    def test_east(self):

        x, y, z = self.check_direction([0.0, 1.0, 0.0])

        self.assertAlmostEqual(x, 25.0)
        self.assertAlmostEqual(y, 8.0)
        self.assertAlmostEqual(z, 3.0)

    def test_south(self):

        x, y, z = self.check_direction([-1.0, 0.0, 0.0])

        self.assertAlmostEqual(x, 18.0)
        self.assertAlmostEqual(y, 5.0)
        self.assertAlmostEqual(z, 3.0)

    def test_west(self):

        x, y, z = self.check_direction([0.0, -1.0, 0.0])

        self.assertAlmostEqual(x, 15.0)
        self.assertAlmostEqual(y, 12.0)
        self.assertAlmostEqual(z, 3.0)

    def test_stationary_drone(self):

        with self.assertRaises(RuntimeError):

            self.check_direction([0.0, 0.0, 0.0])

    def test_stale_vehicle_state(self):

        self.vehicle_state["timestamp"] = 99.0
        self.vehicle_state["current_timestamp"] = 100.0

        with self.assertRaises(RuntimeError):

            self.event.calculate_relative_spawn_position()

    def test_future_vehicle_timestamp(self):

        self.vehicle_state["timestamp"] = 101.0
        self.vehicle_state["current_timestamp"] = 100.0

        with self.assertRaises(RuntimeError):

            self.event.calculate_relative_spawn_position()

    def test_invalid_velocity(self):

        with self.assertRaises(ValueError):

            self.check_direction([float("nan"), 0.0, 0.0])


if __name__ == "__main__":

    unittest.main()
