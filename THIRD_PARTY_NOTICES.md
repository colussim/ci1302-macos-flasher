# Third-party tools and attribution

## citool-cli 1.2.2

The native programming engine is maintained by **coloz and citool-cli
contributors** and distributed through the
[Arduino CI130X release](https://github.com/coloz/arduino-ci130x/releases/tag/citool-cli-v1.2.2).
Its package includes an MIT license credited to citool-cli contributors (2026).
The release identifies source commit `abdbb89fb0afc7e95c7588e2bc9cddb7ebf5dd70`
in `coloz/citool-cli`; that source repository was not publicly accessible during
this project's review. Do not describe this helper as a source-audited or
independent implementation of the serial programming protocol.

The executable also contains ChipIntelli vendor bootloader/update-agent binaries
under their original terms, as stated in its packaged README. This repository
does not redistribute those binaries or copy vendor source code. Its installer
downloads the original release and retains the original `LICENSE` and `README.md`
in the ignored `.tools/` directory. This repository's MIT license applies to
the authored wrapper, tests, and original documentation, not to all upstream
binary components.

Pinned macOS Universal artifact:

- Archive SHA-256: `44caacf0d4e832ca2edcb047ef2deaaec0393262b63fd233ac65d18d91ab6e50`.
- Executable SHA-256: `f9f07bc1cfaab4875470dfdd1890977bef3be860bb8c5fb73e447fb51febb331`.
- Platform: Intel x86_64 and Apple Silicon arm64 in a Universal Mach-O executable.

Digests were checked against the upstream release metadata and its Arduino
package index. They establish consistency with the pinned release, not an
independent audit or a guarantee about the executable's behavior.

## Hardware and references

- [M5Stack Module ASR M147](https://docs.m5stack.com/en/module/Module_ASR):
  product specifications, USB programming port, and schematic.
- [M5Stack custom firmware guide](https://docs.m5stack.com/en/guide/module_asr/custom_firmware):
  generating a complete CI1302 image through SmartPI.
- [Wireless-Tag WT99C202/C302](https://github.com/wireless-tag-com/WT99C202_C302):
  a research reference for CI1302 updates from an embedded controller. None of
  its code or precompiled libraries is included here.

M5Stack and ChipIntelli names identify the hardware and original tools. This
repository is not an official product or endorsement from either company.
