#!/usr/bin/env bash

# Ensure setup scripts are executed inside the Docker container
if [ ! -f "/.dockerenv" ]; then
    echo "[ERROR] These setup scripts must be run inside the Docker container."
    echo
    echo "Build and start the container first:"
    echo "  cd docker"
    echo "  docker compose build"
    echo "  cd .."
    echo "  ./scripts/host/start_dev.sh"
    exit 1
fi

set -euo pipefail

# ==========================================================
# PX4-Gazebo-Criticality
# Common functions used by all setup scripts
# ==========================================================

# ----------------------------------------------------------
# Project paths
# ----------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SETUP_DIR="$PROJECT_ROOT/setup"

ROBOTICS_DIR="$PROJECT_ROOT/robotics"
PX4_DIR="$ROBOTICS_DIR/PX4-Autopilot"

XRCE_DIR="$PROJECT_ROOT/micro-xrce-dds"
XRCE_AGENT_DIR="$XRCE_DIR/Micro-XRCE-DDS-Agent"

ROS_WS="$PROJECT_ROOT/ros2_ws"
ROS_SRC="$ROS_WS/src"

VENV_DIR="$PROJECT_ROOT/.venv"

# ----------------------------------------------------------
# Load pinned versions
# ----------------------------------------------------------

source "$SETUP_DIR/versions.txt"

# ----------------------------------------------------------
# Logging helpers
# ----------------------------------------------------------

source_ros() {
    set +u
    source /opt/ros/jazzy/setup.bash
    set -u
}

info() {
    echo "[INFO] $*"
}

warn() {
    echo "[WARN] $*"
}

error() {
    echo "[ERROR] $*" >&2
    exit 1
}

# ----------------------------------------------------------
# Validation helpers
# ----------------------------------------------------------

require_command() {

    command -v "$1" >/dev/null 2>&1 || \
        error "Required command not found: $1"

}

require_directory() {

    [ -d "$1" ] || \
        error "Directory does not exist: $1"

}

require_file() {

    [ -f "$1" ] || \
        error "File does not exist: $1"

}

# ----------------------------------------------------------
# Git helpers
# ----------------------------------------------------------

clone_repo_if_missing() {

    local REPO="$1"
    local DEST="$2"

    if [ -d "$DEST/.git" ]; then
        info "Repository already exists:"
        echo "       $DEST"
        return
    fi

    git clone "$REPO" "$DEST"

}

checkout_commit() {

    local DIR="$1"
    local COMMIT="$2"

    require_directory "$DIR"

    git -C "$DIR" fetch --all --tags

    git -C "$DIR" checkout "$COMMIT"

}

# ----------------------------------------------------------
# End
# ----------------------------------------------------------
