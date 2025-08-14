#!/bin/bash


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

if command -v docker &>/dev/null; then
    if [[ "$OS" == "Linux" ]]; then
        sudo systemctl start docker
    elif [[ "$OS" == "Darwin" ]]; then
        open -a Docker
    fi
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

PARSER_PY="$(realpath ./assets/parser.py)"

if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Error: Python not found."
    exit 1
fi

SITE_PACKAGES=$($PYTHON -c "import site; print(site.getsitepackages()[0])")
DEST_PARSER_PY="$SITE_PACKAGES/asn1tools/parser.py"

echo "Copying parser.py to $DEST_PARSER_PY"

if [ -f "$PARSER_PY" ]; then
    cp "$PARSER_PY" "$DEST_PARSER_PY"
    echo "Copied parser.py to site-packages."
fi

echo "Setup complete. You can now run the project."

