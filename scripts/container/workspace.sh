#!/bin/bash

# Source ROS 2
source /opt/ros/jazzy/setup.bash

# Source workspace if it exists
if [ -f /workspace/ros2_ws/install/setup.bash ]; then
    source /workspace/ros2_ws/install/setup.bash
fi

# Activate Python virtual environment
if [ -f /workspace/.venv/bin/activate ]; then
    source /workspace/.venv/bin/activate
fi

echo
echo "========================================="
echo " PX4 Gazebo Criticality Workspace Ready"
echo "========================================="
echo

cd /workspace

