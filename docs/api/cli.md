# Command-line interface

No HTTP server, REST endpoint, database, or authentication service is exposed.
The interface is the local Bash executable `flasher.sh`; a network credential
is not needed to download the public pinned release.

| Command | Input | Effects |
|---|---|---|
| `install` | None | HTTPS download, digest checks, installation in `.tools/` |
| `list` | None | USB/serial enumeration; no reset or Flash write |
| `inspect FILE [--sha256 HASH]` | Complete CI1302 FW_V2 `.bin` | Local hash/table/CRC inspection; no device access |
| `probe PORT` | Explicit CH340 port | MaskROM handshake and agent transfer to RAM; no Flash erase/write |
| `flash PORT FILE [--sha256 HASH]` | Explicit port and complete image | Image checks, identity checks, erase/write/CRC/reset |
| `help` / `--help` / `-h` | None | Usage text, no download/device access |

`--sha256` takes exactly 64 hexadecimal characters (either case). A missing,
empty, malformed, or mismatching digest fails before programming. If omitted,
the image's calculated SHA-256 is printed; the native partition/CRC inspection
still runs. CRC verifies format/integrity, not supplier authenticity. Obtain
an expected digest from a trusted supplier when available.

Serial paths must be `/dev/cu.usbserial-*` or `/dev/cu.wchusbserial*`, must exist
as character devices, and must appear in the native tool's list with **VID
1A86 / PID 7523**. No automatic port selection, RTS reset, unbounded connection
wait, `erase` command, or bypass/force option is provided.

Probe/flash use 115200 handshake baud, 460800 update-agent baud, an 8000 ms
response timeout, manual reset, and a 60-second connection timeout. Flash uses
230400 firmware baud. Native command exit status is propagated; wrapper input
or validation errors exit 1. Help exits 0. The helper never treats a probe or
100% programming output as a completed CRC verification.

Relative and absolute file paths are accepted. Quote paths containing spaces.
Names beginning with a dash are passed after `--` to the native tool. Inspection
rejects empty/missing files, OTA suffixes, and non-CI1302/FW_V2 images. The file
must remain unchanged throughout inspection/programming.

Execution requires local serial-device access. A permission error is a host
access problem; it does not establish module failure. Installer filesystem
changes are confined to this checkout's `.tools/` cache.
