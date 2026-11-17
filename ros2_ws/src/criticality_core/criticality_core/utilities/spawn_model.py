import time

import rclpy
from rclpy.node import Node

from criticality_core.entity_manager import EntityManager


# ======================================================
# Configuration
# ======================================================

MODEL_FILE = "tree.sdf"
MODEL_NAME = "tree_001"

X = -3.5
Y = -3.5
Z = -1.0

STARTUP_DELAY = 2.0

# ======================================================


class SpawnModel(Node):

    def __init__(self):

        super().__init__("spawn_model")

        self.manager = EntityManager()

        self.get_logger().info(
            f"Spawning {MODEL_NAME}..."
        )

        time.sleep(STARTUP_DELAY)

        self.manager.spawn_model(
            model_file=MODEL_FILE,
            model_name=MODEL_NAME,
            x=X,
            y=Y,
            z=Z,
        )

        self.get_logger().info("Done.")

        rclpy.shutdown()


def main():

    rclpy.init()

    SpawnModel()


if __name__ == "__main__":
    main()
