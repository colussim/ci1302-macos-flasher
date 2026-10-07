# System overview

The user supplies a complete vendor CI1302 image and explicitly selects a
supported module's USB serial port. A local Bash wrapper validates its pinned
native engine and inputs, then delegates inspection or programming. The native
engine owns MaskROM, RAM-agent, erase/programming, CRC verification, and reset.
Heavy voice recognition, image generation, and host application behavior are
outside this tool.

There is no daemon, UI server, API service, database, or cloud account. The only
network operation is an explicit HTTPS installation from the pinned public
GitHub release. Local cache is untracked; firmware is supplied separately.

See the [context](context-diagram.md), [containers](container-diagram.md),
[components](component-diagram.md), [deployment](deployment-diagram.md), and
[data flow](data-flow-diagram.md) diagrams, and the
[native-engine decision](../decisions/ADR-0001-native-engine.md).

Security boundaries are the user-supplied file, the third-party download, local
execution, and the physical USB device. Digest pins restrict the executable;
native inspection restricts image format/chip/CRC; optional supplier SHA-256
checks the chosen image; port/VID/PID checks restrict the tested CH340 route.
These checks do not audit third-party source or authenticate firmware's supplier
unless a trusted external digest is provided.
