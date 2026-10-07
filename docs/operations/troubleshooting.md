# Troubleshooting

| Symptom | Check / next action |
|---|---|
| Tool missing | Run `./flasher.sh install`; only install the pinned public release |
| Tool/archive SHA-256 mismatch | Stop; inspect the download/cache and compare the upstream release metadata. Do not bypass the check |
| No CH340 port | Use the module's own USB socket and a data cable; compare before/after `list` |
| Wrong VID/PID or USB CDC port rejected | Select the actual module; VID 1A86/PID 7522 and other adapters are outside this helper's tested scope |
| Permission denied opening port | Check macOS/device access permissions and any application sandbox; close serial monitors. Do not broadly change `/dev` permissions |
| Waiting for MaskROM | Press the module's Debug Rst while the command is waiting; it times out after 60 seconds |
| Probe succeeds but final reset acknowledgement times out | The observed probe did this without writing Flash. Reset/power-cycle, then use a new manual reset for the next command |
| Firmware inspection / CRC fails | Use the complete compatible CI1302 FW_V2 image, not an ASR resource, `.bin.ota`, or `user_code.bin` |
| Programming or verification fails | Keep the log, check power/cable and module identity, and probe again before a recovery flash |
| Wake phrase does not trigger after CRC success | Reset/power-cycle; verify firmware configuration, pronunciation, supply, UART routing, and host wake ID separately |

Do not open both aliases of a CH340 adapter concurrently. If reconnecting changes
the port name, rerun `list` and start a new command with the actual port. The
wrapper does not choose a replacement port automatically.

The physical test used 460800 agent/230400 firmware baud. Higher rates are not
exposed by this wrapper. A timeout is not proof that increasing baud will help.
The native tool remains a separate third-party executable; this repository
does not claim every adapter, Mac release, or CI1302 board has been tested.

There is no daemon, monitoring endpoint, or automatic retry. Progress and error
output go to the terminal; capture a log with `pipefail` as documented in the
[installation guide](../deployment/installation.md). Do not publish private
firmware exports, credentials, full USB inventories, or private host paths in
issue reports. Include tool version, adapter VID/PID, module model, the failing
stage, and a sanitized error excerpt instead.
