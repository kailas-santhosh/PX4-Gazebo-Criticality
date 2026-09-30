#!/usr/bin/env bash

set -e

if [ -f /workspace/docker/env.sh ]; then
    source /workspace/docker/env.sh
fi

echo
echo "======================================"
echo " PX4-Gazebo-Criticality Development"
echo "======================================"
echo

source /workspace/docker/env.sh

exec "$@"
