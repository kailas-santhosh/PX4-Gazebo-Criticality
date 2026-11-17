
import math

from criticality_core.navigation.base_navigation import (
    BaseNavigation,
)


class MovingTargetNavigation(BaseNavigation):

    def __init__(self, config, logger=None):

        super().__init__(
            config=config,
            logger=logger,
        )

        self.follow_distance = float(
            getattr(config, "follow_distance", 3.0)
        )

        self.follow_altitude = float(
            getattr(config, "follow_altitude", 3.0)
        )

        self.target_timeout = float(
            getattr(config, "target_timeout", 1.0)
        )

        self.minimum_target_speed = float(
            getattr(config, "minimum_target_speed", 0.1)
        )

        if self.follow_distance <= 0.0:
            raise ValueError(
                "Follow distance must be positive."
            )

        if self.follow_altitude <= 0.0:
            raise ValueError(
                "Follow altitude must be positive."
            )

        if self.target_timeout <= 0.0:
            raise ValueError(
                "Target timeout must be positive."
            )

        if self.minimum_target_speed < 0.0:
            raise ValueError(
                "Minimum target speed cannot be negative."
            )

        self.previous_target = None
        self.current_target_position = None

        self.target_timestamp = None
        self.target_velocity = None

        self.navigation_target = None

        self.current_time = None

    def initialize(self):

        self.previous_target = None
        self.current_target_position = None

        self.target_timestamp = None
        self.target_velocity = None

        self.navigation_target = None
        self.current_time = None

        if self.logger is not None:

            self.logger.info(
                "Moving target navigation initialized."
            )

            self.logger.info(
                f"Follow distance: "
                f"{self.follow_distance:.2f} m"
            )

            self.logger.info(
                f"Follow altitude: "
                f"{self.follow_altitude:.2f} m"
            )

    # --------------------------------------------------
    # Receive target position in Gazebo ENU coordinates
    # --------------------------------------------------

    def set_target_pose(self, position, timestamp):

        if len(position) != 3:
            return

        timestamp = float(timestamp)

        new_position = (
            float(position[0]),
            float(position[1]),
            float(position[2]),
        )

        if self.current_target_position is None:

            self.current_target_position = new_position
            self.target_timestamp = timestamp

            return

        dt = timestamp - self.target_timestamp

        # Ignore duplicate or out-of-order timestamps.
        if dt <= 0.0:
            return

        previous_position = self.current_target_position

        # Update target position.
        self.previous_target = previous_position
        self.current_target_position = new_position
        self.target_timestamp = timestamp

        # Estimate horizontal target velocity in ENU.
        vx = (
            new_position[0] - previous_position[0]
        ) / dt

        vy = (
            new_position[1] - previous_position[1]
        ) / dt

        self.target_velocity = (vx, vy)

    # --------------------------------------------------
    # Update navigation
    # --------------------------------------------------

    def update(self, position, timestamp=None):

        if timestamp is None:
            self.navigation_target = None
            return

        self.current_time = float(timestamp)

        self.navigation_target = None

        if self.current_target_position is None:
            return

        if self.target_velocity is None:
            return

        # Check target-data freshness.
        target_age = (
            self.current_time - self.target_timestamp
        )

        if target_age < 0.0:
            return

        if target_age > self.target_timeout:
            return

        # Estimate horizontal target speed.
        vx, vy = self.target_velocity

        speed = math.sqrt(
            vx * vx + vy * vy
        )

        if speed < self.minimum_target_speed:
            return

        # Unit direction of target movement in ENU.
        direction_x = vx / speed
        direction_y = vy / speed

        target_x, target_y, _ = (
            self.current_target_position
        )

        # Follow behind the moving target.
        desired_x_enu = (
            target_x
            - self.follow_distance * direction_x
        )

        desired_y_enu = (
            target_y
            - self.follow_distance * direction_y
        )

        # --------------------------------------------------
        # Convert Gazebo ENU to PX4 local NED.
        #
        # NED X = ENU Y
        # NED Y = ENU X
        # NED Z = -ENU Z
        #
        # The UAV altitude is specified independently.
        # --------------------------------------------------

        desired_x_ned = desired_y_enu
        desired_y_ned = desired_x_enu
        desired_z_ned = -self.follow_altitude

        self.navigation_target = (
            desired_x_ned,
            desired_y_ned,
            desired_z_ned,
        )

    # --------------------------------------------------
    # Return desired UAV position in PX4 NED
    # --------------------------------------------------

    def current_target(self):

        return self.navigation_target

    # --------------------------------------------------
    # Moving-target missions do not finish automatically
    # --------------------------------------------------

    def finished(self):

        return False

