#!/usr/bin/env bash
# Author: Emmanuel COLUSSI
# Validate the release before extracting or executing third-party files.
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$PROJECT_ROOT/scripts/common.sh"
require_macos

if [[ -f "$TOOL" ]]; then
    require_tool
    "$TOOL" --version
    exit 0
fi

mkdir -p "$PROJECT_ROOT/.tools/citool-cli"
staging="$(mktemp -d "$PROJECT_ROOT/.tools/citool-cli/.install.XXXXXX")"
# The trap only removes the temporary directory created by this invocation.
trap 'rm -rf "$staging"' EXIT

printf 'Downloading citool-cli %s for macOS...\n' "$TOOL_VERSION"
curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.2 \
    --connect-timeout 20 --max-time 180 \
    "$TOOL_URL" --output "$staging/archive.tar.gz"
verify_sha256 "$staging/archive.tar.gz" "$ARCHIVE_SHA256"

members="$(tar -tzf "$staging/archive.tar.gz")"
while IFS= read -r member; do
    case "$member" in
        citool-cli/|citool-cli/citool-cli|citool-cli/LICENSE|citool-cli/README.md) ;;
        *) fail "Unexpected archive member: $member" ;;
    esac
done <<< "$members"
tar -xzf "$staging/archive.tar.gz" -C "$staging" \
    citool-cli/citool-cli citool-cli/LICENSE citool-cli/README.md
verify_sha256 "$staging/citool-cli/citool-cli" "$EXECUTABLE_SHA256"
[[ -f "$staging/citool-cli/LICENSE" && -f "$staging/citool-cli/README.md" ]] \
    || fail "The release license or README is missing"
chmod 755 "$staging/citool-cli/citool-cli"
[[ ! -e "$TOOL_DIRECTORY" ]] || fail "Installation directory already exists; inspect it before retrying"
mv "$staging/citool-cli" "$TOOL_DIRECTORY"
require_tool
"$TOOL" --version
printf 'Installed verified release under .tools/citool-cli/%s\n' "$TOOL_VERSION"
