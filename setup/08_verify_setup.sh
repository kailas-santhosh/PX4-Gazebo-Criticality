#!/usr/bin/env bash

source "$(dirname "$0")/00_common.sh"

info "Verifying PX4-Gazebo-Criticality setup..."

echo

# ----------------------------------------------------------
# Directories
# ----------------------------------------------------------

require_directory "$PROJECT_ROOT"
require_directory "$PX4_DIR"
require_directory "$XRCE_AGENT_DIR"
require_directory "$ROS_WS"
require_directory "$ROS_SRC"

echo "[OK] Project directories"

# ----------------------------------------------------------
# Commands
# ----------------------------------------------------------

require_command git
require_command cmake
require_command make
require_command python3
require_command pip3
require_command colcon
require_command rosdep
require_command MicroXRCEAgent

echo "[OK] Required commands"

# ----------------------------------------------------------
# ROS
# ----------------------------------------------------------

if [ ! -f /opt/ros/jazzy/setup.bash ]; then
    error "ROS 2 Jazzy not found."
fi

source_ros

echo "[OK] ROS 2 Jazzy"

# ----------------------------------------------------------
# Gazebo
# ----------------------------------------------------------

if command -v gz >/dev/null 2>&1; then
    echo "[OK] Gazebo Harmonic"
else
    error "Gazebo not found."
fi

# ----------------------------------------------------------
# PX4
# ----------------------------------------------------------

PX4_HEAD=$(git -C "$PX4_DIR" rev-parse HEAD)

if [ "$PX4_HEAD" != "$PX4_COMMIT" ]; then
    error "PX4 commit mismatch."
fi

echo "[OK] PX4 commit"

# ----------------------------------------------------------
# Micro XRCE DDS Agent
# ----------------------------------------------------------

XRCE_HEAD=$(git -C "$XRCE_AGENT_DIR" rev-parse HEAD)

if [ "$XRCE_HEAD" != "$XRCE_COMMIT" ]; then
    error "Micro XRCE DDS Agent commit mismatch."
fi

echo "[OK] Micro XRCE DDS Agent"

# ----------------------------------------------------------
# px4_msgs
# ----------------------------------------------------------

PX4_MSGS_HEAD=$(git -C "$ROS_SRC/px4_msgs" rev-parse HEAD)

if [ "$PX4_MSGS_HEAD" != "$PX4_MSGS_COMMIT" ]; then
    error "px4_msgs commit mismatch."
fi

echo "[OK] px4_msgs"

# ----------------------------------------------------------
# px4_ros_com
# ----------------------------------------------------------

PX4_ROS_COM_HEAD=$(git -C "$ROS_SRC/px4_ros_com" rev-parse HEAD)

if [ "$PX4_ROS_COM_HEAD" != "$PX4_ROS_COM_COMMIT" ]; then
    error "px4_ros_com commit mismatch."
fi

echo "[OK] px4_ros_com"

# ----------------------------------------------------------
# ROS Workspace
# ----------------------------------------------------------

if [ ! -d "$ROS_WS/install" ]; then
    error "ROS workspace has not been built."
fi

echo "[OK] ROS workspace"

# ----------------------------------------------------------
# Python Virtual Environment
# ----------------------------------------------------------

if [ ! -d "$VENV_DIR" ]; then
    error "Python virtual environment not found."
fi

source "$VENV_DIR/bin/activate"

python --version >/dev/null

deactivate

echo "[OK] Python virtual environment"

# ----------------------------------------------------------
# Docker
# ----------------------------------------------------------

if command -v docker >/dev/null 2>&1; then
    echo "[OK] Docker"
else
    echo "[WARN] Docker not found (ignored if running inside container)"
fi

# ----------------------------------------------------------
# Summary
# ----------------------------------------------------------

echo
echo "=========================================="
echo "PX4-Gazebo-Criticality setup verified."
echo "Environment is ready."
echo "=========================================="
