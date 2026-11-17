
from criticality_core.triggers.base_trigger import BaseTrigger
from criticality_core.triggers.trigger_context import TriggerContext


class TimeTrigger(BaseTrigger):
    """
    Trigger based on elapsed experiment time.

    delay:
        Time in seconds after experiment start.

    duration:
        Optional active duration in seconds.
        If None, the trigger remains active after activation.
    """

    def __init__(
        self,
        delay: float,
        duration: float | None = None,
    ):
        if delay < 0:
            raise ValueError("Time trigger delay cannot be negative.")

        if duration is not None and duration <= 0:
            raise ValueError("Time trigger duration must be positive.")

        self.delay = float(delay)
        self.duration = (
            float(duration) if duration is not None else None
        )

    def should_fire(self, context: TriggerContext) -> bool:

        if context.experiment_start_time is None:
            return False

        elapsed = (
            context.timestamp - context.experiment_start_time
        )

        if elapsed < self.delay:
            return False

        if self.duration is None:
            return True

        return elapsed < self.delay + self.duration
