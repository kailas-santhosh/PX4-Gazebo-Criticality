#!/usr/bin/env python3

from dataclasses import dataclass, field

from criticality_core.logging.sequence_manager import (
    SequenceManager,
)
from criticality_core.logging.dataset_session import (
    get_current_session,
)


# ==================================================
# Telemetry Snapshot
# ==================================================

@dataclass
class BatteryTelemetry:
    """
    Latest battery telemetry received from PX4.
    """

    voltage: float = 0.0
    remaining: float = 0.0
    warning: int = 0


# --------------------------------------------------


@dataclass
class ImuTelemetry:
    """
    Latest IMU telemetry received from PX4.
    """

    gyro: list = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )

    accel: list = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )


# --------------------------------------------------


@dataclass
class VehicleTelemetry:
    """
    Latest vehicle state received from PX4.
    """

    position: list = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )

    velocity: list = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )


# --------------------------------------------------


@dataclass
class TelemetrySnapshot:
    """
    Shared live telemetry snapshot.

    ScenarioRunner continuously updates this object.
    Whenever an event begins, CriticalityLogger copies
    the current values into the event record.
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


# ==================================================
# Criticality Logger
# ==================================================

class CriticalityLogger:
    """
    Stores criticality events during a simulation.

    Events are kept in memory and later exported to
    criticality_labels.csv in EuRoC-compatible format.
    """

    def __init__(
        self,
        telemetry=None,
    ):

        self.events = []

        self.telemetry = telemetry

        #
        # Join the active dataset session created by
        # ScenarioRunner.
        #
        sequence_dir = get_current_session()

        self.sequence_manager = SequenceManager(
            sequence_dir=sequence_dir,
        )

    # --------------------------------------------------
    # Event Started
    # --------------------------------------------------

    def start_event(
        self,
        event_type,
        onset_ts,
        severity="unknown",
        params=None,
        weak_signal_ts=None,
    ):

        event = {

            "weak_signal_ts": weak_signal_ts,

            "onset_ts": onset_ts,

            "offset_ts": None,

            "event_type": event_type,

            "severity": severity,

            "params": params if params is not None else {},

            "finished": False,

            "label_written": False,

            "telemetry": None,

        }

        #
        # Capture current telemetry snapshot
        #

        if self.telemetry is not None:

            event["telemetry"] = {

                "battery": {

                    "voltage":
                        self.telemetry.battery.voltage,

                    "remaining":
                        self.telemetry.battery.remaining,

                    "warning":
                        self.telemetry.battery.warning,

                },

                "imu": {

                    "gyro":
                        self.telemetry.imu.gyro.copy(),

                    "accel":
                        self.telemetry.imu.accel.copy(),

                },

                "vehicle": {

                    "position":
                        self.telemetry.vehicle.position.copy(),

                    "velocity":
                        self.telemetry.vehicle.velocity.copy(),

                },

            }

        self.events.append(event)

        return len(self.events) - 1

    # --------------------------------------------------
    # Event Ended
    # --------------------------------------------------

    def end_event(
        self,
        event_id,
        offset_ts,
    ):

        if event_id >= len(self.events):
            return

        self.events[event_id]["offset_ts"] = offset_ts
        self.events[event_id]["finished"] = True

    # --------------------------------------------------
    # Get Events
    # --------------------------------------------------

    def get_events(self):

        return self.events
        
    # --------------------------------------------------
    # Save CSV
    # --------------------------------------------------

    def save_csv(self):

        import csv
        import json

        #
        # Defensive: ensure the sequence directory exists
        # before writing. It normally does, but this makes
        # the logger safe to use in any order.
        #
        self.sequence_manager.sequence_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            self.sequence_manager.labels_csv,
            "w",
            newline="",
        ) as csvfile:

            writer = csv.writer(csvfile)

            writer.writerow([
                "weak_signal_ts",
                "onset_ts",
                "offset_ts",
                "event_type",
                "severity",
                "params",
                "battery_voltage",
                "battery_remaining",
                "battery_warning",
                "gyro",
                "accel",
                "position",
                "velocity",
            ])

            for event in self.events:

                telemetry = event.get("telemetry")

                if telemetry is None:

                    battery_voltage = ""
                    battery_remaining = ""
                    battery_warning = ""

                    gyro = ""
                    accel = ""

                    position = ""
                    velocity = ""

                else:

                    battery = telemetry["battery"]
                    imu = telemetry["imu"]
                    vehicle = telemetry["vehicle"]

                    battery_voltage = float(battery["voltage"])
                    battery_remaining = float(battery["remaining"])
                    battery_warning = float(battery["warning"])

                    gyro = json.dumps(
                        [float(x) for x in imu["gyro"]]
                    )

                    accel = json.dumps(
                        [float(x) for x in imu["accel"]]
                    )

                    position = json.dumps(
                        [float(x) for x in vehicle["position"]]
                    )

                    velocity = json.dumps(
                        [float(x) for x in vehicle["velocity"]]
                    )
                writer.writerow([

                    event["weak_signal_ts"],

                    event["onset_ts"],

                    event["offset_ts"],

                    event["event_type"],

                    event["severity"],

                    json.dumps(
                        event["params"]
                    ),

                    battery_voltage,

                    battery_remaining,

                    battery_warning,

                    gyro,

                    accel,

                    position,

                    velocity,

                ])
