#!/usr/bin/env bash

set -e

echo "======================================"
echo " PX4-Gazebo-Criticality Development"
echo "======================================"

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CONTAINER_NAME="px4-gazebo-criticality"

cd "$PROJECT_ROOT/docker"

echo
echo "[1/4] Checking Docker..."

docker --version >/dev/null
docker compose version >/dev/null

echo "Docker OK"

echo
echo "[2/4] Checking DISPLAY..."

if [ -z "${DISPLAY:-}" ]; then
    echo "DISPLAY is not set."
    exit 1
fi

echo "DISPLAY = $DISPLAY"

echo
echo "[3/4] Enabling X11..."

command -v xhost >/dev/null || {
    echo "xhost is not installed."
    exit 1
}

xhost +local:docker >/dev/null

echo "X11 access granted."

echo
echo "[4/4] Starting development container..."

docker compose up -d

docker exec -it "$CONTAINER_NAME" bash
