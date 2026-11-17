
import random

from criticality_core.events.base_event import BaseEvent


class SensorEvent(BaseEvent):

    def __init__(
        self,
        trigger,
        sensor,
        severity="medium",
        logger=None,
        criticality_logger=None,
        failure_injector=None,
        camera_controller=None,
    ):

        super().__init__(
            trigger=trigger,
            logger=logger,
            criticality_logger=criticality_logger,
            repeatable=True,
        )

        self.sensor = sensor.lower()

        self._severity = severity

        self.failure_injector = failure_injector
        self.camera_controller = camera_controller

        self.sensor_degraded = False

        #
        # Randomized every time the event starts.
        # Stored for dataset logging.
        #

        self.degradation_level = None

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    def event_type(self):

        return "sensor_degradation"

    # --------------------------------------------------

    def severity(self):

        return self._severity

    # --------------------------------------------------

    def parameters(self):

        return {

            "sensor": self.sensor,

            "degradation_level": self.degradation_level,

        }

    # --------------------------------------------------
    # Event Lifecycle
    # --------------------------------------------------

    def on_enter(self):

        self.sensor_degraded = True

        #
        # Randomize degradation level.
        # (Dataset metadata only.)
        #

        if self.sensor == "camera":

            self.degradation_level = random.uniform(
                0.20,
                0.60,
            )

        elif self.sensor in (
            "imu",
            "gyro",
            "accel",
            "accelerometer",
            "mag",
            "magnetometer",
            "baro",
            "barometer",
        ):

            self.degradation_level = random.uniform(
                0.05,
                0.50,
            )

        else:

            self.degradation_level = 0.30

        if self.logger is not None:

            self.logger.info(

                f"{self.sensor} degradation started "
                f"(level={self.degradation_level:.2f})"

            )

        #
        # Camera is handled by the CameraController.
        # Other sensors use PX4FailureInjector.
        #

        if self.sensor == "camera":

            if self.camera_controller is not None:

                self.camera_controller.enable_gaussian_noise(
                    self.degradation_level
                )

        else:

            if self.failure_injector is not None:

                self.failure_injector.inject_sensor_failure(
                    sensor=self.sensor
                )

    # --------------------------------------------------

    def on_update(self):

        #
        # Reserved for future extensions.
        #
        # Examples:
        #   • increase degradation over time
        #   • randomly drop additional frames
        #   • inject intermittent failures
        #

        pass

    # --------------------------------------------------

    def on_exit(self):

        self.sensor_degraded = False

        if self.logger is not None:

            self.logger.info(

                f"{self.sensor} restored"

            )

        #
        # Restore the affected sensor.
        #

        if self.sensor == "camera":

            if self.camera_controller is not None:

                self.camera_controller.disable()

        else:

            if self.failure_injector is not None:

                self.failure_injector.restore_sensor(
                    sensor=self.sensor
                )

