# Services and Launches

Reference catalog of every project-defined service and launch file. For schemas of YAML configuration files, see `docs/yaml_schemas.md`.

## Services

All project services live in `crx10ial_interfaces/srv/`.

### `CommandGripper` (`crx10ial_gripper/command`)

Commands the fake gripper.

Constants in `Request`:

- `OPEN = 1` - command opens the gripper.
- `CLOSE = 2` - command closes the gripper.
- `VACUUM_ON = 3` - sets the fake vacuum state to enabled.
- `VACUUM_OFF = 4` - clears the fake vacuum state.

Request fields:

- `uint8 command` - one of the constants above.
- `float64 width_m` - target jaw width in metres (0.0 to 0.12).
- `float64 force_n` - target force in newtons (>= 0.0).

Response fields:

- `bool success`, `string message`.
- `uint8 state` - state machine value (`IDLE=0, OPEN=1, CLOSED=2, HOLDING=3`).
- `float64 width_m`, `float64 force_n`.
- `string attached_object_id` - empty unless an object is attached.
- `bool vacuum_enabled`.

### `AttachObject` (`crx10ial_gripper/attach_object`)

Attaches a known world collision object to `grasp_link`.

Request: `string object_id` (must be a known mock object; `work_object` is the default).

Response: `bool success`, `string message`, `string attached_object_id`.

The implementation removes the object from the world and adds it as an attached collision via `/apply_planning_scene`.

### `DetachObject` (`crx10ial_gripper/detach_object`)

Detaches the currently attached object and restores it as a world collision at its configured pose.

Request: empty.

Response: `bool success`, `string message`, `string detached_object_id`.

### `GetGripperState` (`crx10ial_gripper/get_state`)

Reads the current fake gripper state.

Request: empty.

Response: `uint8 state`, `float64 width_m`, `float64 force_n`, `string attached_object_id`, `bool vacuum_enabled`.

## Launches

All launches live under `src/<package>/launch/`.

### `crx10ial_cell_description/view_cell.launch.py`

Visualizes the workcell in RViz with `joint_state_publisher_gui`. Useful for inspecting frame placement and collision geometry without running MoveIt or controllers.

Arguments:

- `launch_rviz` (`true`/`false`, default `true`).

### `crx10ial_bringup/mock.launch.py`

Brings up the full mock workcell: FANUC mock control, MoveIt 2, RViz (optional), the static planning-scene publisher, and the fake gripper.

Arguments:

- `robot_model` (default `crx10ia_l`).
- `robot_ip` (default `1.1.1.1`; unused in mock).
- `launch_rviz` (`true`/`false`, default `true`).
- `publish_scene` (`true`/`false`, default `true`).
- `launch_gripper` (`true`/`false`, default `true`).
- `ros2_control_config` (default: FANUC's `ros2_controllers.yaml`).
- `gpio_configuration` (default: FANUC's `example_gpio_config.yaml`).

Notable nodes started:

- `controller_manager` (`ros2_control_node`).
- `robot_state_publisher`.
- 5 controller spawners: `joint_state_broadcaster`, `joint_trajectory_controller`, `fanuc_gpio_controller`, `fanuc_force_sensor_broadcaster`, `force_torque_sensor_broadcaster`.
- `move_group`.
- `rviz2` (conditional).
- `mock_scene_publisher` (conditional).
- `fake_gripper` (conditional).
- `slider_gui_node` (FANUC upstream helper).

### `crx10ial_tasks/fixed_pick_place.launch.py`

Starts the M3 fixed pick/place node alongside the mock cell. Use after `mock.launch.py` is up.

Arguments:

- `robot_model` (default `crx10ia_l`).
- `run_mode` - one of `plan`, `negative_plan`, `execute_mock` (default `plan`).
- `config_file` - YAML path; defaults to the installed `fixed_pick_place.yaml`.

Behaviours:

- `plan` - builds the MTC task and calls `Task::plan(max_solutions)`. Logs diagnostics and exits.
- `negative_plan` - same, but uses the failure place pose. Expects diagnostics.
- `execute_mock` - plans, then orchestrates motion through `MoveGroupInterface` and the fake gripper. Asserts a single attached object via `/get_planning_scene` after attach.

The launch always injects the MoveIt configuration (`robot_description`, `robot_description_semantic`, kinematics, joint limits, planning pipelines) so the node can build the MTC task without the move_group monitor topics.

## Common topics and services touched at runtime

These are not project-owned but are consumed by project code in mock mode.

- `/joint_states` - joint state publisher feeds MoveIt and `tf`.
- `/tf`, `/tf_static` - frame transforms.
- `/collision_object` - latched topic published by `mock_scene_publisher`.
- `/apply_planning_scene` - service exposed by `move_group`; called by `fake_gripper`.
- `/get_planning_scene` - service exposed by `move_group`; called by execute_mock and the M3 duplicate-attach check.
- `/plan_kinematic_path` - MoveIt motion-planning service.
- `/execute_trajectory` - MoveIt trajectory execution action.
