from abc import ABC
from abc import abstractmethod

from .trigger_context import TriggerContext


class BaseTrigger(ABC):
    """
    Base class for every trigger type.

    All future trigger implementations must inherit
    from this class.
    """

    @abstractmethod
    def should_fire(
        self,
        context: TriggerContext,
    ) -> bool:
        """
        Returns True when the trigger condition
        has been satisfied.
        """
        pass
