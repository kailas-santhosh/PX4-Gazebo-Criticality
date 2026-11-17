#!/usr/bin/env python3

from pymavlink import mavutil


class MavlinkClient:
    """
    Generic MAVLink client for communicating with PX4.

    This class is responsible for:

    - Connecting to PX4
    - Waiting for heartbeat
    - Reading parameters
    - Writing parameters

    It intentionally contains NO battery-specific logic.
    """

    def __init__(
        self,
        connection_string="udp:127.0.0.1:14540",
        timeout=5.0,
    ):

        self.connection_string = connection_string
        self.timeout = timeout

        self.master = None

        self.target_system = 1
        self.target_component = 1
        
        self.connect()

    # ----------------------------------------------------------

    def connect(self):

        if self.master is not None:
            return

        self.master = mavutil.mavlink_connection(
            self.connection_string
        )

        self.master.wait_heartbeat(timeout=self.timeout)

        self.target_system = self.master.target_system or 1
        self.target_component = (
            self.master.target_component or 1
        )

        print(
            f"[MAVLINK] Connected "
            f"(sys={self.target_system}, "
            f"comp={self.target_component})"
        )

    # ----------------------------------------------------------

    def clear_receive_buffer(self):
        """
        Remove any stale MAVLink messages that have accumulated.

        This ensures subsequent parameter requests receive fresh
        PARAM_VALUE responses instead of processing old telemetry.
        """

        while True:

            msg = self.master.recv_match(
                blocking=False,
            )

            if msg is None:
                break

    # ----------------------------------------------------------

    def get_parameter(
        self,
        name,
    ):

        self.clear_receive_buffer()

        self.master.mav.param_request_read_send(
            self.target_system,
            self.target_component,
            name.encode(),
            -1,
        )

        while True:

            msg = self.master.recv_match(
                type="PARAM_VALUE",
                blocking=True,
                timeout=self.timeout,
            )

            if msg is None:
                raise TimeoutError(
                    f"Timeout reading parameter '{name}'"
                )

            if msg.param_id.rstrip("\x00") == name:
                return msg.param_value

    # ----------------------------------------------------------

    def set_parameter(
        self,
        name,
        value,
    ):

        self.clear_receive_buffer()

        self.master.mav.param_set_send(
            self.target_system,
            self.target_component,
            name.encode(),
            float(value),
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32,
        )

        while True:

            msg = self.master.recv_match(
                type="PARAM_VALUE",
                blocking=True,
                timeout=self.timeout,
            )

            if msg is None:
                raise TimeoutError(
                    f"Timeout writing parameter '{name}'"
                )

            if msg.param_id.rstrip("\x00") == name:

                print(
                    f"[MAVLINK] "
                    f"{name} = {msg.param_value}"
                )

                return msg.param_value
