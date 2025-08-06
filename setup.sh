#!/bin/bash
set -e  # Exit on first error


# Detect OS
OS="$(uname -s)"

# ===== Docker =====
if ! command -v docker &>/dev/null; then
    echo "Docker not found. Installing..."
    if [[ "$OS" == "Linux" ]]; then
        # For Ubuntu/Debian
        if command -v apt-get &>/dev/null; then
            sudo apt-get update
            sudo apt-get install -y docker.io
            sudo systemctl enable --now docker
        else
            echo "Unsupported Linux distribution. Please install Docker manually."
            exit 1
        fi
    elif [[ "$OS" == "Darwin" ]]; then
        # macOS
        if command -v brew &>/dev/null; then
            brew install --cask docker
            echo "Please open Docker Desktop manually after installation."
        else
            echo "Homebrew not found. Install Homebrew first: https://brew.sh/"
            exit 1
        fi
    else
        echo "Unsupported operating system. Please install Docker manually."
        exit 1
    fi
else
    echo "Docker is already installed."
fi


# ===== CMake =====
if ! command -v cmake &>/dev/null; then
    echo "CMake not found. Installing..."
    if [[ "$OS" == "Linux" ]]; then
        if command -v apt-get &>/dev/null; then
            sudo apt-get update
            sudo apt-get install -y cmake
        else
            echo "Unsupported Linux distribution. Please install CMake manually."
            exit 1
        fi
    elif [[ "$OS" == "Darwin" ]]; then
        if command -v brew &>/dev/null; then
            brew install cmake
        else
            echo "Homebrew not found. Install Homebrew first: https://brew.sh/"
            exit 1
        fi
    else
        echo "Unsupported operating system. Please install CMake manually."
        exit 1
    fi
else
    echo "CMake is already installed."
fi


# ===== Copy Parser Script =====

PARSER_PY="./assets/parser.py"

SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
DEST_PARSER_PY="$SITE_PACKAGES/asn1tools/parser.py"

if [ ! -f "$PARSER_PY" ]; then
    cp "$PARSER_PY" "$DEST_PARSER_PY"
    echo "Copied parser.py to site-packages."
fi

echo "Setup complete. You can now run the project."


