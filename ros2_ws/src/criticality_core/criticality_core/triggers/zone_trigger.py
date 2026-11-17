from .base_trigger import BaseTrigger
from .trigger_context import TriggerContext

from criticality_core.utils.trigger_zone import (
    TriggerZone,
)


class ZoneTrigger(BaseTrigger):
    """
    Trigger based on a spherical trigger zone.

    This wraps the existing TriggerZone class so
    that future trigger implementations share a
    common interface.
    """

    def __init__(
        self,
        x,
        y,
        z,
        radius,
    ):

        self.zone = TriggerZone(
            x=x,
            y=y,
            z=z,
            radius=radius,
        )

    def should_fire(
        self,
        context: TriggerContext,
    ) -> bool:

        return self.zone.contains(
            context.x,
            context.y,
            context.z,
        )

    def distance(
        self,
        context: TriggerContext,
    ):

        return self.zone.distance(
            context.x,
            context.y,
            context.z,
        )
