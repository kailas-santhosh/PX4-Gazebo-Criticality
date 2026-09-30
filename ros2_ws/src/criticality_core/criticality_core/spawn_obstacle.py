import subprocess
import time

import rclpy
from rclpy.node import Node


MODEL_PATH = "/workspace/ros2_ws/src/criticality_core/models/critical_box.sdf"


class SpawnObstacle(Node):

    def __init__(self):

        super().__init__("spawn_obstacle")

        self.get_logger().info(
            "Waiting 12 seconds before spawning obstacle..."
        )

        time.sleep(12)

        self.spawn()

        self.get_logger().info("Done.")

        rclpy.shutdown()

    def spawn(self):

        cmd = [
            "gz",
            "service",
            "-s",
            "/world/default/create",
            "--reqtype",
            "gz.msgs.EntityFactory",
            "--reptype",
            "gz.msgs.Boolean",
            "--timeout",
            "3000",
            "--req",
            f'sdf_filename: "{MODEL_PATH}"'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        print(result.stdout)
        print(result.stderr)


def main():

    rclpy.init()

    SpawnObstacle()


if __name__ == "__main__":
    main()
