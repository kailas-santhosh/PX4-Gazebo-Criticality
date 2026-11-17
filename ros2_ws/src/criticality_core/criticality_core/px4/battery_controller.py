#!/usr/bin/env python3

from .mavlink_client import MavlinkClient


class BatteryController:
    """
    Controls the PX4 simulated battery using MAVLink parameter updates.

    This class is responsible for:
      - remembering the original simulator parameters
      - triggering accelerated battery drain
      - restoring the simulator back to its original state
    """

    def __init__(
        self,
        connection="udp:127.0.0.1:14540",
    ):

        self.client = MavlinkClient(connection)

        # Original parameter values
        self.original_drain = None
        self.original_min_pct = None

    # ----------------------------------------------------------
    # Parameter helpers
    # ----------------------------------------------------------

    def get_drain_rate(self):

        return self.client.get_parameter("SIM_BAT_DRAIN")

    def set_drain_rate(self, value):

        self.client.set_parameter(
            "SIM_BAT_DRAIN",
            float(value),
        )

    def get_min_percentage(self):

        return self.client.get_parameter(
            "SIM_BAT_MIN_PCT"
        )

    def set_min_percentage(self, value):

        self.client.set_parameter(
            "SIM_BAT_MIN_PCT",
            float(value),
        )

    # ----------------------------------------------------------
    # Save / Restore
    # ----------------------------------------------------------

    def save_original_parameters(self):

        self.original_drain = self.get_drain_rate()
        self.original_min_pct = self.get_min_percentage()

        print(
            f"[Battery] Saved originals:"
            f" drain={self.original_drain},"
            f" min_pct={self.original_min_pct}"
        )

    def restore(self):

        print(
            f"[Battery] Restoring:"
            f" drain={self.original_drain},"
            f" min_pct={self.original_min_pct}"
        )

        if self.original_drain is not None:
            self.set_drain_rate(self.original_drain)

        if self.original_min_pct is not None:
            self.set_min_percentage(self.original_min_pct)

        print(
            "[Battery] Parameters restored."
        )

        print(
            f"[Battery] Verify:"
            f" drain={self.get_drain_rate()},"
            f" min_pct={self.get_min_percentage()}"
        )

        print(
            "[Battery] Parameters restored."
        )

    # ----------------------------------------------------------
    # High-Level Event API
    # ----------------------------------------------------------

    def start_battery_emergency(
        self,
        drain_rate=500.0,
        minimum_percentage=1.0,
    ):
        """
        Trigger a rapid battery discharge.

        Parameters
        ----------
        drain_rate :
            Battery drain multiplier.

        minimum_percentage :
            Battery percentage floor before shutdown.
        """

        # Save only once
        if self.original_drain is None:
            self.save_original_parameters()

        self.set_min_percentage(
            minimum_percentage
        )

        self.set_drain_rate(
            drain_rate
        )

        print(
            "[Battery] Emergency battery drain activated."
        )
