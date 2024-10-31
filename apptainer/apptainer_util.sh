#!/usr/bin/env bash
set -eu
IMAGES_DIR="images"
BASE_IMAGE="julia:latest"
APP_NAME="medusa"

base() {
    mkdir -p "$IMAGES_DIR"
    apptainer build "$IMAGES_DIR/julia.sif" "docker://$BASE_IMAGE"
}

build() {
    mkdir -p "$IMAGES_DIR"
    apptainer build "$IMAGES_DIR/$APP_NAME.sif" medusa.apptainer
}

run() {
    apptainer run "$IMAGES_DIR/$APP_NAME.sif" "$@"
}

# Pass arguments to the script
case $1 in
    (base)
        base
        ;;
    (build)
        build
        ;;
    (run)
        shift
        run "$@"
        ;;
    (*) exit 1
esac
