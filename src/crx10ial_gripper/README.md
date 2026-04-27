# crx10ial_gripper

Gripper control abstraction for the CRX-10iA/L mock workcell.

## Fake backend

The `fake_gripper` executable provides services under its namespace:

- `command`
- `attach_object`
- `detach_object`
- `get_state`

The backend updates MoveIt through `/apply_planning_scene` for attach/detach. Static world collision objects remain owned by `crx10ial_bringup.mock_scene`.
