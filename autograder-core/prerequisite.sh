#!/usr/bin/env bash

# Exit immediately on:
# - any command failure
# - unset variables
# - failures in pipelines
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
if [[ "$EUID" -eq 0 ]]; then
    error "Do NOT run this script as root. Run as a normal user with sudo access."
fi

command -v sudo >/dev/null 2>&1 || error "sudo is required but not installed."

# ---------- APT update ----------
info "Updating package lists..."
sudo apt update -y || error "apt update failed"

# ---------- Install system packages ----------
info "Installing python3-pip..."
sudo apt install -y python3-pip || error "Failed to install python3-pip"

info "Installing tesseract-ocr..."
sudo apt install -y tesseract-ocr || error "Failed to install tesseract-ocr"

# ---------- Install Poetry ----------
if ! command -v poetry >/dev/null 2>&1; then
    info "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 - \
        || error "Poetry installation failed"
else
    info "Poetry already installed, skipping"
fi

# ---------- Ensure PATH ----------
POETRY_BIN="$HOME/.local/bin"

if [[ ":$PATH:" != *":$POETRY_BIN:"* ]]; then
    info "Adding Poetry to PATH in ~/.bashrc"
    echo "export PATH=\"$POETRY_BIN:\$PATH\"" >> ~/.bashrc
else
    info "Poetry path already present in PATH"
fi

# Apply PATH for current shell
export PATH="$POETRY_BIN:$PATH"

# ---------- Verify Poetry ----------
command -v poetry >/dev/null 2>&1 || error "Poetry not found in PATH after installation"

# ---------- Install Python dependencies ----------
info "Installing Python dependencies via Poetry..."
poetry install || error "poetry install failed"

info "🎉 All prerequisites installed successfully!"
