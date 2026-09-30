#!/usr/bin/env bash

set -e

echo "======================================"
echo " PX4-Gazebo-Criticality Simulator"
echo "======================================"
echo

echo "[1/3] Checking ROS workspace..."

if [ ! -f /workspace/ros2_ws/install/setup.bash ]; then
    echo
    echo "ROS workspace has not been built."
    echo "Run:"
    echo
    echo "    build"
    echo
    exit 1
fi

echo "[2/3] Entering PX4..."

cd /workspace/robotics/PX4-Autopilot

echo "[3/3] Launching PX4 SITL + Gazebo..."
echo

exec make px4_sitl gz_x500
