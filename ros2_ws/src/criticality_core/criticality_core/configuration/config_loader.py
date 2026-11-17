from dataclasses import fields, is_dataclass, MISSING
from pathlib import Path

import yaml

from ament_index_python.packages import (
    get_package_share_directory,
)

from .scenario_config import (
    ScenarioConfig,
    ExperimentConfig,
    NavigationConfig,
    LoggingConfig,
    EventConfig,
    TriggerConfig,
    ParameterConfig,
)


def _construct_config(
    cls,
    data,
    aliases=None,
):
    """
    Build a dataclass from a YAML mapping.

    Only keys that the dataclass actually declares are passed
    through, so extra YAML keys (e.g. "description", "notes")
    are ignored safely.

    `aliases` maps YAML keys to dataclass fields, so that e.g.
    YAML "id" can populate dataclass "name" when "name" is
    missing. The dataclass field always wins if present.

    Nested dataclass fields (e.g. EventConfig.trigger ->
    TriggerConfig) are recursively constructed from their
    YAML sub-mappings.
    """

    if not isinstance(data, dict):

        raise ValueError(
            f"Expected a mapping for "
            f"{cls.__name__}, got "
            f"{type(data).__name__}."
        )

    known = {

        f.name for f in fields(cls)
    }

    filtered = {

        k: v for k, v in data.items()
        if k in known
    }

    if aliases:

        for yaml_key, field_name in aliases.items():

            if (
                field_name in known
                and field_name not in filtered
                and yaml_key in data
            ):

                filtered[field_name] = data[yaml_key]

    # --------------------------------------------------
    # Recursively construct nested dataclass fields
    # (e.g. EventConfig.trigger -> TriggerConfig,
    #       EventConfig.parameters -> ParameterConfig)
    # --------------------------------------------------

    for f in fields(cls):

        if f.name not in filtered:

            continue

        value = filtered[f.name]

        if (
            is_dataclass(f.type)
            and isinstance(value, dict)
        ):

            filtered[f.name] = _construct_config(
                f.type,
                value,
            )

    missing = [

        f.name
        for f in fields(cls)
        if f.default is MISSING
        and f.default_factory is MISSING
        and f.name not in filtered
    ]

    if missing:

        raise ValueError(
            f"Missing required field(s) for "
            f"{cls.__name__}: {missing}. "
            f"Provided keys: {sorted(data.keys())}"
        )

    return cls(**filtered)


def load_scenario_config(
    config_file: str,
) -> ScenarioConfig:
    """
    Load a scenario configuration from the package's
    config directory.

    Example:
        load_scenario_config("default_scenario.yaml")
    """

    package_share = Path(
        get_package_share_directory(
            "criticality_core"
        )
    )

    config_path = (
        package_share
        / "config"
        / config_file
    )

    if not config_path.exists():

        raise FileNotFoundError(
            f"Configuration file not found:\n"
            f"{config_path}"
        )

    with open(config_path, "r") as file:

        data = yaml.safe_load(file)

    if data is None:

        raise ValueError(
            "Configuration file is empty."
        )

    if not isinstance(data, dict):

        raise ValueError(
            "Configuration root must be a YAML mapping."
        )

    experiment = _construct_config(
        ExperimentConfig,
        data.get("experiment", {}) or {},
    )

    navigation = _construct_config(
        NavigationConfig,
        data.get("navigation", {}) or {},
    )

    logging = _construct_config(
        LoggingConfig,
        data.get("logging", {}) or {},
    )

    events = [

        _construct_config(
            EventConfig,
            event,
            aliases={"id": "name"},
        )

        for event in (data.get("events", []) or [])
    ]

    return ScenarioConfig(

        experiment=experiment,

        navigation=navigation,

        events=events,

        logging=logging,
    )
