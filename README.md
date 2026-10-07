# CI1302 macOS Flasher

[Français](README.fr.md) · [CLI reference](docs/api/cli.md) · [Troubleshooting](docs/operations/troubleshooting.md)

A small native macOS helper for inspecting, probing, and flashing **CI1302 voice
modules** through a CH340 USB-to-serial interface. Tested with **M5Stack Module
ASR M147** on Apple Silicon. The programming engine is
[citool-cli by coloz](https://github.com/coloz/arduino-ci130x/releases/tag/citool-cli-v1.2.2);
this repository adds a pinned installer, image/USB guards, reproducible commands,
tests, and documentation.

## Quick start

Requirements: macOS, a data-capable USB cable, and a **complete CI1302 FW_V2
serial-flash `.bin` image** from your module supplier or firmware-generation
platform. Bash, curl, tar, awk, and shasum are included with macOS. Python 3 is
only needed for development tests.

```sh
git clone https://github.com/colussim/ci1302-macos-flasher.git
cd ci1302-macos-flasher
./flasher.sh install
./flasher.sh list
./flasher.sh inspect /path/to/firmware.bin
```

Install downloads the pinned **citool-cli 1.2.2 macOS Universal** release over
HTTPS and verifies both archive and executable SHA-256 before execution.
Inspect checks the complete image's CI1302 partition table and CRCs without
opening a serial device. No firmware or third-party executable is included in
this repository.

Connect the **module's own USB-C port**, leaving the host controller/Tab5
disconnected. From `list`, select the CH340 entry with **VID 1A86 / PID 7523**.
Replace the example port with the actual one; do not open both `usbserial` and
`wchusbserial` aliases of the same adapter.

```sh
./flasher.sh probe /dev/cu.usbserial-110
```

When the tool prints `Waiting for a manual device reset into MaskROM...`, press
the module's **Debug Rst** button once. Probe transfers an agent into RAM; it
does **not erase or write Flash**. It changes the running module state, so
reset/power-cycle afterward. Proceed only after a successful probe.

```sh
./flasher.sh flash /dev/cu.usbserial-110 /path/to/firmware.bin
```

Wait for MaskROM and press **Debug Rst again**. Keep the cable connected.
Programming erases/writes the complete image, then checks its CRC. Success
requires Programming and Verifying at 100%, `Flash completed; firmware CRC
verification passed.`, and exit status zero. Then reset/power-cycle and test
your firmware's wake phrase and UART events.

If your supplier gives an expected SHA-256, verify it before programming:

```sh
./flasher.sh flash /dev/cu.usbserial-110 /path/to/firmware.bin \
  --sha256 YOUR_SUPPLIER_64_CHARACTER_SHA256
```

See [installation and recovery](docs/deployment/installation.md) for the full
procedure and [M147 hardware notes](docs/operations/m147.md) for DIP routing.

## Scope and validation

| Item | Status |
|---|---|
| Physical hardware | One M5Stack M147 / CI1302, CH340 1A86:7523 |
| Reviewed Mac | Apple Silicon, macOS 27.0.1 |
| Native engine | citool-cli 1.2.2 Universal, also contains Intel code |
| Successful programming | 2026-10-07; 1,638,005-byte FW_V2 image; CRC passed; 115.94 seconds |
| Rates used | Handshake 115200, agent 460800, firmware 230400 |
| Recognition/host integration | Separate physical test; not established by flash success |
| Intel Macs / other CI1302 boards | Not physically validated by this repository |
| CI1303 / CI1306 | Upstream advertises support; deliberately rejected by this helper |
| Other USB adapters / operating systems | Outside this helper's validated scope |

This is a terminal tool, with no GUI or HTTP server. It programs the CI1302,
not the ESP32 controller. It cannot convert a wake-word data file, an ESP-SR
model, an OTA package, or `user_code.bin` into a complete programming image.
Keep the original complete vendor firmware before replacing a module's image.

The [hardware validation record](docs/operations/validation.md) distinguishes the
physical flash from this wrapper's automated tests. Upstream binaries include
vendor bootloader/update-agent code; see [third-party notices](THIRD_PARTY_NOTICES.md).

## Development

```sh
make check
```

Tests use temporary mock executables; they do not reset or flash hardware.
GitHub Actions runs these checks on macOS. See [development notes](docs/development/testing.md)
and the [architecture diagrams](docs/architecture/system-overview.md).

Author: **Emmanuel COLUSSI**. The helper and original documentation are licensed
under [MIT](LICENSE). All credit for the native programming engine goes to its
upstream maintainers. This project is independent of M5Stack and ChipIntelli.
