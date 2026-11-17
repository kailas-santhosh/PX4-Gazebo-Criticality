import time

import rclpy
from rclpy.node import Node

from criticality_core.entity_manager import EntityManager


# ======================================================
# Configuration
# ======================================================

MODEL_NAME = "tree_001"

STARTUP_DELAY = 2.0

# ======================================================


class RemoveModel(Node):

    def __init__(self):

        super().__init__("remove_model")

        self.manager = EntityManager()

        self.get_logger().info(
            f"Removing {MODEL_NAME}..."
        )

        time.sleep(STARTUP_DELAY)

        self.manager.remove_model(
            model_name=MODEL_NAME,
        )

        self.get_logger().info("Done.")

        rclpy.shutdown()


def main():

    rclpy.init()

    RemoveModel()


if __name__ == "__main__":
    main()
