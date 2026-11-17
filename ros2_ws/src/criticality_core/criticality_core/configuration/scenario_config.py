from dataclasses import dataclass, field
from typing import List, Optional


# ==========================================================
# Experiment
# ==========================================================

@dataclass
class ExperimentConfig:

    name: str = "default_experiment"

    random_seed: Optional[int] = None

    max_duration: float = 180.0


# ==========================================================
# Navigation
# ==========================================================

@dataclass
class NavigationConfig:

    mode: str = "fixed_waypoints"

    # Moving-target navigation parameters

    follow_distance: float = 3.0

    # Desired UAV altitude above the Gazebo world ground

    follow_altitude: float = 3.0

    # Maximum permitted age of target data

    target_timeout: float = 1.0

    # Minimum target speed required to estimate direction

    minimum_target_speed: float = 0.1


# ==========================================================
# Trigger
# ==========================================================

@dataclass
class TriggerConfig:

    # "zone" or "time"
    type: str = "zone"

    # Spatial trigger fields
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    radius: Optional[float] = None

    # Time trigger fields
    delay: Optional[float] = None
    duration: Optional[float] = None


# ==========================================================
# Event Parameters
# ==========================================================

@dataclass
class ParameterConfig:

    sensor: Optional[str] = None

    model_file: Optional[str] = None

    model_name: Optional[str] = None

    spawn: Optional[dict] = None

    minimum_percentage: Optional[float] = None


# ==========================================================
# Event
# ==========================================================

@dataclass
class EventConfig:

    name: str

    id: Optional[str] = None

    type: str = ""

    enabled: bool = True

    severity: str = "medium"

    trigger: TriggerConfig = field(
        default_factory=TriggerConfig
    )

    parameters: ParameterConfig = field(
        default_factory=ParameterConfig
    )


# ==========================================================
# Logging
# ==========================================================

@dataclass
class LoggingConfig:

    save_images: bool = True

    save_imu: bool = True

    save_groundtruth: bool = True

    save_criticality_labels: bool = True


# ==========================================================
# Root Configuration
# ==========================================================

@dataclass
class ScenarioConfig:

    experiment: ExperimentConfig = field(
        default_factory=ExperimentConfig
    )

    navigation: NavigationConfig = field(
        default_factory=NavigationConfig
    )

    events: List[EventConfig] = field(
        default_factory=list
    )

    logging: LoggingConfig = field(
        default_factory=LoggingConfig
    )
