#!/usr/bin/env bash

set -e

echo "======================================"
echo " Building ROS 2 Workspace"
echo "======================================"

WORKSPACE="/workspace/ros2_ws"

echo
echo "[1/4] Checking workspace..."

if [ ! -d "$WORKSPACE" ]; then
    echo "Workspace not found:"
    echo "$WORKSPACE"
    exit 1
fi

echo "Workspace found."

echo
echo "[2/4] Sourcing ROS 2..."

source /opt/ros/jazzy/setup.bash

echo "ROS 2 sourced."

echo
echo "[3/4] Building workspace..."

cd "$WORKSPACE"

colcon build

echo
echo "[4/4] Verifying package..."

source install/setup.bash

if ros2 pkg list | grep -qx "criticality_core"; then
    echo
    echo "======================================"
    echo " Build Successful!"
    echo "======================================"
else
    echo
    echo "Package 'criticality_core' not found after build."
    exit 1
fi
