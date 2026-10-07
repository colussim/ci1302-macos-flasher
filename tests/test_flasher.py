# Author: Emmanuel COLUSSI
"""Exercise guards and native-command delegation without touching USB devices."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL_HASH = "f9f07bc1cfaab4875470dfdd1890977bef3be860bb8c5fb73e447fb51febb331"
MOCK_TOOL = '''#!/usr/bin/env python3
# Author: Emmanuel COLUSSI
import json
import os
from pathlib import Path
import sys
args = sys.argv[1:]
with open(os.environ["MOCK_TRACE"], "a") as trace:
    trace.write(json.dumps(args) + "\\n")
if args[0] == "--version":
    print("citool-cli 1.2.2")
elif args[0] == "inspect":
    if os.environ.get("MOCK_MODE") == "bad-crc":
        print("CRC mismatch", file=sys.stderr)
        sys.exit(7)
    chip = "CI1303" if os.environ.get("MOCK_MODE") == "wrong-chip" else "CI1302"
    print(f"V2 partition table: chip {chip}, firmware version 2.0.0")
elif args[0] == "list":
    print("/dev/cu.usbserial-test USB Serial [VID:1A86 PID:7523]")
    sys.exit(int(os.environ.get("MOCK_EXIT", "0")))
else:
    print("Unexpected serial operation", file=sys.stderr)
    sys.exit(90)
'''


class FlasherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ci1302 test ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copyfile(ROOT / "flasher.sh", self.root / "flasher.sh")
        (self.root / "scripts").mkdir()
        shutil.copyfile(ROOT / "scripts/install-citool.sh", self.root / "scripts/install-citool.sh")
        self.tool = self.root / ".tools/citool-cli/1.2.2/citool-cli"
        self.tool.parent.mkdir(parents=True)
        self.tool.write_text(MOCK_TOOL)
        self.tool.chmod(0o755)
        mock_hash = hashlib.sha256(self.tool.read_bytes()).hexdigest()
        common = (ROOT / "scripts/common.sh").read_text().replace(TOOL_HASH, mock_hash)
        (self.root / "scripts/common.sh").write_text(common)
        self.image = self.root / "firmware with spaces.bin"
        self.image.write_bytes(b"test firmware")
        self.trace = self.root / "trace.jsonl"
        mock_bin = self.root / "mock-bin"
        mock_bin.mkdir()
        uname = mock_bin / "uname"
        uname.write_text("#!/bin/sh\n# Author: Emmanuel COLUSSI\nprintf 'Darwin\\n'\n")
        uname.chmod(0o755)
        self.env = dict(os.environ, MOCK_TRACE=str(self.trace))
        self.env["PATH"] = str(mock_bin) + os.pathsep + self.env["PATH"]
        self.mock_bin = mock_bin

    def invoke(self, *args):
        return subprocess.run(
            ["bash", str(self.root / "flasher.sh"), *map(str, args)],
            env=self.env, capture_output=True, text=True, check=False, timeout=10,
        )

    def calls(self):
        return [json.loads(line) for line in self.trace.read_text().splitlines()] if self.trace.exists() else []

    def test_help_needs_no_tool_or_hardware(self):
        self.tool.unlink()
        self.assertEqual(self.invoke("--help").returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_unknown_command_and_unexpected_arguments(self):
        for args in [("erase",), ("list", "extra"), ("flash",), ("probe",)]:
            with self.subTest(args=args):
                self.assertNotEqual(self.invoke(*args).returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_tampered_tool_is_never_executed(self):
        self.tool.write_text(MOCK_TOOL + "# modified\n")
        result = self.invoke("list")
        self.assertIn("SHA-256 mismatch", result.stderr)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_space_containing_image_and_uppercase_digest(self):
        digest = hashlib.sha256(self.image.read_bytes()).hexdigest().upper()
        result = self.invoke("inspect", self.image, "--sha256", digest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls(), [["inspect", "--", str(self.image)]])

    def test_wrong_digest_blocks_flash_before_native_execution(self):
        result = self.invoke("flash", "/dev/cu.usbserial-test", self.image, "--sha256", "0" * 64)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SHA-256 mismatch", result.stderr)
        self.assertEqual(self.calls(), [])

    def test_invalid_digest_and_options_are_rejected(self):
        for args in [("--sha256", "bad"), ("--sha256", ""), ("--force", "yes")]:
            with self.subTest(args=args):
                self.assertNotEqual(self.invoke("inspect", self.image, *args).returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_missing_empty_and_ota_images_are_rejected(self):
        for name, data in [("missing.bin", None), ("empty.bin", b""), ("image.bin.ota", b"ota")]:
            image = self.root / name
            if data is not None:
                image.write_bytes(data)
            with self.subTest(name=name):
                self.assertNotEqual(self.invoke("inspect", image).returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_crc_failure_stops_before_serial_operations(self):
        self.env["MOCK_MODE"] = "bad-crc"
        result = self.invoke("flash", "/dev/cu.usbserial-test", self.image)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Native firmware inspection failed", result.stderr)
        self.assertEqual([call[0] for call in self.calls()], ["inspect"])

    def test_other_chip_stops_before_serial_operations(self):
        self.env["MOCK_MODE"] = "wrong-chip"
        result = self.invoke("flash", "/dev/cu.usbserial-test", self.image)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only accepts complete CI1302", result.stderr)
        self.assertEqual([call[0] for call in self.calls()], ["inspect"])

    def test_usb_cdc_and_absent_ports_are_rejected(self):
        for port in ["/dev/cu.usbmodemTAB5", "/dev/cu.usbserial-nonexistent-unit-test"]:
            with self.subTest(port=port):
                self.assertNotEqual(self.invoke("probe", port).returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_native_failure_exit_status_is_preserved(self):
        self.env["MOCK_EXIT"] = "12"
        self.assertEqual(self.invoke("list").returncode, 12)

    def mock_download(self, archive):
        curl = self.mock_bin / "curl"
        curl.write_text(
            '#!/usr/bin/env python3\n# Author: Emmanuel COLUSSI\n'
            'import os, shutil, sys\n'
            'destination = sys.argv[sys.argv.index("--output") + 1]\n'
            'shutil.copyfile(os.environ["MOCK_ARCHIVE"], destination)\n'
        )
        curl.chmod(0o755)
        self.env["MOCK_ARCHIVE"] = str(archive)

    def test_installer_reuses_verified_cache(self):
        result = self.invoke("install")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls(), [["--version"]])

    def test_invalid_archive_digest_blocks_extraction_and_execution(self):
        self.tool.unlink()
        archive = self.root / "bad-download.tar.gz"
        archive.write_bytes(b"not a release archive")
        self.mock_download(archive)
        result = self.invoke("install")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SHA-256 mismatch", result.stderr)
        self.assertFalse(self.tool.exists())
        self.assertEqual(self.calls(), [])
        self.assertEqual(list((self.root / ".tools/citool-cli").glob(".install.*")), [])

    def test_unexpected_archive_member_is_rejected_before_extraction(self):
        self.tool.unlink()
        archive = self.root / "unexpected.tar.gz"
        with tarfile.open(archive, "w:gz") as bundle:
            bundle.add(self.image, arcname="../escaped-image.bin")
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        common = self.root / "scripts/common.sh"
        content = common.read_text().replace(
            "44caacf0d4e832ca2edcb047ef2deaaec0393262b63fd233ac65d18d91ab6e50", digest
        )
        common.write_text(content)
        self.mock_download(archive)
        result = self.invoke("install")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unexpected archive member", result.stderr)
        self.assertFalse(self.tool.exists())
        self.assertFalse((self.root / ".tools/citool-cli/escaped-image.bin").exists())
        self.assertEqual(self.calls(), [])

    def test_usb_identity_requires_exact_port_vid_and_pid(self):
        port = "/dev/cu.usbserial-test"
        for line, accepted in [
            (f"{port} USB Serial [VID:1A86 PID:7523]", True),
            (f"{port} USB Serial [VID:303A PID:1001]", False),
            (f"{port} USB Serial [VID:1A86 PID:7522]", False),
            (f"{port}-other USB Serial [VID:1A86 PID:7523]", False),
        ]:
            result = subprocess.run(
                ["bash", "-c", 'PROJECT_ROOT="$1"; source "$1/scripts/common.sh"; validate_usb_identity "$2" "$3"',
                 "usb-test", str(self.root), port, line],
                capture_output=True, text=True, check=False, timeout=10,
            )
            with self.subTest(line=line):
                self.assertEqual(result.returncode == 0, accepted)


if __name__ == "__main__":
    unittest.main()
