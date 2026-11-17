from dataclasses import dataclass

@dataclass
class TriggerContext:
    """
    Shared information passed to trigger implementations.
    """

    x: float
    y: float
    z: float

    timestamp: float

    experiment_start_time: float | None = None

    velocity: tuple | None = None

    heading: float | None = None

    battery_remaining: float | None = None

    target_position: tuple | None = None
