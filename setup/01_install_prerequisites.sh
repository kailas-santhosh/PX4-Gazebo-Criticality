#!/usr/bin/env bash

set -e

source "$(dirname "$0")/00_common.sh"

info "Initializing development environment..."

# rosdep initialization (only once)
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
    info "Initializing rosdep..."
    rosdep init
else
    info "rosdep already initialized."
fi

info "Updating rosdep database..."
rosdep update

info "Development environment initialized."
