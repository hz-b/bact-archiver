#!/bin/sh
set -xv

input=$1
output=$2
PROTOC=protoc
DIRNAME=dirname

SRC_DIR=`"$DIRNAME" "$input"`
BUILD_DIR=`"$DIRNAME" "$output"`

echo "$PROTOC" --proto_path="$SRC_DIR" --python_out="$BUILD_DIR" "$input"
"$PROTOC" --proto_path="$SRC_DIR" --python_out="$BUILD_DIR" "$input"


