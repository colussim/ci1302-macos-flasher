# Installation, upgrade, and recovery

## Requirements

Use macOS with Bash 3.2 or newer and its bundled curl, tar, awk, shasum, and
standard file utilities. The upstream Universal executable includes Intel and
Apple Silicon code; the recorded physical test used Apple Silicon/macOS
27.0.1. No Intel hardware regression or minimum-OS-version matrix is available.
Python 3 is only required for development tests. No SDK, Rust compiler,
container runtime, Windows VM, or Wine installation is needed to flash an
already generated image.

Clone this repository and run `./flasher.sh install`. HTTPS is mandatory for
downloads and redirects. The installer verifies the pinned archive before
extracting only expected entries, then verifies the executable before running
its version command. It preserves upstream license/README files. A cached
executable is also checked before reuse; a corrupted existing cache is rejected.

Get a complete CI1302 FW_V2 serial-flash `.bin` from your supplier or a supported
generation platform. For M147, use
[M5Stack's SmartPI procedure](https://docs.m5stack.com/en/guide/module_asr/custom_firmware).
Do not use this installer to generate resources, compile firmware, or convert
an OTA image. Store private firmware under ignored `firmware/`; this repository
ships no factory, custom, or recovery firmware.

## Programming sequence

1. Preserve the original complete vendor firmware and its checksum.
2. Disconnect the host controller and connect only the module's own USB port.
3. Run `list` and confirm CH340 VID 1A86 / PID 7523 and the current port name.
4. Run `inspect` on the full image, optionally supplying a trusted SHA-256.
5. Run `probe`, press manual Debug Rst when prompted, and require a successful
   MaskROM/agent connection. Reset or power-cycle after the probe.
6. Run `flash`, wait for the MaskROM prompt, and press Debug Rst again.
7. Leave power connected through erase, programming, verification, and reset.
8. Require final CRC success and zero exit status, then test the firmware's
   behavior separately.

To save output, use an ignored `logs/` directory. A shell pipeline must preserve
the programmer's exit status:

```sh
mkdir -p logs
set -o pipefail
./flasher.sh flash /dev/cu.usbserial-110 /path/to/firmware.bin 2>&1 | tee logs/flash.log
```

## Upgrades and rollback

The version and both tool digests are fixed in `scripts/common.sh`. Review the
upstream release and its notices, verify digests from the release and package
index, run automated/native offline checks, and repeat a physical module test
before updating the pins. Preserve the previous checkout and its ignored cache
until the new version is validated; each version uses a separate directory.

Reinstalling a tool does not change installed module firmware. Firmware rollback
requires an explicit flash of the original complete compatible vendor image;
there is no automatic on-device rollback. This helper does not back up or read
the currently installed Flash. If an operation fails after erase begins, the
module may not boot its former application; preserve the failure log and use a
validated complete image and successful MaskROM probe before attempting recovery.
Do not change unrelated ESP32/C6/Tab5 firmware to recover CI1302.
