import time

import rclpy
from rclpy.node import Node

from criticality_core.entity_manager import EntityManager


# ======================================================
# Scenario Configuration
# ======================================================

TREE_1 = {
    "model_file": "tree.sdf",
    "model_name": "tree_001",
    "x": -3.5,
    "y": -3.5,
    "z": -1.0,
}

BOX_1 = {
    "model_file": "critical_box.sdf",
    "model_name": "critical_box_001",
    "x": 2.0,
    "y": 0.0,
    "z": 0.5,
}

TREE_2 = {
    "model_file": "tree.sdf",
    "model_name": "tree_002",
    "x": 6.0,
    "y": -2.0,
    "z": -1.0,
}

STEP_DELAY = 5.0

# ======================================================


class ObstacleDemo(Node):

    def __init__(self):

        super().__init__("obstacle_demo")

        self.manager = EntityManager()

        self.run_demo()

        self.get_logger().info("Scenario completed.")

        rclpy.shutdown()

    # --------------------------------------------------

    def wait(self):

        time.sleep(STEP_DELAY)

    # --------------------------------------------------

    def run_demo(self):

        self.get_logger().info("Step 1: Spawn Tree 1")

        self.manager.spawn_model(**TREE_1)

        self.wait()

        # ----------------------------------------------

        self.get_logger().info("Step 2: Spawn Box")

        self.manager.spawn_model(**BOX_1)

        self.wait()

        # ----------------------------------------------

        self.get_logger().info("Step 3: Move Tree 1")

        self.manager.move_model(
            model_name="tree_001",
            x=5.0,
            y=5.0,
            z=-1.0,
        )

        self.wait()

        # ----------------------------------------------

        self.get_logger().info("Step 4: Remove Box")

        self.manager.remove_model(
            model_name="critical_box_001",
        )

        self.wait()

        # ----------------------------------------------

        self.get_logger().info("Step 5: Spawn Tree 2")

        self.manager.spawn_model(**TREE_2)


def main():

    rclpy.init()

    ObstacleDemo()


if __name__ == "__main__":
    main()
