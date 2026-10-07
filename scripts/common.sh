#!/usr/bin/env bash
# Author: Emmanuel COLUSSI
# Shared validation for the pinned native tool and user-supplied images.

TOOL_VERSION="1.2.2"
ARCHIVE_SHA256="44caacf0d4e832ca2edcb047ef2deaaec0393262b63fd233ac65d18d91ab6e50"
EXECUTABLE_SHA256="f9f07bc1cfaab4875470dfdd1890977bef3be860bb8c5fb73e447fb51febb331"
TOOL_URL="https://github.com/coloz/arduino-ci130x/releases/download/citool-cli-v1.2.2/citool-cli-1.2.2-macos-universal.tar.gz"
TOOL_DIRECTORY="$PROJECT_ROOT/.tools/citool-cli/$TOOL_VERSION"
TOOL="$TOOL_DIRECTORY/citool-cli"

fail() {
    printf 'Error: %s\n' "$1" >&2
    exit 1
}

require_macos() {
    [[ "$(uname -s)" == Darwin ]] || fail "This helper requires macOS"
}

file_sha256() {
    local result
    result="$(shasum -a 256 < "$1")" || fail "Cannot hash: $1"
    printf '%s\n' "${result%% *}"
}

verify_sha256() {
    [[ -f "$1" ]] || fail "Missing file: $1"
    [[ "$(file_sha256 "$1")" == "$2" ]] || fail "SHA-256 mismatch: $1"
}

require_tool() {
    verify_sha256 "$TOOL" "$EXECUTABLE_SHA256"
    [[ -x "$TOOL" ]] || fail "Run ./flasher.sh install to install the executable"
}

inspect_image() {
    local image="$1" expected="$2" digest inspection
    [[ -f "$image" && -s "$image" ]] || fail "Firmware must be a nonempty regular file: $image"
    case "$image" in
        *.bin|*.BIN) ;;
        *) fail "Select the complete serial-flash .bin image, not an OTA or resource file" ;;
    esac
    if [[ -n "$expected" ]]; then
        [[ "$expected" =~ ^[[:xdigit:]]{64}$ ]] || fail "Expected SHA-256 must contain exactly 64 hexadecimal characters"
        expected="$(printf '%s' "$expected" | tr '[:upper:]' '[:lower:]')"
        verify_sha256 "$image" "$expected"
    fi
    digest="$(file_sha256 "$image")"
    printf 'Image SHA-256: %s\n' "$digest"
    inspection="$("$TOOL" inspect -- "$image")" || fail "Native firmware inspection failed; no serial programming was started"
    printf '%s\n' "$inspection"
    case "$inspection" in
        *"V2 partition table: chip CI1302,"*) ;;
        *) fail "This helper only accepts complete CI1302 FW_V2 images" ;;
    esac
}

validate_usb_identity() {
    printf '%s\n' "$2" | awk -v port="$1" \
        '$1 == port && index($0, "VID:1A86 PID:7523") { found = 1 } END { exit !found }'
}

validate_port() {
    local port="$1" listing
    case "$port" in
        /dev/cu.usbserial-*|/dev/cu.wchusbserial*) ;;
        *) fail "Use a CH340 /dev/cu.usbserial-* or /dev/cu.wchusbserial* port; USB CDC ports are not accepted" ;;
    esac
    [[ -c "$port" ]] || fail "Serial port is absent: $port"
    listing="$("$TOOL" list)" || fail "Cannot enumerate USB serial interfaces"
    validate_usb_identity "$port" "$listing" \
        || fail "The selected port must identify as CH340 VID 1A86 / PID 7523"
}
