# 2. Use FANUC Official ROS 2 Driver

## Status

Accepted (2026-04-27)

## Context

Multiple options exist for ROS-driving a FANUC controller from Linux:

- **FANUC official ROS 2 driver** (`FANUC-CORPORATION/fanuc_driver`). Vendor-maintained. Includes `fanuc_description`, `fanuc_hardware_interface`, `fanuc_moveit_config`, and FANUC-specific controllers. Targets J519 Stream Motion + R912 RMI. Has a `humble` branch.
- **ROS-Industrial Fanuc** (`ros-industrial/fanuc`). Original, ROS 1 era driver. ROS 2 port is partial and community-maintained.
- **Unofficial ROS 2 Fanuc interface** (`paolofrance/ros2_fanuc_interface`). Single-author, smaller scope, no vendor backing.
- Custom driver development.

Scoring criteria the project cares about:

- Long-term support and bug-fix flow.
- Feature coverage: trajectory streaming, I/O, registers, payload, recovery.
- URDF and MoveIt config quality for the CRX series.
- Compatibility with iRVision integration via R[]/PR[].

## Decision

Use the **FANUC official ROS 2 driver** as the primary upstream for description, hardware interface, MoveIt configuration, and message types.

Specifically:

- Pin `fanuc_description` and `fanuc_driver` in `third_party.humble.repos` and `third_party.humble.lock.repos` to specific commits. Reproduce in M0 Task 1.
- Treat `ros-industrial/fanuc` and `paolofrance/ros2_fanuc_interface` as references only. Do not ship code that depends on them.
- Do not write a custom driver in M0-M7.

## Consequences

Positive:

- The robot model (`crx10ia_l`), MoveIt configuration, and SRDF are vendor-quality. The project trusts these, freeing engineering effort for cell, gripper, and task work.
- Future driver updates (new controller versions, fixes) flow from FANUC. The project follows by bumping the lock file.
- iRVision integration paths are aligned with what FANUC officially documents.

Negative:

- The project is dependent on FANUC's release cadence for upstream fixes. Some niche features may lag.
- The driver assumes specific software options (J519, R912). Hosts without those options cannot run the hardware path. M7 explicitly checks the option inventory.

Mitigations:

- Maintain a pinned-commit lock file so accidental upstream regressions are caught at the next intentional bump.
- Document required FANUC controller options in M7 prep and in [../concepts/hardware_overview.md](../concepts/hardware_overview.md).
- Keep the project's gripper, vision, and task layers behind their own interfaces so a future driver change does not cascade through application code.
