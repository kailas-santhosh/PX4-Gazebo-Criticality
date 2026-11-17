import math
import re

from criticality_core.entity_manager import EntityManager
from criticality_core.events.base_event import BaseEvent


class ObstacleEvent(BaseEvent):

    MIN_HORIZONTAL_SPEED = 0.5
    MAX_STATE_AGE = 0.5

    def __init__(
        self,
        trigger,
        model_file,
        model_name,
        x,
        y,
        z,
        severity="medium",
        logger=None,
        criticality_logger=None,
        vehicle_state_provider=None,
        spawn_reference=None,
        forward=0.0,
        right=0.0,
        down=0.0,
    ):

        super().__init__(
            trigger=trigger,
            logger=logger,
            criticality_logger=criticality_logger,
            repeatable=False,
        )

        self.manager = EntityManager()

        self.model_file = model_file
        self.model_name = model_name

        # Existing fixed coordinates.
        self.x = x
        self.y = y
        self.z = z

        # Actual Gazebo ENU coordinates after spawn calculation.
        self.spawn_x = None
        self.spawn_y = None
        self.spawn_z = None

        # Optional drone-relative spawning.
        self.vehicle_state_provider = vehicle_state_provider
        self.spawn_reference = spawn_reference

        self.forward = float(forward)
        self.right = float(right)
        self.down = float(down)

        self._severity = severity

        offsets = [self.forward, self.right, self.down]

        if not all(math.isfinite(value) for value in offsets):
            raise ValueError("Spawn offsets must be finite numbers.")

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    def event_type(self):

        return "obstacle"

    # --------------------------------------------------

    def severity(self):

        return self._severity

    # --------------------------------------------------

    def parameters(self):

        # Use actual spawn coordinates when available.
        # Otherwise retain the configured fixed coordinates.
        actual_x = (
            self.spawn_x
            if self.spawn_x is not None
            else self.x
        )

        actual_y = (
            self.spawn_y
            if self.spawn_y is not None
            else self.y
        )

        actual_z = (
            self.spawn_z
            if self.spawn_z is not None
            else self.z
        )

        return {
            "model_file": self.model_file,
            "model_name": self.model_name,
            # Actual Gazebo ENU spawn coordinates.
            "x": actual_x,
            "y": actual_y,
            "z": actual_z,
            # Original placement configuration.
            "spawn_reference": self.spawn_reference,
            "forward": self.forward,
            "right": self.right,
            "down": self.down,
        }

    # --------------------------------------------------
    # Calculate Position Relative to Direction of Travel
    # --------------------------------------------------

    def calculate_relative_spawn_position(self):

        if self.vehicle_state_provider is None:

            raise RuntimeError(
                "Vehicle state provider is unavailable."
            )

        state = self.vehicle_state_provider()

        if state is None:

            raise RuntimeError(
                "Vehicle state is unavailable."
            )

        position = state.get("position")
        velocity = state.get("velocity")

        if position is None or velocity is None:

            raise RuntimeError(
                "Vehicle position or velocity is unavailable."
            )

        if len(position) != 3 or len(velocity) != 3:

            raise ValueError(
                "Vehicle position and velocity must have "
                "three components."
            )

        # Validate vehicle-state timestamps.
        state_timestamp = state.get("timestamp")
        current_timestamp = state.get("current_timestamp")

        if state_timestamp is None or current_timestamp is None:

            raise RuntimeError(
                "Vehicle-state timestamps are unavailable."
            )

        try:

            state_timestamp = float(state_timestamp)
            current_timestamp = float(current_timestamp)

        except (TypeError, ValueError):

            raise ValueError(
                "Vehicle-state timestamps must be numeric."
            )

        if not math.isfinite(state_timestamp) or not math.isfinite(current_timestamp):

            raise ValueError(
                "Vehicle-state timestamps must be finite."
            )

        state_age = current_timestamp - state_timestamp

        if state_age < 0.0:

            raise RuntimeError(
                "Vehicle-state timestamp is in the future."
            )

        if state_age > self.MAX_STATE_AGE:

            raise RuntimeError(
                f"Vehicle state is stale ({state_age:.3f} seconds old)."
            )

        try:

            north, east, down_position = map(float, position)

            velocity_north = float(velocity[0])
            velocity_east = float(velocity[1])

        except (TypeError, ValueError, OverflowError):

            raise ValueError(
                "Vehicle position and velocity must contain "
                "valid numeric values."
            )

        values = [
            north,
            east,
            down_position,
            velocity_north,
            velocity_east,
        ]

        if not all(math.isfinite(value) for value in values):

            raise ValueError(
                "Vehicle position and velocity must be finite."
            )

        horizontal_speed = math.hypot(
            velocity_north,
            velocity_east,
        )

        if horizontal_speed < self.MIN_HORIZONTAL_SPEED:

            raise RuntimeError(
                "Horizontal vehicle speed is too low for "
                "direction-of-travel obstacle placement."
            )

        # Unit vector in the horizontal direction of travel.
        forward_north = velocity_north / horizontal_speed
        forward_east = velocity_east / horizontal_speed

        # Right-hand perpendicular vector in NED.
        right_north = -forward_east
        right_east = forward_north

        # Calculate obstacle position in PX4 Local NED.
        spawn_north = (
            north
            + self.forward * forward_north
            + self.right * right_north
        )

        spawn_east = (
            east
            + self.forward * forward_east
            + self.right * right_east
        )

        spawn_down = down_position + self.down

        # Convert PX4 Local NED position to Gazebo ENU.
        spawn_x = spawn_east
        spawn_y = spawn_north
        spawn_z = -spawn_down

        return spawn_x, spawn_y, spawn_z

    # --------------------------------------------------
    # Spawn Confirmation Helper
    # --------------------------------------------------

    @staticmethod
    def _spawn_succeeded(result):

        if result is None:

            return False

        if result.returncode != 0:

            return False

        response = result.stdout or ""

        return re.search(
            r"\bdata\s*:\s*true\b",
            response,
            flags=re.IGNORECASE,
        ) is not None

    # --------------------------------------------------
    # Event Lifecycle
    # --------------------------------------------------

    def on_enter(self):

        if self.logger is not None:

            self.logger.info(
                f"Spawning {self.model_name}"
            )

        # Drone-relative placement.
        if self.spawn_reference == "direction_of_travel":

            try:

                spawn_x, spawn_y, spawn_z = (
                    self.calculate_relative_spawn_position()
                )

            except (RuntimeError, ValueError) as error:

                if self.logger is not None:

                    self.logger.error(
                        f"Cannot spawn {self.model_name}: {error}"
                    )

                return False

        # Existing fixed-coordinate placement.
        else:

            spawn_x = self.x
            spawn_y = self.y
            spawn_z = self.z

        # Store the resolved Gazebo ENU spawn coordinates.
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
        self.spawn_z = spawn_z

        if self.logger is not None:

            self.logger.info(
                f"Obstacle spawn position (Gazebo ENU): "
                f"x={spawn_x:.2f}, "
                f"y={spawn_y:.2f}, "
                f"z={spawn_z:.2f}"
            )

        try:

            result = self.manager.spawn_model(
                model_file=self.model_file,
                model_name=self.model_name,
                x=spawn_x,
                y=spawn_y,
                z=spawn_z,
            )

        except Exception as error:

            if self.logger is not None:

                self.logger.error(
                    f"Obstacle spawn command failed for "
                    f"{self.model_name}: {error}"
                )

            return False

        if not self._spawn_succeeded(result):

            if self.logger is not None:

                self.logger.error(
                    f"Gazebo did not confirm spawning "
                    f"{self.model_name}. "
                    f"Return code: {getattr(result, 'returncode', None)}; "
                    f"response: {getattr(result, 'stdout', '')}"
                )

            return False

        if self.logger is not None:

            self.logger.info(
                f"Successfully spawned {self.model_name}"
            )

        return True

    # --------------------------------------------------

    def on_update(self):
        pass

    # --------------------------------------------------

    def on_exit(self):
        pass
