#!/usr/bin/env bash

# Fail fast on:
# - command errors
# - unset variables
# - pipeline failures
set -euo pipefail

# ---------- Helpers ----------
error() {
    echo "❌ ERROR: $1" >&2
    exit 1
}

info() {
    echo "✅ $1"
}

trap 'error "Script failed at line $LINENO"' ERR

# ---------- Preconditions ----------
command -v python3 >/dev/null 2>&1 || error "python3 is not installed"
command -v pip >/dev/null 2>&1 || error "pip is not installed"

REQ_FILE="requirements.txt"
VENV_DIR="venv"

[[ -f "$REQ_FILE" ]] || error "$REQ_FILE not found in current directory"

# ---------- Create virtual environment ----------
if [[ ! -d "$VENV_DIR" ]]; then
    info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR" || error "Failed to create virtual environment"
else
    info "Virtual environment already exists, skipping creation"
fi

# ---------- Activate virtual environment ----------
info "Activating virtual environment..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate" || error "Failed to activate virtual environment"

# ---------- Upgrade pip (strongly recommended) ----------
info "Upgrading pip..."
pip install --upgrade pip || error "Failed to upgrade pip"

# ---------- Install dependencies ----------
info "Installing Python dependencies..."
pip install -r "$REQ_FILE" || error "Failed to install Python dependencies"

# ---------- Verify ----------
python -c "import sys; print('Using Python:', sys.executable)" \
    || error "Python verification failed"

info "Virtual environment setup completed successfully!"
