#!/usr/bin/env bash

source "$(dirname "$0")/00_common.sh"

info "Building ROS 2 workspace..."

require_directory "$ROS_WS"
require_directory "$ROS_SRC"

# Source ROS 2
source_ros

cd "$ROS_WS"

info "Installing ROS package dependencies..."

rosdep install \
    --from-paths src \
    --ignore-src \
    -r \
    -y

info "Building workspace..."

colcon build

info "ROS 2 workspace built successfully."

echo
echo "Workspace: $ROS_WS"
