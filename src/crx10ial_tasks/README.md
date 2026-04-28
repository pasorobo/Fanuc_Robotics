# crx10ial_tasks

Task-level planning package for the CRX-10iA/L workcell.

## M3 Fixed Pick-and-Place

M3 uses MoveIt Task Constructor for fixed-pose pick/place planning on Ubuntu 22.04 / ROS 2 Humble.

Runtime scene ownership follows the M2 gripper contract:

- MTC attach/detach stages are used only for internal planning-scene propagation.
- `moveit::task_constructor::Task::execute()` is not used in M3.
- Runtime attach/detach is performed through `/crx10ial_gripper/attach_object` and `/crx10ial_gripper/detach_object`.

Record the installed MTC binaries with:

```bash
apt list --installed 2>/dev/null | grep 'ros-humble-moveit-task-constructor'
```
