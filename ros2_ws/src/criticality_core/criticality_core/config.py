"""
Global configuration for the Criticality Framework.
"""

from pathlib import Path

# ======================================================
# Gazebo World
# ======================================================

WORLD_NAME = "default"

# ======================================================
# Gazebo Services
# ======================================================

CREATE_SERVICE = f"/world/{WORLD_NAME}/create"
REMOVE_SERVICE = f"/world/{WORLD_NAME}/remove"
SET_POSE_SERVICE = f"/world/{WORLD_NAME}/set_pose"

# ======================================================
# Default Orientation
# ======================================================

ROLL = 0.0
PITCH = 0.0
YAW = 0.0

QUAT_W = 1.0

# ======================================================
# Project Root
# ======================================================

PROJECT_ROOT = Path("/workspace")

# ======================================================
# Dataset Paths
# ======================================================

DATASETS_DIR = PROJECT_ROOT / "datasets"

# ======================================================
# ROS Workspace
# ======================================================

ROS2_WS = PROJECT_ROOT / "ros2_ws"

# ======================================================
# Criticality Core Package
# ======================================================

PACKAGE_ROOT = (
    ROS2_WS
    / "src"
    / "criticality_core"
)

CRITICALITY_CORE = (
    PACKAGE_ROOT
    / "criticality_core"
)

MODELS_DIR = (
    PACKAGE_ROOT
    / "models"
)
