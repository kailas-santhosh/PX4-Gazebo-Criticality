"""
Configuration package for the Criticality Framework.

Provides:

- Scenario configuration dataclasses
- YAML configuration loading
- Configuration validation
"""

from .scenario_config import ScenarioConfig
from .config_loader import load_scenario_config
from .config_validator import validate_config

__all__ = [
    "ScenarioConfig",
    "load_scenario_config",
    "validate_config",
]
