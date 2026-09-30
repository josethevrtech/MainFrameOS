#!/bin/bash
# Arch/ALARM development helper; requires existing Qt6/KF6/SDL3 development files.
set -euo pipefail
here=$(cd -- "$(dirname -- "$0")" && pwd)
out=${1:?Usage: build.sh NEW_OUTPUT_DIRECTORY}
mkdir "$out"
out=$(realpath "$out")
/usr/lib/qt6/moc "$here/controller.cpp" -o "$out/controller.moc"
c++ -std=c++17 -Wall -Wextra -Werror -O2 "$here/controller.cpp" -I"$out" -I/usr/include/KF6/KGlobalAccel $(pkg-config --cflags --libs Qt6Widgets Qt6DBus) -lKF6GlobalAccel -o "$out/frame-control-service"
cc -Wall -Wextra -Werror -O2 "$here/client.c" $(pkg-config --cflags --libs sdl3) -o "$out/frame-input-client"
