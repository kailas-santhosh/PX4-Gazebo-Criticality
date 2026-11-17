#!/usr/bin/env python3

from px4_msgs.msg import VehicleCommand


class PX4FailureInjector:
    """
    Generic PX4 Failure Injection helper.

    Wraps VEHICLE_CMD_INJECT_FAILURE so event classes do not need
    to know any PX4 command details.
    """

    # ----------------------------------------------------------
    # Failure Units
    # ----------------------------------------------------------

    GPS = VehicleCommand.FAILURE_UNIT_SENSOR_GPS
    GYRO = VehicleCommand.FAILURE_UNIT_SENSOR_GYRO
    ACCEL = VehicleCommand.FAILURE_UNIT_SENSOR_ACCEL
    MAG = VehicleCommand.FAILURE_UNIT_SENSOR_MAG
    BARO = VehicleCommand.FAILURE_UNIT_SENSOR_BARO
    BATTERY = VehicleCommand.FAILURE_UNIT_SYSTEM_BATTERY

    # ----------------------------------------------------------
    # Failure Types
    # ----------------------------------------------------------

    OK = VehicleCommand.FAILURE_TYPE_OK
    OFF = VehicleCommand.FAILURE_TYPE_OFF
    STUCK = VehicleCommand.FAILURE_TYPE_STUCK
    GARBAGE = VehicleCommand.FAILURE_TYPE_GARBAGE
    WRONG = VehicleCommand.FAILURE_TYPE_WRONG
    SLOW = VehicleCommand.FAILURE_TYPE_SLOW
    DELAYED = VehicleCommand.FAILURE_TYPE_DELAYED
    INTERMITTENT = VehicleCommand.FAILURE_TYPE_INTERMITTENT
    DRIFT = VehicleCommand.FAILURE_TYPE_DRIFT

    # ----------------------------------------------------------

    def __init__(self, node):

        self.node = node

        self.publisher = node.create_publisher(
            VehicleCommand,
            "/fmu/in/vehicle_command",
            10,
        )

    # ----------------------------------------------------------
    # Generic Failure Injection
    # ----------------------------------------------------------

    def inject_failure(
        self,
        failure_unit,
        failure_type,
    ):

        msg = VehicleCommand()

        msg.timestamp = (
            self.node.get_clock().now().nanoseconds // 1000
        )

        msg.command = VehicleCommand.VEHICLE_CMD_INJECT_FAILURE

        msg.param1 = float(failure_unit)
        msg.param2 = float(failure_type)

        msg.target_system = 1
        msg.target_component = 1

        msg.source_system = 1
        msg.source_component = 1

        msg.confirmation = 0
        msg.from_external = True

        self.publisher.publish(msg)

        self.node.get_logger().info(
            f"Injected failure "
            f"(unit={failure_unit}, type={failure_type})"
        )

    # ----------------------------------------------------------
    # GPS
    # ----------------------------------------------------------

    def inject_gps_failure(
        self,
        failure_type=GARBAGE,
    ):

        self.inject_failure(
            self.GPS,
            failure_type,
        )

    def restore_gps(self):

        self.inject_failure(
            self.GPS,
            self.OK,
        )

    # ----------------------------------------------------------
    # Generic Sensor Injection
    # ----------------------------------------------------------

    def inject_sensor_failure(
        self,
        sensor,
        failure_type=None,
    ):

        sensor = sensor.lower()

        if failure_type is None:
            failure_type = self.GARBAGE

        if sensor == "gyro":
            self.inject_gyro(failure_type)

        elif sensor in ("accel", "accelerometer"):
            self.inject_accel(failure_type)

        elif sensor in ("mag", "magnetometer"):
            self.inject_mag(failure_type)

        elif sensor in ("baro", "barometer"):
            self.inject_baro(failure_type)

        elif sensor == "camera":
            #
            # Camera is NOT a PX4 sensor.
            # It will later be degraded using Gazebo.
            #
            self.node.get_logger().warning(
                "Camera degradation is not supported "
                "through PX4 failure injection."
            )

        else:
            self.node.get_logger().warning(
                f"Unknown sensor '{sensor}'."
            )

    # ----------------------------------------------------------

    def restore_sensor(
        self,
        sensor,
    ):

        sensor = sensor.lower()

        if sensor == "gyro":
            self.restore_gyro()

        elif sensor in ("accel", "accelerometer"):
            self.restore_accel()

        elif sensor in ("mag", "magnetometer"):
            self.restore_mag()

        elif sensor in ("baro", "barometer"):
            self.restore_baro()

        elif sensor == "camera":
            self.node.get_logger().warning(
                "Camera restoration will later be handled "
                "by Gazebo."
            )

        else:
            self.node.get_logger().warning(
                f"Unknown sensor '{sensor}'."
            )

    # ----------------------------------------------------------
    # Battery
    # ----------------------------------------------------------

    def inject_battery_failure(
        self,
        failure_type=OFF,
    ):

        self.inject_failure(
            self.BATTERY,
            failure_type,
        )

    def restore_battery(self):

        self.inject_failure(
            self.BATTERY,
            self.OK,
        )

    # ----------------------------------------------------------
    # Individual Sensor Wrappers
    # ----------------------------------------------------------

    def inject_gyro(
        self,
        failure_type=GARBAGE,
    ):

        self.inject_failure(
            self.GYRO,
            failure_type,
        )

    def restore_gyro(self):

        self.inject_failure(
            self.GYRO,
            self.OK,
        )

    # ----------------------------------------------------------

    def inject_accel(
        self,
        failure_type=GARBAGE,
    ):

        self.inject_failure(
            self.ACCEL,
            failure_type,
        )

    def restore_accel(self):

        self.inject_failure(
            self.ACCEL,
            self.OK,
        )

    # ----------------------------------------------------------

    def inject_mag(
        self,
        failure_type=GARBAGE,
    ):

        self.inject_failure(
            self.MAG,
            failure_type,
        )

    def restore_mag(self):

        self.inject_failure(
            self.MAG,
            self.OK,
        )

    # ----------------------------------------------------------

    def inject_baro(
        self,
        failure_type=GARBAGE,
    ):

        self.inject_failure(
            self.BARO,
            failure_type,
        )

    def restore_baro(self):

        self.inject_failure(
            self.BARO,
            self.OK,
        )
