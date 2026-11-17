#!/usr/bin/env python3

from dataclasses import dataclass, field


# ==================================================
# Battery Telemetry
# ==================================================

@dataclass
class BatteryTelemetry:
    """
    Latest battery telemetry received from PX4.
    """

    timestamp: int = 0  # PX4 timestamp (microseconds)

    voltage: float = 0.0

    remaining: float = 0.0

    warning: int = 0


# ==================================================
# IMU Telemetry
# ==================================================

@dataclass
class ImuTelemetry:
    """
    Latest IMU telemetry received from PX4.
    """

    timestamp: int = 0

    gyro: list = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )

    accel: list = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )



# ==================================================
# Vehicle Telemetry
# ==================================================

@dataclass
class VehicleTelemetry:
    """
    Latest vehicle state received from PX4.
    """

    timestamp: int = 0

    position: list = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )

    orientation: list = field(
        default_factory=lambda: [1.0, 0.0, 0.0, 0.0]
    )  # qw, qx, qy, qz

    velocity: list = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )
