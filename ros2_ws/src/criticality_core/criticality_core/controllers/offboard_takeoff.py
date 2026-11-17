
import math
import time

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
    VehicleCommandAck,
    VehicleLocalPosition,
    VehicleLandDetected,
    VehicleStatus,
)

from geometry_msgs.msg import PointStamped
from std_msgs.msg import Bool


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
        # PX4 Subscriptions
        # --------------------------------------------------

        self.pos_sub = self.create_subscription(
            VehicleLocalPosition,
            "/fmu/out/vehicle_local_position_v1",
            self.position_callback,
            qos,
        )

        self.ack_sub = self.create_subscription(
            VehicleCommandAck,
            "/fmu/out/vehicle_command_ack",
            self.command_ack_callback,
            qos,
        )

        self.land_sub = self.create_subscription(
            VehicleLandDetected,
            "/fmu/out/vehicle_land_detected",
            self.land_detected_callback,
            qos,
        )

        self.status_sub = self.create_subscription(
            VehicleStatus,
            "/fmu/out/vehicle_status_v1",
            self.vehicle_status_callback,
            qos,
        )

        # --------------------------------------------------
        # Navigation Subscriptions
        # --------------------------------------------------

        self.target_sub = self.create_subscription(
            PointStamped,
            "/navigation/target",
            self.target_callback,
            qos,
        )

        self.mission_complete_sub = self.create_subscription(
            Bool,
            "/navigation/mission_complete",
            self.mission_complete_callback,
            qos,
        )

        # --------------------------------------------------
        # Vehicle State
        # --------------------------------------------------

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        self.current_heading = 0.0
        self.position_valid = False

        self.current_target = None

        # --------------------------------------------------
        # Yaw Control
        # --------------------------------------------------

        self.current_yaw_setpoint = None
        self.yaw_rate_limit = 0.5
        self.yaw_distance_threshold = 0.25
        self.last_yaw_update_time = time.monotonic()

        # --------------------------------------------------
        # Startup State
        # --------------------------------------------------

        self.counter = 0
        self.offboard_requested = False
        self.arm_requested = False

        # --------------------------------------------------
        # Landing State
        # --------------------------------------------------

        self.landing_requested = False
        self.landing_acknowledged = False
        self.landing_failed = False

        self.landed = False
        self.landed_since = None
        self.landed_confirmation_seconds = 1.5

        self.disarm_requested = False
        self.disarm_acknowledged = False
        self.disarm_failed = False
        self.disarmed_confirmed = False

        self.vehicle_status_received = False
        self.vehicle_nav_state = None
        self.vehicle_arming_state = None

        self.offboard_heartbeat_active = True

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
        self.current_heading = msg.heading

        self.position_valid = bool(
            msg.xy_valid and msg.z_valid
        )

    # --------------------------------------------------
    # Navigation Target Callback
    # --------------------------------------------------

    def target_callback(self, msg):

        if self.landing_requested:
            return

        self.current_target = [
            msg.point.x,
            msg.point.y,
            msg.point.z,
        ]

    # --------------------------------------------------
    # Mission Completion Callback
    # --------------------------------------------------

    def mission_complete_callback(self, msg):

        if not msg.data:
            return

        if self.landing_requested:
            return

        self.landing_requested = True

        self.get_logger().info(
            "Mission completion received. "
            "Requesting PX4 landing."
        )

        self.send_landing_command()

    # --------------------------------------------------
    # PX4 Vehicle Status Callback
    # --------------------------------------------------

    def vehicle_status_callback(self, msg):

        self.vehicle_status_received = True
        self.vehicle_nav_state = msg.nav_state
        self.vehicle_arming_state = msg.arming_state

        if (
            self.landing_requested
            and self.vehicle_nav_state
            != VehicleStatus.NAVIGATION_STATE_OFFBOARD
            and self.offboard_heartbeat_active
        ):

            self.offboard_heartbeat_active = False

            self.get_logger().info(
                "PX4 has exited Offboard mode."
            )

        if (
            self.disarm_acknowledged
            and self.vehicle_arming_state
            == VehicleStatus.ARMING_STATE_DISARMED
            and not self.disarmed_confirmed
        ):

            self.disarmed_confirmed = True

            self.get_logger().info(
                "DISARM CONFIRMED. Mission finished."
            )

    # --------------------------------------------------
    # Landing Detection Callback
    # --------------------------------------------------

    def land_detected_callback(self, msg):

        self.landed = bool(msg.landed)

        if self.landed:

            if self.landed_since is None:
                self.landed_since = time.monotonic()

        else:
            self.landed_since = None

    # --------------------------------------------------
    # PX4 Command Acknowledgement Callback
    # --------------------------------------------------

    def command_ack_callback(self, msg):

        accepted = (
            msg.result
            == VehicleCommandAck.VEHICLE_CMD_RESULT_ACCEPTED
        )

        # Landing command acknowledgement.
        if (
            msg.command == VehicleCommand.VEHICLE_CMD_NAV_LAND
            and self.landing_requested
            and not self.landing_acknowledged
            and not self.landing_failed
        ):

            if accepted:

                self.landing_acknowledged = True

                self.get_logger().info(
                    "PX4 accepted landing command."
                )

            else:

                self.landing_failed = True

                self.get_logger().error(
                    f"PX4 rejected landing command. "
                    f"ACK result: {msg.result}. "
                    "Automatic disarming is disabled."
                )

        # Disarm command acknowledgement.
        if (
            msg.command
            == VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM
            and self.disarm_requested
            and not self.disarm_acknowledged
            and not self.disarm_failed
        ):

            if accepted:

                self.disarm_acknowledged = True

                self.get_logger().info(
                    "PX4 accepted disarm command. "
                    "Waiting for disarmed status."
                )

            else:

                self.disarm_failed = True

                self.get_logger().error(
                    f"PX4 rejected disarm command. "
                    f"ACK result: {msg.result}."
                )

    # --------------------------------------------------
    # PX4 Command Publisher
    # --------------------------------------------------

    def publish_vehicle_command(
        self,
        command,
        param1=0.0,
        param2=0.0,
    ):

        msg = VehicleCommand()

        msg.timestamp = int(
            self.get_clock().now().nanoseconds / 1000
        )

        msg.command = command

        msg.param1 = float(param1)
        msg.param2 = float(param2)

        msg.target_system = 1
        msg.target_component = 1

        msg.source_system = 1
        msg.source_component = 1

        msg.from_external = True

        self.cmd_pub.publish(msg)

    # --------------------------------------------------
    # Landing Command
    # --------------------------------------------------

    def send_landing_command(self):

        self.publish_vehicle_command(
            VehicleCommand.VEHICLE_CMD_NAV_LAND
        )

        self.get_logger().info(
            "NAV_LAND command sent."
        )

    # --------------------------------------------------
    # Disarm Command
    # --------------------------------------------------

    def send_disarm_command(self):

        if self.disarm_requested:
            return

        self.disarm_requested = True

        self.publish_vehicle_command(
            VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM,
            param1=0.0,
        )

        self.get_logger().info(
            "Disarm command sent after confirmed touchdown."
        )

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
    # Yaw Utilities
    # --------------------------------------------------

    def normalize_angle(self, angle):

        return math.atan2(
            math.sin(angle),
            math.cos(angle),
        )

    def calculate_yaw_setpoint(self, target_x, target_y):

        dx = target_x - self.current_x
        dy = target_y - self.current_y

        horizontal_distance = math.hypot(dx, dy)

        if self.current_yaw_setpoint is None:

            if not self.position_valid:
                return self.current_heading

            self.current_yaw_setpoint = self.current_heading
            self.last_yaw_update_time = time.monotonic()

        if not self.position_valid:
            return self.current_yaw_setpoint

        if horizontal_distance < self.yaw_distance_threshold:
            return self.current_yaw_setpoint

        desired_yaw = math.atan2(dy, dx)

        yaw_error = self.normalize_angle(
            desired_yaw - self.current_yaw_setpoint
        )

        now = time.monotonic()
        dt = now - self.last_yaw_update_time

        dt = min(max(dt, 0.0), 0.2)

        self.last_yaw_update_time = now

        max_yaw_change = self.yaw_rate_limit * dt

        yaw_change = max(
            -max_yaw_change,
            min(yaw_error, max_yaw_change),
        )

        self.current_yaw_setpoint = self.normalize_angle(
            self.current_yaw_setpoint + yaw_change
        )

        return self.current_yaw_setpoint

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

        target_yaw = self.calculate_yaw_setpoint(
            self.current_target[0],
            self.current_target[1],
        )

        msg.yaw = float(target_yaw)

        self.traj_pub.publish(msg)

    # --------------------------------------------------
    # Arm
    # --------------------------------------------------

    def arm(self):

        self.publish_vehicle_command(
            VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM,
            param1=1.0,
        )

        self.get_logger().info("ARM command sent.")

    # --------------------------------------------------
    # Offboard Mode
    # --------------------------------------------------

    def offboard(self):

        self.publish_vehicle_command(
            VehicleCommand.VEHICLE_CMD_DO_SET_MODE,
            param1=1.0,
            param2=6.0,
        )

        self.get_logger().info("OFFBOARD command sent.")

    # --------------------------------------------------
    # Landing and Disarming State Machine
    # --------------------------------------------------

    def update_landing_state(self):

        if not self.landing_requested:
            return

        if self.landing_failed:
            return

        if not self.landing_acknowledged:
            return

        # Require continuous landed detection.
        if (
            self.landed
            and self.landed_since is not None
            and time.monotonic() - self.landed_since
            >= self.landed_confirmation_seconds
        ):

            if not self.disarm_requested:
                self.send_disarm_command()

    # --------------------------------------------------
    # Main Control Loop
    # --------------------------------------------------

    def timer_callback(self):

        # Continue Offboard heartbeat until PX4 confirms
        # that it has exited Offboard mode.
        if self.offboard_heartbeat_active:
            self.publish_offboard_mode()

        # Keep streaming the current setpoint while PX4
        # remains in Offboard mode during the landing transition.
        if (
            self.current_target is not None
            and (
                not self.landing_requested
                or (
                    self.vehicle_status_received
                    and self.vehicle_nav_state
                    == VehicleStatus.NAVIGATION_STATE_OFFBOARD
                )
            )
        ):

            self.publish_setpoint()

        # Normal takeoff and navigation startup.
        if (
            not self.landing_requested
            and self.current_target is not None
        ):

            if (
                self.counter == 20
                and not self.offboard_requested
            ):

                self.offboard()
                self.offboard_requested = True

            if (
                self.counter == 25
                and not self.arm_requested
            ):

                self.arm()
                self.arm_requested = True

            self.counter += 1

        # Landing and disarming sequence.
        self.update_landing_state()


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

