#!/usr/bin/env bash

set -e

echo "Stopping development container..."

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

cd "$PROJECT_ROOT/docker"

docker compose down
