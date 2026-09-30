#!/usr/bin/env bash

# ==========================================================
# PX4-Gazebo-Criticality
# Runtime Environment
#
# Automatically sourced by ~/.bashrc
# ==========================================================

# ----------------------------------------------------------
# ROS 2
# ----------------------------------------------------------

if [ -f /opt/ros/jazzy/setup.bash ]; then
    source /opt/ros/jazzy/setup.bash
fi

# ----------------------------------------------------------
# ROS Workspace
# ----------------------------------------------------------

if [ -f /workspace/ros2_ws/install/setup.bash ]; then
    source /workspace/ros2_ws/install/setup.bash
fi

# ----------------------------------------------------------
# Python Virtual Environment
# ----------------------------------------------------------

if [ -f /workspace/.venv/bin/activate ]; then
    source /workspace/.venv/bin/activate
fi

# ----------------------------------------------------------
# Project Environment
# ----------------------------------------------------------

export PX4_PROJECT_ROOT="/workspace"
export PX4_AUTOPILOT="/workspace/robotics/PX4-Autopilot"
export ROS_WS="/workspace/ros2_ws"
export XRCE_AGENT_DIR="/workspace/micro-xrce-dds/Micro-XRCE-DDS-Agent"
export PATH="$XRCE_AGENT_DIR/build:$PATH"

# ----------------------------------------------------------
# Aliases
# ----------------------------------------------------------

alias doctor="/workspace/scripts/container/doctor.sh"

alias build="/workspace/scripts/container/build.sh"

alias clean="/workspace/scripts/container/clean.sh"

alias sim="/workspace/scripts/container/run_sim.sh"

alias agent="MicroXRCEAgent udp4 -p 8888"

alias ws="cd /workspace"

alias px4="cd /workspace/robotics/PX4-Autopilot"

alias rosws="cd /workspace/ros2_ws"

alias setup="cd /workspace/setup"
