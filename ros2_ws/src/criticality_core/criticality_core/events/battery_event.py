#!/usr/bin/env python3

import random

from criticality_core.events.base_event import BaseEvent


class BatteryEvent(BaseEvent):
    """
    Battery criticality event.

    Simulates a battery emergency by increasing the PX4 battery
    drain rate through the BatteryController. PX4's native battery
    failsafe logic then handles Low Battery, Critical Battery,
    RTL, Landing, and Disarm automatically.
    """

    def __init__(
        self,
        trigger,
        severity="high",
        logger=None,
        criticality_logger=None,
        battery_controller=None,
        drain_rate=None,
        minimum_percentage=1.0,
    ):

        super().__init__(
            trigger=trigger,
            logger=logger,
            criticality_logger=criticality_logger,
            repeatable=False,
        )

        self.battery_controller = battery_controller

        self._severity = severity

        self.battery_emergency = False

        #
        # Event parameters
        #

        self.drain_rate = drain_rate
        self.minimum_percentage = minimum_percentage

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    def event_type(self):

        return "battery"

    # --------------------------------------------------

    def severity(self):

        return self._severity

    # --------------------------------------------------

    def parameters(self):

        return {
            "drain_rate": self.drain_rate,
            "minimum_percentage": self.minimum_percentage,
        }

    # --------------------------------------------------
    # Event Lifecycle
    # --------------------------------------------------

    def on_enter(self):

        self.battery_emergency = True

        #
        # Randomize drain rate if one wasn't supplied.
        #

        if self.drain_rate is None:

            self.drain_rate = random.uniform(
                300.0,
                700.0,
            )

        if self.logger is not None:

            self.logger.info(
                "Battery emergency started "
                f"(drain_rate={self.drain_rate:.1f})"
            )

        #
        # Trigger accelerated battery drain.
        #

        if self.battery_controller is not None:

            self.battery_controller.start_battery_emergency(
                drain_rate=self.drain_rate,
                minimum_percentage=self.minimum_percentage,
            )

    # --------------------------------------------------

    def on_update(self):

        #
        # Reserved for future extensions.
        #
        # Possible future improvements:
        #
        #   • Multi-stage battery degradation
        #   • Dynamic drain-rate adjustment
        #   • Monitoring remaining battery percentage
        #   • Logging RTL / LAND transitions
        #

        pass

    # --------------------------------------------------

    def on_exit(self):

        #self.battery_emergency = False

        #if self.logger is not None:

            #self.logger.info(
                #"Battery emergency finished"
            #)
        #
        # Restore original simulator parameters.
        #

        #if self.battery_controller is not None:

        #    self.battery_controller.restore()
        pass
