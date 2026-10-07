# Development and testing

Run `make check` with Python 3 available. Bash syntax is checked and unittest
exercises argument parsing, checksum enforcement, rejection of empty/OTA/wrong
chip images, native CRC failure propagation, exact CH340 identity matching,
USB CDC rejection, path quoting, and native exit-status preservation.

Temporary fixtures replace the pinned executable digest with the fixture's
digest **only in a temporary copied script**, and simulate macOS `uname` output.
Production digest constants are never modified by the tests. No fixture opens
a serial port. A successful mock inspection is a command-delegation test, not
a real firmware-format test; perform native offline `inspect` separately on a
private complete image.

Check scripts on the macOS bundled Bash 3.2 as well as newer Bash when changing
syntax. Keep source comments/logs in English and maintain the user-facing French
README consistently with the English CLI and hardware limitations. New source
files require the Emmanuel COLUSSI author header.

For a native integration check, run the real pinned installer, then `list` and
`inspect` on a trusted private image. These do not write Flash. Probe/flash are
intentional physical operations requiring a verified module and manual reset;
they must never be added to CI or run automatically by the installer.

No dependencies need to be built. The upstream engine is a pinned executable
download, so `bash -n`, mocked unit checks, real version/inspection, and a
recorded hardware test are the applicable checks. There is no application
firmware build or server compilation step in this repository.
