#!/usr/bin/env python3

import math

from cv_bridge import CvBridge

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    HistoryPolicy,
    DurabilityPolicy,
)

from sensor_msgs.msg import Image

from px4_msgs.msg import (
    SensorCombined,
    VehicleLocalPosition,
    VehicleAttitude,
)

from criticality_core.logging.sequence_manager import (
    SequenceManager,
)
from criticality_core.logging.dataset_session import (
    get_current_session,
)
from criticality_core.logging.euroc_logger import (
    EuRoCLogger,
)
from criticality_core.logging.telemetry_snapshot import (
    TelemetrySnapshot,
)


# ------------------------------------------------------
# Topics
# ------------------------------------------------------

CAMERA_TOPIC = "/criticality/camera/image"

IMU_TOPIC = "/fmu/out/sensor_combined"

POSITION_TOPIC = (
    "/fmu/out/vehicle_local_position_v1"
)

ATTITUDE_TOPIC = "/fmu/out/vehicle_attitude"


# ------------------------------------------------------
# Logging Rates
# ------------------------------------------------------

IMU_LOG_RATE_HZ = 200.0
GT_LOG_RATE_HZ = 50.0


class DatasetLogger(Node):
    """
    Records EuRoC-compatible datasets.

    The node maintains its own local TelemetrySnapshot.
    It does not share Python objects with other ROS nodes.

    Timestamp policy
    ----------------
    Original PX4 timestamps are retained in microseconds.

    Simulation timestamps are captured from the ROS
    simulation clock at the moment each PX4 message
    arrives in its callback:

        simulation_timestamp_us =
            ros_clock_now_ns // 1000

    The EuRoCLogger converts both timestamps to nanoseconds
    when writing the CSV files.

    No IMU or ground-truth rows are written until a valid
    converted sensor timestamp is available.

    Ground-truth rows remain anchored to the position
    timestamp. Position and attitude retain their own
    independent timestamps in the telemetry snapshot.

    Duplicate-sample policy
    -----------------------
    Each timer-driven stream tracks its last-logged raw
    PX4 timestamp and emits each measurement only once.
    """

    def __init__(self):

        super().__init__("dataset_logger")

        # --------------------------------------------------
        # Local Telemetry
        # --------------------------------------------------

        self.telemetry = TelemetrySnapshot()

        # --------------------------------------------------
        # Dataset
        # --------------------------------------------------

        sequence_dir = get_current_session()

        self.sequence_manager = SequenceManager(
            sequence_dir=sequence_dir,
        )

        self.euroc_logger = EuRoCLogger(
            self.sequence_manager,
        )

        # --------------------------------------------------
        # OpenCV Bridge
        # --------------------------------------------------

        self.bridge = CvBridge()

        # --------------------------------------------------
        # Counters / Flags
        # --------------------------------------------------

        self.first_frame_logged = False
        self.first_imu_logged = False
        self.first_gt_logged = False

        self.image_count = 0
        self.imu_count = 0
        self.gt_count = 0

        # --------------------------------------------------
        # Duplicate-Sample Suppression
        # --------------------------------------------------

        self.last_logged_imu_timestamp = 0
        self.last_logged_gt_timestamp = 0

        # --------------------------------------------------
        # QoS
        # --------------------------------------------------

        # Best-effort, volatile — matches PX4 DDS behaviour.
        self.qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )

        # --------------------------------------------------
        # Topics
        # --------------------------------------------------

        self.camera_topic = CAMERA_TOPIC
        self.imu_topic = IMU_TOPIC
        self.position_topic = POSITION_TOPIC
        self.attitude_topic = ATTITUDE_TOPIC

        # --------------------------------------------------
        # Camera Subscription
        # --------------------------------------------------

        self.camera_subscription = self.create_subscription(
            Image,
            self.camera_topic,
            self.camera_callback,
            self.qos,
        )

        # --------------------------------------------------
        # PX4 Subscriptions
        # --------------------------------------------------

        self.imu_subscription = self.create_subscription(
            SensorCombined,
            self.imu_topic,
            self.imu_callback,
            self.qos,
        )

        self.position_subscription = self.create_subscription(
            VehicleLocalPosition,
            self.position_topic,
            self.position_callback,
            self.qos,
        )

        self.attitude_subscription = self.create_subscription(
            VehicleAttitude,
            self.attitude_topic,
            self.attitude_callback,
            self.qos,
        )

        # --------------------------------------------------
        # Logging Timers
        # --------------------------------------------------

        self.imu_timer = self.create_timer(
            1.0 / IMU_LOG_RATE_HZ,
            self.imu_timer_callback,
        )

        self.gt_timer = self.create_timer(
            1.0 / GT_LOG_RATE_HZ,
            self.gt_timer_callback,
        )

        # --------------------------------------------------
        # Startup
        # --------------------------------------------------

        self.get_logger().info(
            "Dataset Logger initialized."
        )

        self.get_logger().info(
            f"Recording sequence:\n"
            f"{self.sequence_manager.sequence_dir}"
        )

        self.get_logger().info(
            "ROS subscriptions:"
        )

        self.get_logger().info(
            f"  Camera   : {self.camera_topic}"
        )

        self.get_logger().info(
            f"  IMU      : {self.imu_topic}"
        )

        self.get_logger().info(
            f"  Position : {self.position_topic}"
        )

        self.get_logger().info(
            f"  Attitude : {self.attitude_topic}"
        )

        self.get_logger().info(
            f"Logging rates: "
            f"IMU {IMU_LOG_RATE_HZ:.0f} Hz, "
            f"GT {GT_LOG_RATE_HZ:.0f} Hz"
        )

        self.get_logger().info(
            "Waiting for incoming sensor data..."
        )

    # ==================================================
    # Camera Callback
    # ==================================================

    def camera_callback(
        self,
        msg: Image,
    ):
        """
        Save one image frame into the EuRoC dataset.

        Camera timestamps are already in simulation time.
        No PX4 timestamp conversion is applied.
        """

        try:
            image = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding="bgr8",
            )
        except Exception as e:
            self.get_logger().error(
                f"Failed to convert image: {e}"
            )
            return

        timestamp_ns = (
            msg.header.stamp.sec * 1_000_000_000
            + msg.header.stamp.nanosec
        )

        if timestamp_ns == 0:
            self.get_logger().warning(
                "Received image with zero timestamp."
            )
            return

        if not self.first_frame_logged:
            self.get_logger().info(
                "Receiving camera frames."
            )
            self.first_frame_logged = True

        self.euroc_logger.log_camera(
            timestamp_ns=timestamp_ns,
            image=image,
        )

        self.image_count += 1

    # ==================================================
    # IMU Callback
    # ==================================================

    def imu_callback(
        self,
        msg: SensorCombined,
    ):
        """
        Update the local IMU telemetry snapshot.

        The original PX4 timestamp is retained.
        Simulation time is captured from the ROS clock
        when the message is received.
        """

        self.telemetry.imu.timestamp = msg.timestamp

        self.telemetry.imu.timestamp_sim_us = (
            self.get_clock().now().nanoseconds // 1000
        )

        self.telemetry.imu.gyro[:] = msg.gyro_rad

        self.telemetry.imu.accel[:] = (
            msg.accelerometer_m_s2
        )

    # ==================================================
    # Position Callback
    # ==================================================

    def position_callback(
        self,
        msg: VehicleLocalPosition,
    ):
        """
        Update the local position and velocity snapshot.

        The ground-truth row is anchored to the position
        timestamp, so its converted equivalent is stored
        separately.
        """

        self.telemetry.vehicle.position_timestamp = (
            msg.timestamp
        )

        self.telemetry.vehicle.position_timestamp_sim_us = (
            self.get_clock().now().nanoseconds // 1000
        )

        self.telemetry.vehicle.position[:] = (
            msg.x,
            msg.y,
            msg.z,
        )

        self.telemetry.vehicle.velocity[:] = (
            msg.vx,
            msg.vy,
            msg.vz,
        )

    # ==================================================
    # Attitude Callback
    # ==================================================

    def attitude_callback(
        self,
        msg: VehicleAttitude,
    ):
        """
        Update the local orientation snapshot.

        Position and attitude timestamps remain independent.
        """

        self.telemetry.vehicle.attitude_timestamp = (
            msg.timestamp
        )

        self.telemetry.vehicle.attitude_timestamp_sim_us = (
            self.get_clock().now().nanoseconds // 1000
        )

        # PX4 VehicleAttitude.q is [w, x, y, z].
        self.telemetry.vehicle.orientation[:] = msg.q

    # ==================================================
    # IMU Timer
    # ==================================================

    def imu_timer_callback(self):
        """
        Periodically log the latest IMU sample.

        A row is written only when:
        - An IMU sample has arrived.
        - A simulation timestamp is available.
        - The raw PX4 timestamp has not already been logged.
        """

        imu = self.telemetry.imu

        if imu.timestamp == 0:
            return

        if imu.timestamp_sim_us == 0:
            return

        if (
            imu.timestamp
            == self.last_logged_imu_timestamp
        ):
            return

        if not self.first_imu_logged:
            self.get_logger().info(
                "Receiving synchronized IMU data."
            )
            self.first_imu_logged = True

        self.euroc_logger.log_imu(
            timestamp_us=imu.timestamp,
            simulation_timestamp_us=imu.timestamp_sim_us,
            gyro=imu.gyro,
            accel=imu.accel,
        )

        self.last_logged_imu_timestamp = imu.timestamp
        self.imu_count += 1

    # ==================================================
    # Ground-Truth Timer
    # ==================================================

    def gt_timer_callback(self):
        """
        Periodically log the latest ground-truth sample.

        The row timestamp remains anchored to the position
        stream. The attitude timestamp is retained separately
        in the snapshot but does not determine the row time.
        """

        vehicle = self.telemetry.vehicle

        if vehicle.position_timestamp == 0:
            return

        if vehicle.position_timestamp_sim_us == 0:
            return

        if (
            vehicle.position_timestamp
            == self.last_logged_gt_timestamp
        ):
            return

        if not self.first_gt_logged:
            self.get_logger().info(
                "Receiving synchronized ground-truth data."
            )
            self.first_gt_logged = True

        self.euroc_logger.log_groundtruth(
            timestamp_us=vehicle.position_timestamp,
            simulation_timestamp_us=(
                vehicle.position_timestamp_sim_us
            ),
            position=vehicle.position,
            orientation=vehicle.orientation,
            velocity=vehicle.velocity,
        )

        self.last_logged_gt_timestamp = (
            vehicle.position_timestamp
        )

        self.gt_count += 1

    # ==================================================
    # Shutdown
    # ==================================================

    def destroy_node(self):

        try:

            self.euroc_logger.close()

            self.get_logger().info(
                "Dataset recording complete."
            )

            self.get_logger().info(
                f"Images saved: {self.image_count}"
            )

            self.get_logger().info(
                f"IMU samples saved: {self.imu_count}"
            )

            self.get_logger().info(
                f"Ground-truth samples saved: {self.gt_count}"
            )

        finally:

            super().destroy_node()


# ==================================================
# Main
# ==================================================

def main():

    rclpy.init()

    node = DatasetLogger()

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
