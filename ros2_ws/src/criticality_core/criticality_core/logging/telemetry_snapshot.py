
#!/usr/bin/env python3

from dataclasses import dataclass, field


# ==================================================
# Battery
# ==================================================

@dataclass
class BatteryTelemetry:
    """
    Latest battery state received from PX4.
    """

    timestamp: int = 0

    voltage: float = 0.0
    current: float = 0.0
    remaining: float = 0.0


# ==================================================
# IMU
# ==================================================

@dataclass
class ImuTelemetry:
    """
    Latest IMU sample received from PX4
    (SensorCombined topic).

    timestamp:
        Original PX4 timestamp in microseconds.

    timestamp_sim_us:
        Converted Gazebo simulation timestamp
        in microseconds.
    """

    timestamp: int = 0
    timestamp_sim_us: int = 0

    gyro: list = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )

    accel: list = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )


# ==================================================
# Vehicle
# ==================================================

@dataclass
class VehicleTelemetry:
    """
    Latest vehicle state received from PX4.

    Position and attitude come from independent PX4
    topics (VehicleLocalPosition and VehicleAttitude).

    Each stream retains:

    - Original PX4 timestamp in microseconds.
    - Converted simulation timestamp in microseconds.

    This allows the logger to preserve both clock
    references and inspect temporal alignment.
    """

    position_timestamp: int = 0
    position_timestamp_sim_us: int = 0

    attitude_timestamp: int = 0
    attitude_timestamp_sim_us: int = 0

    position: list = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )

    orientation: list = field(
        default_factory=lambda: [1.0, 0.0, 0.0, 0.0]
    )

    velocity: list = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )


# ==================================================
# Shared Telemetry Snapshot
# ==================================================

@dataclass
class TelemetrySnapshot:
    """
    Local telemetry snapshot owned by DatasetLogger.

    Stores the latest battery, IMU and vehicle telemetry.

    PX4 timestamps and converted simulation timestamps
    are retained separately.
    """

    battery: BatteryTelemetry = field(
        default_factory=BatteryTelemetry
    )

    imu: ImuTelemetry = field(
        default_factory=ImuTelemetry
    )

    vehicle: VehicleTelemetry = field(
        default_factory=VehicleTelemetry
    )

