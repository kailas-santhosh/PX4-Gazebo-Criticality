
import math
import re

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped

from criticality_core.entity_manager import EntityManager


class MovingTargetSimulator(Node):

    def __init__(self):

        super().__init__("moving_target_simulator")

        # --------------------------------------------------
        # Parameters
        # --------------------------------------------------

        self.declare_parameter("model_name", "moving_target")
        self.declare_parameter("radius", 5.0)
        self.declare_parameter("speed", 1.0)
        self.declare_parameter("center_x", 0.0)
        self.declare_parameter("center_y", 0.0)
        self.declare_parameter("ground_z", 0.25)
        self.declare_parameter("update_rate", 5.0)

        self.model_name = (
            self.get_parameter("model_name")
            .get_parameter_value()
            .string_value
        )

        self.radius = (
            self.get_parameter("radius").value
        )

        self.speed = (
            self.get_parameter("speed").value
        )

        self.center_x = (
            self.get_parameter("center_x").value
        )

        self.center_y = (
            self.get_parameter("center_y").value
        )

        self.ground_z = (
            self.get_parameter("ground_z").value
        )

        self.update_rate = (
            self.get_parameter("update_rate").value
        )

        if self.radius <= 0.0:
            raise ValueError("Target radius must be positive.")

        if self.speed <= 0.0:
            raise ValueError("Target speed must be positive.")

        if self.update_rate <= 0.0:
            raise ValueError("Update rate must be positive.")

        # --------------------------------------------------
        # Entity manager
        # --------------------------------------------------

        self.manager = EntityManager()

        self.spawned = False
        self.start_time = None

        # --------------------------------------------------
        # ROS publisher
        # --------------------------------------------------

        self.pose_pub = self.create_publisher(
            PoseStamped,
            "/navigation/moving_target/pose",
            10,
        )

        # --------------------------------------------------
        # Simulation timer
        # --------------------------------------------------

        self.timer = self.create_timer(
            1.0 / self.update_rate,
            self.update_target,
        )

        self.get_logger().info(
            "Moving target simulator initialized."
        )

        self.get_logger().info(
            f"Radius: {self.radius:.2f} m | "
            f"Speed: {self.speed:.2f} m/s | "
            f"Update rate: {self.update_rate:.1f} Hz"
        )

    # ------------------------------------------------------
    # Check Gazebo service response
    # ------------------------------------------------------

    @staticmethod
    def service_succeeded(result):

        if result.returncode != 0:
            return False

        return bool(
            re.search(
                r"\bdata:\s*true\b",
                result.stdout,
                re.IGNORECASE,
            )
        )

    # ------------------------------------------------------
    # Calculate circular position
    # ------------------------------------------------------

    def calculate_position(self, elapsed_time):

        angular_speed = self.speed / self.radius

        angle = angular_speed * elapsed_time

        x = (
            self.center_x
            + self.radius * math.cos(angle)
        )

        y = (
            self.center_y
            + self.radius * math.sin(angle)
        )

        z = self.ground_z

        return x, y, z

    # ------------------------------------------------------
    # Spawn target
    # ------------------------------------------------------

    def spawn_target(self, sim_time):

        x, y, z = self.calculate_position(0.0)

        self.get_logger().info(
            f"Spawning {self.model_name}..."
        )

        result = self.manager.spawn_model(
            model_file="moving_target.sdf",
            model_name=self.model_name,
            x=x,
            y=y,
            z=z,
        )

        if not self.service_succeeded(result):

            self.get_logger().error(
                "Failed to spawn moving target. "
                "Check Gazebo service output and model path."
            )

            return False

        self.spawned = True
        self.start_time = sim_time

        self.get_logger().info(
            f"Target spawned at ({x:.2f}, {y:.2f}, {z:.2f})."
        )

        self.publish_position(x, y, z)

        return True

    # ------------------------------------------------------
    # Publish target position
    # ------------------------------------------------------

    def publish_position(self, x, y, z):

        msg = PoseStamped()

        msg.header.stamp = (
            self.get_clock().now().to_msg()
        )

        msg.header.frame_id = "gazebo_world"

        msg.pose.position.x = float(x)
        msg.pose.position.y = float(y)
        msg.pose.position.z = float(z)

        msg.pose.orientation.w = 1.0

        self.pose_pub.publish(msg)

    # ------------------------------------------------------
    # Update target
    # ------------------------------------------------------

    def update_target(self):

        # Use simulation time, not wall-clock time.
        now = self.get_clock().now().nanoseconds / 1e9

        # Wait until the ROS clock receives simulation time.
        if now <= 0.0:
            return

        # Spawn only once.
        if not self.spawned:

            self.spawn_target(now)
            return

        elapsed_time = now - self.start_time

        x, y, z = self.calculate_position(
            elapsed_time
        )

        result = self.manager.move_model(
            model_name=self.model_name,
            x=x,
            y=y,
            z=z,
        )

        if not self.service_succeeded(result):

            self.get_logger().error(
                "Failed to update moving target pose."
            )

            return

        self.publish_position(x, y, z)


def main(args=None):

    rclpy.init(args=args)

    node = MovingTargetSimulator()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.get_logger().info(
            "Moving target simulator stopped."
        )

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()

