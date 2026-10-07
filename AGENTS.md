# Repository instructions

This is a Bash/macOS command-line helper, not a firmware SDK or server. Preserve
compatibility with macOS Bash 3.2. Keep source comments, names, and diagnostic
messages in English, and include `Author: Emmanuel COLUSSI` headers in new
source files. The user-facing French README is an intentional translation.

Read README.md, scripts/common.sh, and the architecture/deployment guides before
changing behavior. Keep changes focused. Always synchronize CLI documentation,
tests, pinned tool metadata, and validation claims with code.

Run `make check` for changes. Real native install/list/inspect checks are safe
offline/read-only integration operations. Never run probe/flash against physical
hardware without explicit user authorization. CI must never open serial devices.

Do not commit firmware images, downloaded vendor executables, SDKs, private logs,
device inventories, credentials, or private filesystem paths. Retain upstream
attribution and license files in the downloaded cache. Do not claim source
auditing when the upstream engine's source was unavailable for review.

Keep HTTPS-only downloads, both pinned digests, CI1302 image validation, exact
CH340 USB identity checks, manual reset, bounded connection waits, and explicit
port/image selection. Do not add automatic flashing, retries, bypass switches,
or automatic port selection. Physical flash success does not prove wake-word
recognition or host-controller integration.
