# CRX-10iA/L Gripper Frames

## Frame Tree

The mock gripper uses this fixed frame tree:

```text
world
└── base_link ... flange ... end_effector
    └── tool_link
        ├── gripper_palm
        ├── left_finger
        ├── right_finger
        └── grasp_link
```

## Axis Convention

`grasp_link` is the frame used by task logic and fake attach/detach.

- `+X`: tool approach direction from wrist toward the object.
- `+Y`: parallel-jaw opening direction.
- `+Z`: right-handed upward direction from the gripper palm.

For a pre-grasp pose, move along `-X` from `grasp_link`. For approach, move along `+X` into the grasp. For retreat after grasp, move along `-X` unless the task explicitly requests another retreat vector.

## Planning Scene Ownership

`crx10ial_bringup.mock_scene` publishes static world objects:

- `work_table`
- `work_object`
- `camera_stand`

`crx10ial_gripper.fake_gripper` owns attached-object transitions:

- `AttachObject("work_object")` removes `work_object` from the world and attaches it to `grasp_link`.
- `DetachObject()` removes the attached object from `grasp_link` and restores it to the world at the configured mock object pose.

Physical gripper IO and vendor-specific payload behavior are outside M2. The fake backend exposes the same service surface for later hardware-specific nodes.
