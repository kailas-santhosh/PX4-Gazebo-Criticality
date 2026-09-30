#!/usr/bin/env bash

source "$(dirname "$0")/00_common.sh"

info "Installing Micro XRCE DDS Agent..."

require_command git
require_command cmake
require_command make

mkdir -p "$XRCE_DIR"

# ----------------------------------------------------------
# Clone repository
# ----------------------------------------------------------

clone_repo_if_missing \
    "$XRCE_REPO" \
    "$XRCE_AGENT_DIR"

checkout_commit \
    "$XRCE_AGENT_DIR" \
    "$XRCE_COMMIT"

# ----------------------------------------------------------
# Build
# ----------------------------------------------------------

cd "$XRCE_AGENT_DIR"

git submodule update --init --recursive

rm -rf build
mkdir -p build

cd build

cmake ..

make -j"$(nproc)"

# ----------------------------------------------------------
# Verify build
# ----------------------------------------------------------

if [ ! -x "$XRCE_AGENT_DIR/build/MicroXRCEAgent" ]; then
    error "MicroXRCEAgent build failed."
fi

info "Micro XRCE DDS Agent built successfully."

echo
echo "Executable:"
echo "  $XRCE_AGENT_DIR/build/MicroXRCEAgent"
echo
echo "The executable is available automatically through docker/env.sh."
