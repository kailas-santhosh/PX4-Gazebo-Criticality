#!/usr/bin/env bash

source "$(dirname "$0")/00_common.sh"

info "Cloning PX4-Autopilot..."

require_command git

mkdir -p "$ROBOTICS_DIR"

clone_repo_if_missing \
    "https://github.com/PX4/PX4-Autopilot.git" \
    "$PX4_DIR"

info "Checking out PX4 commit..."

checkout_commit \
    "$PX4_DIR" \
    "$PX4_COMMIT"

info "Updating PX4 submodules..."

git -C "$PX4_DIR" submodule sync --recursive

git -C "$PX4_DIR" submodule update \
    --init \
    --recursive \
    --jobs "$(nproc)"

git -C "$PX4_DIR" submodule status --recursive

if git -C "$PX4_DIR" submodule status --recursive | grep -qE '^[+-]'; then
    error "One or more PX4 submodules failed to initialize."
fi

info "PX4 successfully prepared."

echo
echo "Repository : $PX4_DIR"
echo "Commit     : $(git -C "$PX4_DIR" rev-parse HEAD)"
