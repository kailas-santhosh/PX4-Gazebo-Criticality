#!/usr/bin/env bash

source "$(dirname "$0")/00_common.sh"

info "Creating Python virtual environment..."

require_command python3
require_command pip3

# ----------------------------------------------------------
# Create virtual environment
# ----------------------------------------------------------

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    info "Virtual environment created."
else
    info "Virtual environment already exists."
fi

# ----------------------------------------------------------
# Activate virtual environment
# ----------------------------------------------------------

source "$VENV_DIR/bin/activate"

python -m pip install --upgrade \
    pip \
    setuptools \
    wheel

# ----------------------------------------------------------
# Install PX4 Python requirements
# ----------------------------------------------------------

require_file "$PX4_DIR/Tools/setup/requirements.txt"

pip install -r \
    "$PX4_DIR/Tools/setup/requirements.txt"

# ----------------------------------------------------------
# Install project Python requirements
# ----------------------------------------------------------

if [ -f "$PROJECT_ROOT/venv/requirements.txt" ]; then

    pip install -r \
        "$PROJECT_ROOT/venv/requirements.txt"

fi

deactivate

info "Python virtual environment configured successfully."

echo
echo "Virtual Environment : $VENV_DIR"
