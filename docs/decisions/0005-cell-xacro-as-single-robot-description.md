# 5. Cell xacro as Single robot_description Source

## Status

Accepted (2026-04-27)

## Context

In M0/M1 the mock launch used `IncludeLaunchDescription(fanuc_mock_control.launch.py)` and let the FANUC mock launch expand its own URDF. MoveIt was given a separate `robot_description` derived from the FANUC `crx10ia_l.urdf.xacro`. There were effectively two URDFs: one for ros2_control (FANUC's view), one for MoveIt (FANUC's same xacro, separately expanded).

In M2 the workcell description grew. The cell xacro started including the FANUC ros2_control macro (`crx_mock_ros2_control_macro.xacro`) so that planning, controllers, and visualization shared a single URDF. With this change, including the upstream FANUC mock launch as-is would expand the FANUC URDF a second time, producing inconsistent state.

Three paths were considered:

- Keep `IncludeLaunchDescription(fanuc_mock_control.launch.py)` and override its `robot_description` parameter from outside.
- Stop including the FANUC mock launch and start the same controllers and nodes directly from the project launch.
- Continue with two URDFs and accept the duplication.

## Decision

Make the **cell xacro the single source of truth** for `robot_description`. The project's mock launch:

- Expands the cell xacro once.
- Feeds the expanded URDF to `controller_manager` (ros2_control), `robot_state_publisher`, and the MoveIt configuration via `MoveItConfigsBuilder.robot_description(file_path=cell_xacro_path, ...)`.
- Starts the FANUC controllers (`joint_state_broadcaster`, `joint_trajectory_controller`, `fanuc_gpio_controller`, `fanuc_force_sensor_broadcaster`, `force_torque_sensor_broadcaster`) directly via 5 spawner `ExecuteProcess` actions, mirroring the upstream FANUC mock launch.
- Starts `slider_gui_node` for parity with the upstream helper.

The launch file documents this choice with an inline comment near `control_node`.

## Consequences

Positive:

- One URDF: changes to the cell (frames, gripper, collision) propagate to MoveIt and ros2_control consistently.
- Project-defined frames (`tool_link`, `grasp_link`, gripper geometry) are visible to MoveIt for planning.
- The mock launch is self-contained; no upstream launch is included, so behaviour is reproducible without reading FANUC's launch file.

Negative:

- The project must track the FANUC controller list and timeouts. If FANUC adds or renames a controller in `fanuc_mock_control.launch.py`, the project's mock launch needs an explicit edit to follow.
- Future controllers introduced for hardware (M7) need similar mirroring rather than launch inclusion.

Mitigations:

- The project's launch file is short and easy to read. Diff it against `fanuc_mock_control.launch.py` periodically when bumping the FANUC lock pin.
- Keep an explicit comment block in `mock.launch.py` linking to this ADR so the rationale is local to the code.

## Related decisions

- [0003](0003-fake-gripper-as-runtime-scene-owner.md) - C1 contract. Also depends on a single planning scene source.
