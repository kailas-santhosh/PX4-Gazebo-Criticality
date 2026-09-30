#!/usr/bin/env bash

source "$(dirname "$0")/00_common.sh"

info "Installing PX4 dependencies..."

require_command bash

require_directory "$PX4_DIR"

cd "$PX4_DIR"

bash Tools/setup/ubuntu.sh --no-sim-tools

info "PX4 dependencies installed successfully."
