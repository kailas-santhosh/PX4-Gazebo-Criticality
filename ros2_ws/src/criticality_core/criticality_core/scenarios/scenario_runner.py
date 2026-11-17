import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    HistoryPolicy,
    DurabilityPolicy,
)

from px4_msgs.msg import VehicleLocalPosition
from px4_msgs.msg import BatteryStatus
from px4_msgs.msg import SensorCombined
from px4_msgs.msg import VehicleAttitude

from geometry_msgs.msg import PointStamped, PoseStamped
from std_msgs.msg import Bool

from criticality_core.events.event_manager import EventManager
from criticality_core.events.event_factory import EventFactory
from criticality_core.logging.criticality_logger import (
    CriticalityLogger,
    TelemetrySnapshot,
)
from criticality_core.logging.dataset_session import (
    create_new_session,
)
from criticality_core.px4.px4_failure_injector import (
    PX4FailureInjector,
)
from criticality_core.px4.battery_controller import BatteryController
from criticality_core.sensors.camera_controller import CameraController
from criticality_core.configuration.config_loader import (
    load_scenario_config,
)
from criticality_core.configuration.config_validator import (
    validate_config,
)
from criticality_core.navigation.navigation_manager import (
    NavigationManager,
)

class ScenarioRunner(Node):

    def __init__(self):

        super().__init__("scenario_runner")

        # --------------------------------------------------
        # Load Scenario Configuration
        # --------------------------------------------------

        self.config = load_scenario_config(
            "default_scenario.yaml"
        )

        validate_config(self.config)

        self.get_logger().info(
            f"Loaded scenario: "
            f"{self.config.experiment.name}"
        )

        # --------------------------------------------------
        # Startup Summary
        # --------------------------------------------------

        self.get_logger().info(
            f"Random seed: "
            f"{self.config.experiment.random_seed}"
        )

        self.get_logger().info(
            f"Navigation mode: "
            f"{self.config.navigation.mode}"
        )

        self.get_logger().info(
            f"Configured events: "
            f"{len(self.config.events)}"
        )

        # --------------------------------------------------
        # QoS Configuration
        # --------------------------------------------------

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # --------------------------------------------------
        # Shared Telemetry Snapshot
        # --------------------------------------------------

        self.telemetry = TelemetrySnapshot()

        # --------------------------------------------------
        # Experiment Time Management
        # --------------------------------------------------

        self.experiment_start_time = None

        self.latest_position = None

        # Latest vehicle velocity in PX4 Local NED.
        self.latest_velocity = None

        # ROS clock timestamp of the latest position/velocity update.
        # Used to reject stale vehicle state during obstacle spawning.
        self.latest_position_timestamp = None

        self.event_update_period = 0.05

        # --------------------------------------------------
        # Create Dataset Session
        # --------------------------------------------------

        sequence_dir = create_new_session()

        self.get_logger().info(
            f"Dataset session:\n{sequence_dir}"
        )

        # --------------------------------------------------
        # Criticality Logger
        # --------------------------------------------------

        self.criticality_logger = CriticalityLogger(
            telemetry=self.telemetry,
        )

        # --------------------------------------------------
        # PX4 Failure Injector
        # --------------------------------------------------

        self.failure_injector = PX4FailureInjector(self)

        # --------------------------------------------------
        # Camera Controller
        # --------------------------------------------------

        self.camera_controller = CameraController(self)

        # --------------------------------------------------
        # Battery Controller
        # --------------------------------------------------

        self.battery_controller = BatteryController()

        # --------------------------------------------------
        # Navigation Manager
        # --------------------------------------------------

        self.navigation_manager = NavigationManager(
            navigation_config=self.config.navigation,
            logger=self.get_logger(),
        )

        # --------------------------------------------------
        # Navigation Target Publisher
        # --------------------------------------------------

        self.target_pub = self.create_publisher(
            PointStamped,
            "/navigation/target",
            qos,
        )

        # --------------------------------------------------
        # Mission Completion Publisher
        # --------------------------------------------------

        self.mission_complete_pub = self.create_publisher(
            Bool,
            "/navigation/mission_complete",
            qos,
        )

        self.mission_complete_sent = False

        # --------------------------------------------------
        # Moving Target Subscription
        # --------------------------------------------------

        self.moving_target_sub = self.create_subscription(
            PoseStamped,
            "/navigation/moving_target/pose",
            self.moving_target_callback,
            10,
        )

        # --------------------------------------------------
        # Telemetry Subscriptions
        # --------------------------------------------------

        self.create_subscription(
            BatteryStatus,
            "/fmu/out/battery_status_v1",
            self.battery_callback,
            qos,
        )

        self.create_subscription(
            SensorCombined,
            "/fmu/out/sensor_combined",
            self.imu_callback,
            qos,
        )

        self.create_subscription(
            VehicleAttitude,
            "/fmu/out/vehicle_attitude",
            self.attitude_callback,
            qos,
        )

        # --------------------------------------------------
        # Event Manager
        # --------------------------------------------------

        self.event_manager = EventManager()

        # --------------------------------------------------
        # Event Factory
        # Shared dependencies are injected once
        # --------------------------------------------------

        self.event_factory = EventFactory(
            logger=self.get_logger(),
            criticality_logger=self.criticality_logger,
            failure_injector=self.failure_injector,
            camera_controller=self.camera_controller,
            battery_controller=self.battery_controller,
            vehicle_state_provider=self.get_vehicle_state,
        )

        # --------------------------------------------------
        # Create Events From Configuration
        # --------------------------------------------------

        for event in self.config.events:

            if not event.enabled:

                continue

            event_instance = self.event_factory.create_event(
                event
            )

            self.event_manager.add_event(
                event_instance
            )

        # --------------------------------------------------
        # Vehicle Position Subscription
        # --------------------------------------------------

        self.create_subscription(
            VehicleLocalPosition,
            "/fmu/out/vehicle_local_position_v1",
            self.position_callback,
            qos,
        )

        # --------------------------------------------------
        # Event Update Timer
        # --------------------------------------------------

        self.event_timer = self.create_timer(
            self.event_update_period,
            self.event_timer_callback,
        )

        # --------------------------------------------------
        # Startup
        # --------------------------------------------------

        self.get_logger().info(
            "Scenario Runner initialized."
        )

    # --------------------------------------------------
    # Moving Target Callback
    # --------------------------------------------------

    def moving_target_callback(self, msg):

        if self.config.navigation.mode.lower() != "moving_target":

            return

        if msg.header.frame_id != "gazebo_world":

            self.get_logger().warning(
                "Ignoring moving target pose with unexpected "
                f"frame: {msg.header.frame_id}"
            )

            return

        timestamp = (
            msg.header.stamp.sec
            + msg.header.stamp.nanosec / 1e9
        )

        if timestamp <= 0.0:

            return

        position = [
            msg.pose.position.x,
            msg.pose.position.y,
            msg.pose.position.z,
        ]

        self.navigation_manager.set_target_pose(
            position=position,
            timestamp=timestamp,
        )

    # --------------------------------------------------
    # Vehicle Position Callback
    # --------------------------------------------------

    def position_callback(self, msg):

        self.telemetry.vehicle.timestamp = msg.timestamp

        self.telemetry.vehicle.position = [
            msg.x,
            msg.y,
            msg.z,
        ]

        self.telemetry.vehicle.velocity = [
            msg.vx,
            msg.vy,
            msg.vz,
        ]

        self.latest_position = [
            msg.x,
            msg.y,
            msg.z,
        ]

        self.latest_velocity = [
            msg.vx,
            msg.vy,
            msg.vz,
        ]

        self.latest_position_timestamp = (
            self.get_clock().now().nanoseconds / 1e9
        )

        timestamp = (
            self.get_clock().now().nanoseconds / 1e9
        )

        #
        # Establish experiment start time
        # using the first received position message.
        #

        if self.experiment_start_time is None:

            self.experiment_start_time = timestamp

            self.get_logger().info(
                f"Experiment started at: "
                f"{self.experiment_start_time:.3f}"
            )

        #
        # Update the navigation strategy using the
        # latest position.
        #

        self.navigation_manager.update(
            position=[
                msg.x,
                msg.y,
                msg.z,
            ],
            timestamp=timestamp,
        )

        # --------------------------------------------------
        # Mission Completion Detection
        # --------------------------------------------------

        if (
            self.navigation_manager.finished()
            and not self.mission_complete_sent
        ):

            completion_msg = Bool()
            completion_msg.data = True

            self.mission_complete_pub.publish(completion_msg)

            self.mission_complete_sent = True

            self.get_logger().info(
                "Navigation mission completed. "
                "Landing requested."
            )

        #
        # Get the latest navigation target.
        #

        target = self.navigation_manager.current_target()

        #
        # Publish only valid targets.
        #

        if target is not None:

            target_msg = PointStamped()

            target_msg.header.stamp = (
                self.get_clock().now().to_msg()
            )

            target_msg.header.frame_id = "px4_local_ned"

            target_msg.point.x = float(target[0])
            target_msg.point.y = float(target[1])
            target_msg.point.z = float(target[2])

            self.target_pub.publish(target_msg)

    # --------------------------------------------------
    # Vehicle State Provider
    # --------------------------------------------------

    def get_vehicle_state(self):

        if self.latest_position is None:

            return None

        if self.latest_velocity is None:

            return None

        if self.latest_position_timestamp is None:

            return None

        return {
            "position": list(self.latest_position),
            "velocity": list(self.latest_velocity),
            "timestamp": self.latest_position_timestamp,
            "current_timestamp": (
                self.get_clock().now().nanoseconds / 1e9
            ),
        }

    # --------------------------------------------------
    # Event Timer Callback
    # --------------------------------------------------

    def event_timer_callback(self):

        if self.latest_position is None:

            return

        if self.experiment_start_time is None:

            return

        timestamp = (
            self.get_clock().now().nanoseconds / 1e9
        )

        x, y, z = self.latest_position

        self.event_manager.update(
            x=x,
            y=y,
            z=z,
            timestamp=timestamp,
            experiment_start_time=self.experiment_start_time,
        )

    # --------------------------------------------------
    # Battery Callback
    # --------------------------------------------------

    def battery_callback(self, msg):

        self.telemetry.battery.timestamp = msg.timestamp

        self.telemetry.battery.voltage = msg.voltage_v
        self.telemetry.battery.remaining = msg.remaining
        self.telemetry.battery.warning = msg.warning

    # --------------------------------------------------
    # IMU Callback
    # --------------------------------------------------

    def imu_callback(self, msg):

        self.telemetry.imu.timestamp = msg.timestamp

        self.telemetry.imu.gyro = list(msg.gyro_rad)
        self.telemetry.imu.accel = list(
            msg.accelerometer_m_s2
        )

    # --------------------------------------------------
    # Attitude Callback
    # --------------------------------------------------

    def attitude_callback(self, msg):

        self.telemetry.vehicle.timestamp = msg.timestamp
        self.telemetry.vehicle.orientation = list(msg.q)


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    rclpy.init()

    node = ScenarioRunner()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        #
        # Finalize active events before saving labels.
        #

        if hasattr(node, "event_manager"):

            shutdown_timestamp = (
                node.get_clock().now().nanoseconds / 1e9
            )

            node.event_manager.finalize(
                shutdown_timestamp
            )

        #
        # Save labels after finalization.
        #

        node.criticality_logger.save_csv()

        print(
            "\nSimulation logs saved."
        )

        #
        # Restore battery parameters if PX4 is still alive.
        #

        if hasattr(node, "battery_controller"):

            try:

                node.battery_controller.restore()

            except TimeoutError:

                node.get_logger().warn(
                    "Skipping battery restore because PX4 is no longer running."
                )

        #
        # Destroy node.
        #

        node.destroy_node()

        #
        # Shutdown only if still running.
        #

        if rclpy.ok():

            rclpy.shutdown()


if __name__ == "__main__":
    main()
