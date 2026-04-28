# YAML Schemas

The project uses YAML for two configurations today. This page documents both. Schemas are descriptive, not enforced by a JSON-Schema validator; the consuming code (Python or C++) raises when expectations are violated.

## `mock_scene` (in code, not user-facing YAML)

Static workcell collision objects published by `crx10ial_bringup/mock_scene.py`. Defined as a Python tuple `SCENE_BOXES`, not as user YAML. Documented here for reference because changing it requires changing the cell xacro to match.

```python
SCENE_BOXES = (
    BoxSpec("work_table",   (1.00, 0.70, 0.04), (0.75,  0.00, 0.70)),
    BoxSpec("work_object",  (0.08, 0.08, 0.05), (0.55,  0.00, 0.745)),
    BoxSpec("camera_stand", (0.05, 0.05, 0.70), (0.35, -0.55, 0.35)),
)
```

Fields:

- `object_id` - identifier published as `CollisionObject.id`.
- `dimensions` - `(x, y, z)` size of the box in metres.
- `xyz` - `(x, y, z)` centre position in `world`.

The publisher uses TRANSIENT_LOCAL durability so `move_group`'s planning-scene monitor picks up the latest state on subscribe.

## `crx10ial_tasks/config/fixed_pick_place.yaml`

Drives the M3 fixed pick/place task. Single ROS parameter file under the node namespace `fixed_pick_place`.

```yaml
fixed_pick_place:
  ros__parameters:
    arm_group_name: manipulator        # MoveIt planning group
    eef_name: tool_link                # MoveIt end-effector identifier
    hand_frame: grasp_link             # Frame at which objects attach
    world_frame: world

    object.id: work_object             # Attached object id
    object.frame_id: world             # Pose frame for object
    object.dimensions: [0.08, 0.08, 0.05]
    object.pose.xyz: [0.55, 0.0, 0.745]
    object.pose.rpy: [0.0, 0.0, 0.0]

    grasp.frame_id: grasp_link
    grasp.pose.xyz: [0.0, 0.0, 0.0]    # Offset from object frame to grasp pose
    grasp.pose.rpy: [0.0, 0.0, 0.0]
    grasp.approach.direction: [1.0, 0.0, 0.0]   # Unit vector in hand_frame
    grasp.approach.min: 0.05                    # Metres
    grasp.approach.max: 0.10
    grasp.retreat.direction: [-1.0, 0.0, 0.0]
    grasp.retreat.min: 0.05
    grasp.retreat.max: 0.10

    place.frame_id: world
    place.pose.xyz: [0.55, 0.20, 0.745]
    place.pose.rpy: [0.0, 0.0, 0.0]

    failure.place.pose.xyz: [2.00, 0.00, 0.745] # For negative_plan run mode
    failure.place.pose.rpy: [0.0, 0.0, 0.0]

    gripper.open_width_m: 0.08
    gripper.close_width_m: 0.02
    gripper.close_force_n: 30.0

    planning.max_solutions: 1
    planning.timeout_sec: 10.0
    execution.enabled: false           # Reserved for future modes
```

Validation rules implemented in `crx10ial_tasks/src/fixed_pick_place_config.cpp`:

- All `*.xyz` and `*.rpy` arrays must have length 3.
- `grasp.approach.min` must be > 0 and <= `grasp.approach.max`. Same for retreat.
- `gripper.open_width_m`, `gripper.close_width_m`, `gripper.close_force_n` must be > 0.
- `planning.max_solutions` must be > 0 and is cast to `size_t`.
- `planning.timeout_sec` must be > 0.

Notes on conventions:

- `grasp.approach.direction` is expressed in `hand_frame` (`grasp_link`). The default `[1, 0, 0]` matches the `+X approach` convention from [frames.md](frames.md).
- `grasp.pose.xyz: [0, 0, 0]` means the grasp pose equals the object pose. The MTC stage moves first to a *pre-grasp* pose computed as `grasp_world_pose - approach.max * approach.direction`.
- `failure.place.pose.xyz: [2.0, ...]` is intentionally outside the robot's reach (1.249 m). It produces deterministic IK failure for the `negative_plan` run mode.

## Future YAMLs (not yet implemented)

- `crx10ial_vision_bridge/config/vision_jobs.yaml` - declared in the design (section 9). Maps each vision job to trigger DO, busy/complete DI, result register, found-pose register, frames. Will be added in M5.
- `crx10ial_bringup/config/safety.yaml` - workspace limits and reduced-speed thresholds for `crx10ial_safety` (M7 prep).
