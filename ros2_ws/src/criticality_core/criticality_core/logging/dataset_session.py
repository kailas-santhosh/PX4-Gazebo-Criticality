#!/usr/bin/env python3

from pathlib import Path

from criticality_core.config import DATASETS_DIR
from criticality_core.logging.sequence_manager import (
    SequenceManager,
)

SESSION_FILE = DATASETS_DIR / ".current_sequence"


def create_new_session():
    """
    Creates a new EuRoC sequence directory and marks it
    as the active dataset session.
    """

    sequence_manager = SequenceManager()

    SESSION_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    SESSION_FILE.write_text(
        str(sequence_manager.sequence_dir)
    )

    return sequence_manager.sequence_dir


def get_current_session():
    """
    Returns the active dataset sequence directory.
    """

    if not SESSION_FILE.exists():

        raise RuntimeError(
            "No active dataset session found. "
            "Start ScenarioRunner before DatasetLogger."
        )

    sequence_dir = Path(
        SESSION_FILE.read_text().strip()
    )

    if not sequence_dir.exists():

        raise RuntimeError(
            f"Dataset session does not exist:\n{sequence_dir}"
        )

    return sequence_dir
