from abc import ABC, abstractmethod


class BaseNavigation(ABC):

    def __init__(
        self,
        config,
        logger=None,
    ):

        self.config = config
        self.logger = logger

    # --------------------------------------------------

    @abstractmethod
    def initialize(self):
        """
        Called once before navigation begins.
        """
        pass

    # --------------------------------------------------

    @abstractmethod
    def update(
        self,
        position,
    ):
        """
        Called every navigation update.
        """
        pass

    # --------------------------------------------------

    @abstractmethod
    def current_target(self):
        """
        Returns the current navigation target.
        """
        pass

    # --------------------------------------------------

    @abstractmethod
    def finished(self):
        """
        Returns True when navigation has completed.
        """
        pass
