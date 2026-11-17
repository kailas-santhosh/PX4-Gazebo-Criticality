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

from geometry_msgs.msg import PointStamped


class OffboardTakeoff(Node):

    def __init__(self):
        super().__init__("offboard_takeoff")

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # --------------------------------------------------
        # PX4 Publishers
        # --------------------------------------------------

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

        # --------------------------------------------------
        # PX4 Position Subscription
        # --------------------------------------------------

        self.pos_sub = self.create_subscription(
            VehicleLocalPosition,
            "/fmu/out/vehicle_local_position_v1",
            self.position_callback,
            qos,
        )

        # --------------------------------------------------
        # Navigation Target Subscription
        # --------------------------------------------------

        self.target_sub = self.create_subscription(
            PointStamped,
            "/navigation/target",
            self.target_callback,
            qos,
        )

        # --------------------------------------------------
        # State
        # --------------------------------------------------

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0

        self.current_target = None

        self.counter = 0

        self.offboard_requested = False
        self.arm_requested = False

        # --------------------------------------------------
        # Control Timer
        # --------------------------------------------------

        self.timer = self.create_timer(
            0.1,
            self.timer_callback,
        )

        self.get_logger().info(
            "Offboard controller initialized. "
            "Waiting for navigation target."
        )

    # --------------------------------------------------
    # Position Callback
    # --------------------------------------------------

    def position_callback(self, msg):

        self.current_x = msg.x
        self.current_y = msg.y
        self.current_z = msg.z

    # --------------------------------------------------
    # Navigation Target Callback
    # --------------------------------------------------

    def target_callback(self, msg):

        self.current_target = [
            msg.point.x,
            msg.point.y,
            msg.point.z,
        ]

    # --------------------------------------------------
    # Offboard Heartbeat
    # --------------------------------------------------

    def publish_offboard_mode(self):

        msg = OffboardControlMode()

        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        msg.thrust_and_torque = False
        msg.direct_actuator = False

        self.offboard_pub.publish(msg)

    # --------------------------------------------------
    # Trajectory Setpoint
    # --------------------------------------------------

    def publish_setpoint(self):

        if self.current_target is None:
            return

        msg = TrajectorySetpoint()

        msg.timestamp = int(
            self.get_clock().now().nanoseconds / 1000
        )

        msg.position = self.current_target
        msg.yaw = 0.0

        self.traj_pub.publish(msg)

    # --------------------------------------------------
    # Arm
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Offboard Mode
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Main Control Loop
    # --------------------------------------------------

    def timer_callback(self):

        # Continue publishing the Offboard heartbeat.
        self.publish_offboard_mode()

        # Do not start the arming/mode sequence until
        # a valid navigation target has arrived.

        if self.current_target is None:
            return

        # Stream the latest navigation target.
        self.publish_setpoint()

        # Preserve the existing startup timing:
        # 20 control cycles before Offboard request.
        # 25 control cycles before arm request.

        if self.counter == 20 and not self.offboard_requested:

            self.offboard()
            self.offboard_requested = True

        if self.counter == 25 and not self.arm_requested:

            self.arm()
            self.arm_requested = True

        self.counter += 1


def main():

    rclpy.init()

    node = OffboardTakeoff()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
