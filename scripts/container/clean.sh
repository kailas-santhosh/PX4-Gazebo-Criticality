#!/usr/bin/env bash

set -e

echo "======================================"
echo " Cleaning ROS 2 Workspace"
echo "======================================"

WORKSPACE="/workspace/ros2_ws"

if [ ! -d "$WORKSPACE" ]; then
    echo "Workspace not found:"
    echo "$WORKSPACE"
    exit 1
fi

cd "$WORKSPACE"

echo
echo "Removing ROS build artifacts..."

rm -rf build install log

echo
echo "Workspace cleaned."

echo
echo "Run 'build' to rebuild the workspace."
