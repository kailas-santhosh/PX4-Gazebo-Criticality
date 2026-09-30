#!/usr/bin/env bash

source "$(dirname "$0")/00_common.sh"

info "Preparing ROS 2 workspace..."

require_command git
require_directory "$ROS_SRC"

# ----------------------------------------------------------
# Clone px4_msgs
# ----------------------------------------------------------

clone_repo_if_missing \
    "$PX4_MSGS_REPO" \
    "$ROS_SRC/px4_msgs"

checkout_commit \
    "$ROS_SRC/px4_msgs" \
    "$PX4_MSGS_COMMIT"

# ----------------------------------------------------------
# Clone px4_ros_com
# ----------------------------------------------------------

clone_repo_if_missing \
    "$PX4_ROS_COM_REPO" \
    "$ROS_SRC/px4_ros_com"

checkout_commit \
    "$ROS_SRC/px4_ros_com" \
    "$PX4_ROS_COM_COMMIT"

info "ROS 2 repositories prepared successfully."

echo
echo "px4_msgs    : $(git -C "$ROS_SRC/px4_msgs" rev-parse HEAD)"
echo "px4_ros_com : $(git -C "$ROS_SRC/px4_ros_com" rev-parse HEAD)"
