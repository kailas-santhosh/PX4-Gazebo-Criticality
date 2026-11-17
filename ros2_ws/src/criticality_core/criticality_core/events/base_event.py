from abc import ABC, abstractmethod

from criticality_core.triggers.trigger_context import (
    TriggerContext,
)


class BaseEvent(ABC):

    def __init__(
        self,
        trigger,
        logger=None,
        criticality_logger=None,
        repeatable=False,
    ):

        self.trigger = trigger

        self.logger = logger

        self.criticality_logger = criticality_logger

        self.repeatable = repeatable

        self.active = False
        self.completed = False
        self.event_id = None

    # --------------------------------------------------


    def update(
        self,
        x,
        y,
        z,
        timestamp,
        experiment_start_time=None,
    ):

        if self.completed and not self.repeatable:
            return

        context = TriggerContext(
            x=x,
            y=y,
            z=z,
            timestamp=timestamp,
            experiment_start_time=experiment_start_time,
        )

        inside = self.trigger.should_fire(context)

        # -------------------------
        # Enter Trigger
        # -------------------------

        if inside and not self.active:

            activation_result = self.on_enter()

            # An explicit False means activation failed.
            # Keep the event inactive so it can retry.

            if activation_result is False:

                return

            self.active = True

            if self.criticality_logger is not None:

                self.event_id = self.criticality_logger.start_event(
                    event_type=self.event_type(),
                    onset_ts=timestamp,
                    severity=self.severity(),
                    params=self.parameters(),
                )

        # -------------------------
        # Stay Inside
        # -------------------------

        elif inside:

            self.on_update()

        # -------------------------
        # Exit Trigger
        # -------------------------

        elif self.active:

            self.active = False
            self.completed = True

            if (
                self.criticality_logger is not None
                and self.event_id is not None
            ):

                self.criticality_logger.end_event(
                    event_id=self.event_id,
                    offset_ts=timestamp,
                )

            self.on_exit()

    def finalize(self, timestamp):
        """
        Close an active event when the experiment ends.

        This closes its criticality label without invoking
        on_exit(), so persistent physical entities such as
        obstacles are not removed.
        """

        if not self.active:
            return

        if (
            self.criticality_logger is not None
            and self.event_id is not None
        ):

            self.criticality_logger.end_event(
                event_id=self.event_id,
                offset_ts=timestamp,
            )

        self.active = False
        self.completed = True


    # ==================================================
    # Information for logger
    # ==================================================

    @abstractmethod
    def event_type(self):
        pass

    @abstractmethod
    def severity(self):
        pass
    @abstractmethod
    def parameters(self):
        pass

    # ==================================================
    # Event lifecycle
    # ==================================================

    @abstractmethod
    def on_enter(self):
        pass

    @abstractmethod
    def on_update(self):
        pass

    @abstractmethod
    def on_exit(self):
        pass
