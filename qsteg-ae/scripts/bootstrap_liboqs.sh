#!/usr/bin/env bash
# Build and install liboqs (the native library behind `liboqs-python`) into $HOME/_oqs.
#
# Why this script exists: liboqs-python auto-builds liboqs on first import, but its
# default cmake invocation requires OpenSSL development headers (libssl-dev), which
# are absent on the owner's machine and would need root to install. liboqs builds
# fine without OpenSSL — it falls back to its own SHA3/AES implementations, which
# only affects speed, not the correctness of ML-KEM-768 (FIPS 203).
#
# See docs/decisions/001-pqc-library.md.
#
# Usage:  ./scripts/bootstrap_liboqs.sh [liboqs_version]
# Idempotent: exits early if the shared library is already installed.

set -euo pipefail

LIBOQS_VERSION="${1:-0.16.0}"   # must match the liboqs-python pin in pyproject.toml
PREFIX="${OQS_INSTALL_PATH:-$HOME/_oqs}"

if [[ -f "$PREFIX/lib/liboqs.so" ]]; then
    echo "liboqs already installed at $PREFIX/lib/liboqs.so — nothing to do."
    exit 0
fi

for tool in git cmake make gcc; do
    command -v "$tool" >/dev/null || { echo "ERROR: '$tool' not found on PATH." >&2; exit 1; }
done

BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT

echo "Cloning liboqs $LIBOQS_VERSION..."
git clone --branch "$LIBOQS_VERSION" --depth 1 \
    https://github.com/open-quantum-safe/liboqs "$BUILD_DIR/liboqs"

echo "Configuring (OpenSSL disabled)..."
cmake -S "$BUILD_DIR/liboqs" -B "$BUILD_DIR/liboqs/build" \
    -DBUILD_SHARED_LIBS=ON \
    -DOQS_BUILD_ONLY_LIB=ON \
    -DOQS_USE_OPENSSL=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$PREFIX"

echo "Building..."
cmake --build "$BUILD_DIR/liboqs/build" --parallel "$(nproc)"
cmake --build "$BUILD_DIR/liboqs/build" --target install

echo "Installed liboqs $LIBOQS_VERSION to $PREFIX"
