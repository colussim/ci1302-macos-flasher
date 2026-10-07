# Validation record

## Physical native-engine test — 2026-10-07

- Hardware: one M5Stack Module ASR M147 with CI1302 and CH340 VID 1A86/PID 7523.
- Host: Apple Silicon arm64, macOS 27.0.1.
- Engine: the pinned citool-cli 1.2.2 macOS Universal executable.
- Input: a complete SmartPI CI1302 FW_V2 serial-flash image, 1,638,005 bytes.
- Interface: the module's own USB-C, with a manual Debug Rst for each command.
- Rates: 115200 handshake, 460800 agent, 230400 firmware; 8000 ms response timeout.
- Probe: MaskROM and 16,140-byte agent connection passed. Its final reset
  acknowledgement timed out. No Flash erase/write occurred during this probe.
- Flash: a new manual reset established the connection; erase/programming and
  verification reached 100%, final firmware CRC passed, final reset completed,
  exit status zero. Reported elapsed time: **115.94 seconds**.

The private test image and raw logs remain with the original satellite project;
they are not distributed here. This establishes native-engine programming on
one module/Mac combination, not wake-word recognition, host integration, every
firmware configuration, other USB adapters, Intel Macs, or a complete OS matrix.

The standalone wrapper in this repository adds stricter input/USB checks and
user-selected image paths. Its installer and offline inspection are verified
separately; this wrapper has not performed a new physical flash simply to
repeat the successful native-engine test. Automated tests use mocked commands
and never touch hardware.
