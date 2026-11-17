import random

from criticality_core.events.base_event import BaseEvent


class GPSEvent(BaseEvent):

    def __init__(
        self,
        trigger,
        severity="medium",
        logger=None,
        criticality_logger=None,
        failure_injector=None,
    ):

        super().__init__(
            trigger=trigger,
            logger=logger,
            criticality_logger=criticality_logger,
            repeatable=True,
        )

        self.failure_injector = failure_injector

        self._severity = severity

        self.gps_denied = False

        #
        # Randomized every time the event starts.
        #

        self.noise_sigma = None

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    def event_type(self):

        return "gps_denial"

    # --------------------------------------------------

    def severity(self):

        return self._severity

    # --------------------------------------------------

    def parameters(self):

        return {

            "noise_sigma": self.noise_sigma,

        }

    # --------------------------------------------------
    # Event Lifecycle
    # --------------------------------------------------

    def on_enter(self):

        self.gps_denied = True

        #
        # Randomize the logged GPS noise value.
        # (Used for dataset labels only.)
        #

        self.noise_sigma = random.uniform(
            3.0,
            10.0,
        )

        if self.logger is not None:

            self.logger.info(

                f"GPS denial started "
                f"(noise_sigma={self.noise_sigma:.2f})"

            )

        #
        # Inject GPS failure into PX4.
        #

        if self.failure_injector is not None:

            self.failure_injector.inject_gps_failure()

    # --------------------------------------------------

    def on_update(self):

        #
        # Reserved for future extensions.
        #
        # Example:
        #   • periodically change failure type
        #   • progressively worsen degradation
        #

        pass

    # --------------------------------------------------

    def on_exit(self):

        self.gps_denied = False

        if self.logger is not None:

            self.logger.info(

                "GPS restored"

            )

        #
        # Restore normal GPS behaviour.
        #

        if self.failure_injector is not None:

            self.failure_injector.restore_gps()
