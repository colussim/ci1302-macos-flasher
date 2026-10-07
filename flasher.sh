#!/usr/bin/env bash
# Author: Emmanuel COLUSSI
# Native macOS helper for complete CI1302 images; no automatic device selection.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$PROJECT_ROOT/scripts/common.sh"

usage() {
    cat <<'USAGE'
Usage:
  ./flasher.sh install
  ./flasher.sh list
  ./flasher.sh inspect FIRMWARE.bin [--sha256 EXPECTED]
  ./flasher.sh probe PORT
  ./flasher.sh flash PORT FIRMWARE.bin [--sha256 EXPECTED]

Supported USB interface: CH340 VID 1A86 / PID 7523.
Probe loads a RAM update agent without erasing/writing Flash.
Flash erases/writes the complete image; press Debug Rst only when requested.
Use a successful probe before flashing and preserve the original firmware.
USAGE
}

operation="${1:-help}"
image=""
expected=""
port=""
case "$operation" in
    help|--help|-h) usage; exit 0 ;;
    install|list)
        [[ $# -eq 1 ]] || fail "Unexpected arguments for $operation"
        ;;
    inspect)
        [[ $# -eq 2 || $# -eq 4 ]] || fail "Usage: ./flasher.sh inspect FIRMWARE.bin [--sha256 EXPECTED]"
        image="$2"
        if [[ $# -eq 4 ]]; then
            [[ "$3" == --sha256 ]] || fail "Unknown option: $3"
            expected="$4"
            [[ -n "$expected" ]] || fail "Expected SHA-256 must not be empty"
        fi
        ;;
    probe)
        [[ $# -eq 2 ]] || fail "Usage: ./flasher.sh probe PORT"
        port="$2"
        ;;
    flash)
        [[ $# -eq 3 || $# -eq 5 ]] || fail "Usage: ./flasher.sh flash PORT FIRMWARE.bin [--sha256 EXPECTED]"
        port="$2"
        image="$3"
        if [[ $# -eq 5 ]]; then
            [[ "$4" == --sha256 ]] || fail "Unknown option: $4"
            expected="$5"
            [[ -n "$expected" ]] || fail "Expected SHA-256 must not be empty"
        fi
        ;;
    *) usage >&2; fail "Unknown command: $operation" ;;
esac

require_macos
if [[ "$operation" == install ]]; then
    exec bash "$PROJECT_ROOT/scripts/install-citool.sh"
fi
require_tool

case "$operation" in
    list) exec "$TOOL" list ;;
    inspect) inspect_image "$image" "$expected" ;;
    probe)
        validate_port "$port"
        printf 'Probe does not erase/write Flash. Wait for MaskROM, then press Debug Rst.\n'
        exec "$TOOL" probe --port "$port" --manual-reset --connect-timeout 60 \
            --initial-baud 115200 --agent-baud 460800 --timeout-ms 8000
        ;;
    flash)
        inspect_image "$image" "$expected"
        validate_port "$port"
        printf 'Writing the complete CI1302 image. Wait for MaskROM, then press Debug Rst.\n'
        printf 'Keep power connected until programming and CRC verification finish.\n'
        exec "$TOOL" flash --port "$port" --manual-reset --connect-timeout 60 \
            --initial-baud 115200 --agent-baud 460800 --flash-baud 230400 \
            --timeout-ms 8000 -- "$image"
        ;;
esac
