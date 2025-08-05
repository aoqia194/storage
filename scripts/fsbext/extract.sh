#!/bin/bash

shopt -s nullglob

TARGET_DIR="$1"
TARGET_EXT="$2"
# COMMAND="$3"

if [[ -z "$TARGET_DIR" || -z "$TARGET_EXT" ]]; then
    echo "Usage: $0 <UNPACKED_CSB_DIR> <TARGET_EXT>"
    exit 1
fi

FSB_NAME=$(basename "$TARGET_DIR")
RAW_NAME="$FSB_NAME"_EXTRACTED
mkdir -p "$RAW_NAME"
cd "$TARGET_DIR"

for file in *."$TARGET_EXT"; do
    # $COMMAND
    /mnt/c/github/fsbext/fsbext -A -d "../$RAW_NAME" "$file"
done
