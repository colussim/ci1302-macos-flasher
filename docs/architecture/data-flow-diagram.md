# Programming data flow

```mermaid
sequenceDiagram
    actor User
    participant CLI as Bash helper
    participant Engine as Native engine
    participant Module as CI1302
    User->>CLI: flash explicit-port complete-image
    CLI->>CLI: Verify pinned executable and optional image SHA-256
    CLI->>Engine: Inspect full image
    Engine-->>CLI: CI1302 FW_V2 partitions and CRC results
    CLI->>Engine: List ports and validate CH340 identity
    CLI->>Engine: Flash with bounded manual-reset options
    Engine-->>User: Waiting for MaskROM
    User->>Module: Debug Rst
    Engine->>Module: Handshake and RAM update agent
    Engine->>Module: Erase and program full image
    Engine->>Module: CRC verification and reset
    Engine-->>User: Final result and exit status
```

An inspection or identity failure stops before serial programming. Probe uses
the handshake/RAM-agent subset and does not erase/write Flash. Firmware files
and progress logs belong to the user; they are not uploaded by the helper.
