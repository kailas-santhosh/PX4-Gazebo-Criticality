
from criticality_core.navigation.fixed_waypoint_navigation import (
    FixedWaypointNavigation,
)

from criticality_core.navigation.moving_target_navigation import (
    MovingTargetNavigation,
)


class NavigationManager:

    def __init__(self, navigation_config, logger=None):

        self.logger = logger

        self.mode = navigation_config.mode.lower()

        if self.mode == "fixed_waypoints":

            self.navigation = FixedWaypointNavigation(
                navigation_config,
                logger=logger,
            )

        elif self.mode == "moving_target":

            self.navigation = MovingTargetNavigation(
                navigation_config,
                logger=logger,
            )

        else:

            raise ValueError(
                f"Unsupported navigation mode: {self.mode}"
            )

        self.navigation.initialize()

    # --------------------------------------------------
    # Receive moving-target position
    # --------------------------------------------------

    def set_target_pose(self, position, timestamp):

        if self.mode != "moving_target":
            return

        self.navigation.set_target_pose(
            position=position,
            timestamp=timestamp,
        )

    # --------------------------------------------------
    # Update navigation
    # --------------------------------------------------

    def update(self, position, timestamp=None):

        if self.mode == "moving_target":

            self.navigation.update(
                position=position,
                timestamp=timestamp,
            )

        else:

            # Preserve the original fixed-waypoint interface.
            self.navigation.update(position)

    # --------------------------------------------------
    # Current target
    # --------------------------------------------------

    def current_target(self):

        return self.navigation.current_target()

    # --------------------------------------------------
    # Mission completion
    # --------------------------------------------------

    def finished(self):

        return self.navigation.finished()

