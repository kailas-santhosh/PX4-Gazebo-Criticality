
from criticality_core.navigation.base_navigation import (
    BaseNavigation,
)

from criticality_core.missions.square import WAYPOINTS


class FixedWaypointNavigation(BaseNavigation):

    def __init__(
        self,
        config,
        logger=None,
    ):

        super().__init__(
            config=config,
            logger=logger,
        )

        # Current waypoint index.
        self.index = 0

        # Distance at which a waypoint is considered reached.
        self.reach_distance = 0.4

        # Load waypoint sequence from the square mission.
        self.waypoints = [
            tuple(waypoint)
            for waypoint in WAYPOINTS
        ]

    # --------------------------------------------------

    def initialize(self):

        if self.logger is not None:

            self.logger.info(
                "Fixed waypoint navigation initialized."
            )

            self.logger.info(
                f"Loaded {len(self.waypoints)} waypoints."
            )

    # --------------------------------------------------

    def update(
        self,
        position,
    ):

        if self.finished():

            return

        target = self.current_target()

        distance = sum(

            (position[i] - target[i]) ** 2

            for i in range(3)

        ) ** 0.5

        if distance < self.reach_distance:

            if self.logger is not None:

                self.logger.info(
                    f"Reached waypoint {self.index}."
                )

            self.index += 1

            if self.finished():

                if self.logger is not None:

                    self.logger.info(
                        "Fixed waypoint navigation completed."
                    )

            elif self.logger is not None:

                self.logger.info(
                    f"Proceeding to waypoint {self.index}."
                )

    # --------------------------------------------------

    def current_target(self):

        if self.finished():

            return None

        return self.waypoints[self.index]

    # --------------------------------------------------

    def finished(self):

        return self.index >= len(self.waypoints)

