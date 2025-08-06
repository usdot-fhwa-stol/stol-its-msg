#!/bin/bash
set -e

# Store arguments
CMAKE_ARGS="$@"

# Print arguments for debugging
echo "CMake arguments received: $CMAKE_ARGS"

mkdir -p build
rm -rf build/*

cd build
cmake .. $CMAKE_ARGS && make