#!/usr/bin/env bash

set -e

PASS="[PASS]"
FAIL="[FAIL]"

echo "======================================"
echo " PX4-Gazebo-Criticality Doctor"
echo "======================================"

check() {
    local NAME="$1"
    local CMD="$2"

    if eval "$CMD" >/dev/null 2>&1; then
        printf "%-35s %s\n" "$NAME" "$PASS"
    else
        printf "%-35s %s\n" "$NAME" "$FAIL"
    fi
}

echo
echo "========== Runtime =========="

check "ROS 2 Jazzy" \
    "[ -f /opt/ros/jazzy/setup.bash ]"

check "ROS CLI" \
    "which ros2"

check "Colcon" \
    "which colcon"

check "Gazebo" \
    "which gz"

check "MicroXRCEAgent" "command -v MicroXRCEAgent"

check "Python Virtual Environment" \
    "[ -n \"\$VIRTUAL_ENV\" ]"

echo
echo "========== Workspace =========="

check "Project Root" \
    "[ -d /workspace ]"

check "ROS Workspace" \
    "[ -d /workspace/ros2_ws ]"

check "Workspace Built" \
    "[ -f /workspace/ros2_ws/install/setup.bash ]"

check "PX4 Source" \
    "[ -d /workspace/robotics/PX4-Autopilot ]"

check "Micro XRCE Source" \
    "[ -d /workspace/micro-xrce-dds/Micro-XRCE-DDS-Agent ]"

echo
echo "========== ROS Packages =========="

check "criticality_core" \
    "source /workspace/ros2_ws/install/setup.bash && ros2 pkg list | grep -qx criticality_core"

check "ros_gz_bridge" \
    "source /opt/ros/jazzy/setup.bash && ros2 pkg list | grep -qx ros_gz_bridge"

echo
echo "========== PX4 =========="

check "PX4 Executable" \
    "[ -f /workspace/robotics/PX4-Autopilot/build/px4_sitl_default/bin/px4 ]"

echo
echo "========== GUI =========="

check "DISPLAY" \
    "[ -n \"\$DISPLAY\" ]"

check "X11 Socket" \
    "[ -d /tmp/.X11-unix ]"

echo
echo "======================================"
echo " Runtime Environment Check Complete"
echo "======================================"

echo
echo "If any item shows [FAIL], resolve it before running:"
echo
echo "    agent"
echo "    sim"
echo
