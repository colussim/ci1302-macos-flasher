# ADR-0001: Delegate programming to a pinned native engine

Status: Accepted, 2026-10-07.

## Context

The official M147 procedure uses a Windows executable. A reviewed native macOS
citool-cli release accepted a complete SmartPI image and successfully programmed
and CRC-verified one physical M147. Wireless-Tag's embedded updater uses a
different model-update workflow and precompiled ESP32 libraries; it is not a
ready macOS serial flasher. This repository should make the observed native
workflow reusable without distributing private firmware or vendor components.

## Decision

Use Bash and a pinned HTTPS installer for citool-cli 1.2.2 Universal. Verify the
archive and executable digests, preserve upstream notices, require complete
CI1302 FW_V2 images and exact CH340 1A86:7523 identity, and use explicit ports,
manual reset, 60-second connection waits, and the physically tested rates.
Keep firmware/downloads/logs out of Git and expose no network server. Provide
English documentation, including the user-facing quick start.

## Alternatives considered

- Reimplementing the serial protocol: insufficient audited source/protocol
  material and unnecessary recovery risk for this scope.
- Bundling vendor executables/firmware: increases release/licensing and privacy
  obligations; the original pinned download already exists.
- Windows tooling through Wine/VM/container: an additional environment and USB
  access path; no need once a native engine has passed the recorded test.
- A graphical application: extra runtime and UI complexity beyond a reproducible
  terminal workflow.

## Consequences

The helper stays small, dependency-light, and usable without SDK/compiler setup.
It relies on upstream release availability and a third-party executable whose
source was unavailable during review. Digests establish consistency, not source
audit. CI1303/CI1306, other USB adapters, Intel physical tests, and wake-word
validation remain outside the tested scope. Tool upgrades require pin review,
offline checks, and a new recorded physical test.

## Rationale

Preserving the successful native programming sequence and adding explicit
validation is more reliable than implementing an unverified protocol. This is
host tooling, so the firmware project's Go/backend and ESP-IDF patterns do not
apply; no backend service or firmware architecture is introduced.
