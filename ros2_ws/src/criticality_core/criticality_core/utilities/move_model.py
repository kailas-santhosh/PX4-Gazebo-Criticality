import time

import rclpy
from rclpy.node import Node

from criticality_core.entity_manager import EntityManager


# ======================================================
# Configuration
# ======================================================

MODEL_NAME = "tree_001"

X = 5.0
Y = 5.0
Z = -1.0

STARTUP_DELAY = 2.0

# ======================================================


class MoveModel(Node):

    def __init__(self):

        super().__init__("move_model")

        self.manager = EntityManager()

        self.get_logger().info(
            f"Moving {MODEL_NAME}..."
        )

        time.sleep(STARTUP_DELAY)

        self.manager.move_model(
            model_name=MODEL_NAME,
            x=X,
            y=Y,
            z=Z,
        )

        self.get_logger().info("Done.")

        rclpy.shutdown()


def main():

    rclpy.init()

    MoveModel()


if __name__ == "__main__":
    main()
