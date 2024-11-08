#!/usr/bin/env bash
set -eu
IMAGES_DIR="images"

# the name of the docker image to start from
BASE_IMAGE="julia:latest"

# the name of the project
APP_NAME="medusa"

base() {
    mkdir -p "$IMAGES_DIR"
    apptainer build "$IMAGES_DIR/$BASE_IMAGE.sif" "docker://$BASE_IMAGE"
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
