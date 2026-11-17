from .scenario_config import ScenarioConfig


def validate_config(config: ScenarioConfig):

    # --------------------------------------------------
    # Experiment
    # --------------------------------------------------

    if config.experiment.max_duration <= 0:

        raise ValueError(
            "Experiment duration must be positive."
        )

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------

    valid_navigation_modes = [
        "fixed_waypoints",
        "moving_target",
    ]

    if config.navigation.mode not in valid_navigation_modes:

        raise ValueError(
            f"Unknown navigation mode: "
            f"{config.navigation.mode}"
        )

    # --------------------------------------------------
    # Events
    # --------------------------------------------------

    event_names = set()

    valid_event_types = {
        "obstacle",
        "gps_denied",
        "sensor_degradation",
        "battery",
    }

    for event in config.events:

        # Event name uniqueness
        if event.name in event_names:

            raise ValueError(
                f"Duplicate event name: {event.name}"
            )

        event_names.add(event.name)

        if not event.enabled:
            continue

        # Event type
        if event.type not in valid_event_types:

            raise ValueError(
                f"Unknown event type: "
                f"{event.type!r} "
                f"(event id={event.id!r})"
            )

        # Trigger type
        trigger = event.trigger

        if trigger.type not in {"zone", "time"}:

            raise ValueError(
                f"Unknown trigger type: "
                f"{trigger.type!r} "
                f"(event id={event.id!r})"
            )

        # ----------------------------------------------
        # Spatial trigger validation
        # ----------------------------------------------

        if trigger.type == "zone":

            coordinates = {
                "x": trigger.x,
                "y": trigger.y,
                "z": trigger.z,
                "radius": trigger.radius,
            }

            missing = [
                key
                for key, value in coordinates.items()
                if value is None
            ]

            if missing:

                raise ValueError(
                    f"Zone trigger for event "
                    f"{event.id!r} is missing: "
                    f"{missing}"
                )

            if trigger.radius <= 0:

                raise ValueError(
                    f"Zone trigger radius must be positive "
                    f"(event id={event.id!r})"
                )

        # ----------------------------------------------
        # Time trigger validation
        # ----------------------------------------------

        elif trigger.type == "time":

            if trigger.delay is None:

                raise ValueError(
                    f"Time trigger for event "
                    f"{event.id!r} requires a delay."
                )

            if trigger.delay < 0:

                raise ValueError(
                    f"Time trigger delay cannot be negative "
                    f"(event id={event.id!r})"
                )

            if (
                trigger.duration is not None
                and trigger.duration <= 0
            ):

                raise ValueError(
                    f"Time trigger duration must be positive "
                    f"(event id={event.id!r})"
                )

    return True
