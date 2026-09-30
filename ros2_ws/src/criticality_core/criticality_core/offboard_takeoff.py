import math

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    HistoryPolicy,
    DurabilityPolicy,
)

from px4_msgs.msg import (
    OffboardControlMode,
    TrajectorySetpoint,
    VehicleCommand,
    VehicleLocalPosition,
)


class OffboardTakeoff(Node):

    def __init__(self):
        super().__init__("offboard_takeoff")

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self.offboard_pub = self.create_publisher(
            OffboardControlMode,
            "/fmu/in/offboard_control_mode",
            qos,
        )

        self.traj_pub = self.create_publisher(
            TrajectorySetpoint,
            "/fmu/in/trajectory_setpoint",
            qos,
        )

        self.cmd_pub = self.create_publisher(
            VehicleCommand,
            "/fmu/in/vehicle_command",
            qos,
        )

        self.pos_sub = self.create_subscription(
            VehicleLocalPosition,
            "/fmu/out/vehicle_local_position_v1",
            self.position_callback,
            qos,
        )

        self.timer = self.create_timer(
            0.1,
            self.timer_callback,
        )

        self.counter = 0

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0

        # Square patrol route
        self.waypoints = [
            [0.0, 0.0, -3.0],
            [5.0, 0.0, -3.0],
            [5.0, 5.0, -3.0],
            [0.0, 5.0, -3.0],
            [0.0, 0.0, -3.0],
        ]

        self.current_wp = 0
        self.reached_last = False

    def position_callback(self, msg):


        self.get_logger().info(
            f"Position: {msg.x:.2f}, {msg.y:.2f}, {msg.z:.2f}"
        )

        self.current_x = msg.x
        self.current_y = msg.y
        self.current_z = msg.z

    def publish_offboard_mode(self):

        msg = OffboardControlMode()

        #msg.timestamp = int(
        #    self.get_clock().now().nanoseconds / 1000
        #)

        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        msg.thrust_and_torque = False
        msg.direct_actuator = False

        self.offboard_pub.publish(msg)

    def publish_setpoint(self):

        target = self.waypoints[self.current_wp]

        msg = TrajectorySetpoint()

        msg.timestamp = int(
            self.get_clock().now().nanoseconds / 1000
        )

        msg.position = target
        msg.yaw = 0.0

        self.get_logger().info(
            f"Publishing waypoint {self.current_wp}: {target}"
        )

        self.traj_pub.publish(msg)

        distance = math.sqrt(
            (self.current_x - target[0]) ** 2
            + (self.current_y - target[1]) ** 2
            + (self.current_z - target[2]) ** 2
        )

        if distance < 0.4 and not self.reached_last:

            self.get_logger().info(
                f"Reached waypoint {self.current_wp}"
            )

            self.reached_last = True

            if self.current_wp < len(self.waypoints) - 1:

                self.current_wp += 1

                self.get_logger().info(
                    f"Going to waypoint {self.current_wp}"
                )

        elif distance > 0.5:

            self.reached_last = False

    def arm(self):

        msg = VehicleCommand()

        msg.command = (
            VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM
        )

        msg.param1 = 1.0

        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1

        msg.from_external = True

        self.cmd_pub.publish(msg)

        self.get_logger().info("ARM command sent")

    def offboard(self):

        msg = VehicleCommand()

        msg.command = VehicleCommand.VEHICLE_CMD_DO_SET_MODE

        msg.param1 = 1.0
        msg.param2 = 6.0

        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1

        msg.from_external = True

        self.cmd_pub.publish(msg)

        self.get_logger().info("OFFBOARD command sent")

    def timer_callback(self):

        self.publish_offboard_mode()
        self.publish_setpoint()

        if self.counter == 20:
            self.offboard()

        if self.counter == 25:
            self.arm()

        self.counter += 1


def main():

    rclpy.init()

    node = OffboardTakeoff()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
