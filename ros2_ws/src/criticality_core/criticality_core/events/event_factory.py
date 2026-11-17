from criticality_core.events.obstacle_event import ObstacleEvent
from criticality_core.events.gps_event import GPSEvent
from criticality_core.events.sensor_event import SensorEvent
from criticality_core.events.battery_event import BatteryEvent

from criticality_core.triggers.zone_trigger import (
    ZoneTrigger,
)
from criticality_core.triggers.time_trigger import (
    TimeTrigger,
)


class EventFactory:

    def __init__(
        self,
        logger=None,
        criticality_logger=None,
        failure_injector=None,
        camera_controller=None,
        battery_controller=None,
        vehicle_state_provider=None,
    ):

        self.logger = logger
        self.criticality_logger = criticality_logger
        self.failure_injector = failure_injector
        self.camera_controller = camera_controller
        self.battery_controller = battery_controller
        self.vehicle_state_provider = vehicle_state_provider

    # --------------------------------------------------
    # Trigger Construction
    # --------------------------------------------------

    def create_trigger(
        self,
        trigger_config,
    ):

        if trigger_config.type == "zone":

            return ZoneTrigger(
                x=trigger_config.x,
                y=trigger_config.y,
                z=trigger_config.z,
                radius=trigger_config.radius,
            )

        elif trigger_config.type == "time":

            return TimeTrigger(
                delay=trigger_config.delay,
                duration=trigger_config.duration,
            )

        raise ValueError(
            f"Unknown trigger type: "
            f"{trigger_config.type!r}"
        )

    # --------------------------------------------------
    # Config-Driven Event Construction
    # --------------------------------------------------

    def create_event(
        self,
        event_config,
    ):
        """
        Translate an EventConfig (from YAML) into a concrete
        Event instance by dispatching on event_config.type.
        """

        if not event_config.enabled:

            return None

        trigger = self.create_trigger(
            event_config.trigger
        )

        parameters = event_config.parameters

        # --------------------------------------------------
        # Obstacle
        # --------------------------------------------------

        if event_config.type == "obstacle":

            spawn = parameters.spawn or {}

            return ObstacleEvent(
                trigger=trigger,
                model_file=parameters.model_file,
                model_name=parameters.model_name,
                x=spawn.get("x"),
                y=spawn.get("y"),
                z=spawn.get("z"),
                severity=event_config.severity,
                logger=self.logger,
                criticality_logger=self.criticality_logger,
                vehicle_state_provider=self.vehicle_state_provider,
                spawn_reference=spawn.get("reference"),
                forward=spawn.get("forward", 0.0),
                right=spawn.get("right", 0.0),
                down=spawn.get("down", 0.0),
            )

        # --------------------------------------------------
        # GPS Denial
        # --------------------------------------------------

        elif event_config.type == "gps_denied":

            return GPSEvent(
                trigger=trigger,
                severity=event_config.severity,
                logger=self.logger,
                criticality_logger=self.criticality_logger,
                failure_injector=self.failure_injector,
            )

        # --------------------------------------------------
        # Sensor Degradation
        # --------------------------------------------------

        elif event_config.type == "sensor_degradation":

            return SensorEvent(
                trigger=trigger,
                sensor=parameters.sensor,
                severity=event_config.severity,
                logger=self.logger,
                criticality_logger=self.criticality_logger,
                failure_injector=self.failure_injector,
                camera_controller=self.camera_controller,
            )

        # --------------------------------------------------
        # Battery Emergency
        # --------------------------------------------------

        elif event_config.type == "battery":

            return BatteryEvent(
                trigger=trigger,
                severity=event_config.severity,
                logger=self.logger,
                criticality_logger=self.criticality_logger,
                battery_controller=self.battery_controller,
            )

        # --------------------------------------------------
        # Unknown Event
        # --------------------------------------------------

        raise ValueError(
            f"Unknown event type: "
            f"{event_config.type!r} "
            f"(event id={event_config.id!r}, "
            f"name={event_config.name!r})"
        )

    # --------------------------------------------------
    # Obstacle Event
    # --------------------------------------------------

    def create_obstacle_event(
        self,
        trigger_x,
        trigger_y,
        trigger_z,
        trigger_radius,
        model_file,
        model_name,
        spawn_x,
        spawn_y,
        spawn_z,
        severity="medium",
        vehicle_state_provider=None,
        spawn_reference=None,
        forward=0.0,
        right=0.0,
        down=0.0,
    ):

        trigger = ZoneTrigger(
            x=trigger_x,
            y=trigger_y,
            z=trigger_z,
            radius=trigger_radius,
        )

        return ObstacleEvent(
            trigger=trigger,
            model_file=model_file,
            model_name=model_name,
            x=spawn_x,
            y=spawn_y,
            z=spawn_z,
            severity=severity,
            logger=self.logger,
            criticality_logger=self.criticality_logger,
            vehicle_state_provider=vehicle_state_provider,
            spawn_reference=spawn_reference,
            forward=forward,
            right=right,
            down=down,
        )

    # --------------------------------------------------
    # GPS Denial Event
    # --------------------------------------------------

    def create_gps_event(
        self,
        trigger_x,
        trigger_y,
        trigger_z,
        trigger_radius,
        severity="medium",
    ):

        trigger = ZoneTrigger(
            x=trigger_x,
            y=trigger_y,
            z=trigger_z,
            radius=trigger_radius,
        )

        return GPSEvent(
            trigger=trigger,
            severity=severity,
            logger=self.logger,
            criticality_logger=self.criticality_logger,
            failure_injector=self.failure_injector,
        )

    # --------------------------------------------------
    # Sensor Degradation Event
    # --------------------------------------------------

    def create_sensor_event(
        self,
        trigger_x,
        trigger_y,
        trigger_z,
        trigger_radius,
        sensor,
        severity="medium",
    ):

        trigger = ZoneTrigger(
            x=trigger_x,
            y=trigger_y,
            z=trigger_z,
            radius=trigger_radius,
        )

        return SensorEvent(
            trigger=trigger,
            sensor=sensor,
            severity=severity,
            logger=self.logger,
            criticality_logger=self.criticality_logger,
            failure_injector=self.failure_injector,
            camera_controller=self.camera_controller,
        )

    # --------------------------------------------------
    # Battery Emergency Event
    # --------------------------------------------------

    def create_battery_event(
        self,
        trigger_x,
        trigger_y,
        trigger_z,
        trigger_radius,
        severity="high",
    ):

        trigger = ZoneTrigger(
            x=trigger_x,
            y=trigger_y,
            z=trigger_z,
            radius=trigger_radius,
        )

        return BatteryEvent(
            trigger=trigger,
            severity=severity,
            logger=self.logger,
            criticality_logger=self.criticality_logger,
            battery_controller=self.battery_controller,
        )
