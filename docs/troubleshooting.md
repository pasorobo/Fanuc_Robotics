# Troubleshooting

This page collects problems observed during M0-M3 execution and their fixes. New entries should follow the same `Symptom / Cause / Fix / Reference` template.

## Build and dependency

### `vcs: command not found`

**Symptom:** `./scripts/import_dependencies.sh` aborts with `vcs is not installed`.

**Cause:** `python3-vcstool` not installed on the host. Some CI/build environments lack it by default.

**Fix:** With sudo, `sudo apt install -y python3-vcstool`. Without sudo, `python3 -m pip install --user vcstool` then ensure `${HOME}/.local/bin` is on `PATH`.

**Reference:** Documented in `third_party.humble.repos` setup notes and Task 0 of the M0/M1 plan (commit 9c6bf7f added the fallback).

### `git lfs: command not found` during dependency import

**Symptom:** `import_dependencies.sh` fails on `git -C src/fanuc_description lfs install --local`.

**Cause:** `git-lfs` not installed. FANUC mesh files are LFS-stored.

**Fix:** Install `git-lfs` via apt. The import script tolerates the missing tool by skipping the LFS pull when `git lfs version` fails (commit 5f9ad26). Meshes can be fetched manually later if visualization needs them.

### `rosdep` cannot resolve `ament_python`

**Symptom:** `rosdep install ...` fails with "Cannot locate rosdep definition for [ament_python]".

**Cause:** Humble's `rosdep` distro index does not include the `ament_python` buildtool key. The package is provided by the ROS 2 install itself.

**Fix:** Add `--skip-keys ament_python` to the `rosdep install` invocation. Documented in M2 plan Task 0.

## Launch and runtime

### MoveIt complains "Semantic description is not specified"

**Symptom:** `move_group` warns about semantic description; planning fails.

**Cause:** SRDF cannot be loaded. Most often the robot name in the URDF does not match the SRDF root robot name.

**Fix:** Ensure the cell xacro's `<robot name="...">` matches the FANUC SRDF expected name. Commit 6180cfe aligned the cell robot name with `fanuc_moveit_config`'s SRDF.

### Mock gripper self-collision blocks planning

**Symptom:** Plans to plausible poses fail with collision errors involving gripper internal links.

**Cause:** Gripper geometry overlapping the robot wrist or itself.

**Fix:** Separate gripper collision geometry from visual geometry; tighten boxes so adjacent links do not overlap. Commit bb90a39 split gripper collision shapes from visual ones.

### `/apply_planning_scene` returns failure

**Symptom:** `crx10ial_gripper` service responds with success=false; runtime scene not updated.

**Cause:** Race during service call: the future's `add_done_callback` resolves before the threaded executor sees the response, so the response is empty.

**Fix:** Use a wait pattern that does not depend on `add_done_callback` racing the executor. Commit 4197c66 stabilized the apply_planning_scene call by waiting on the future via `Event` only after the call completed.

### MTC plans pass but trajectory ends past the object

**Symptom:** MTC `Task::plan()` returns SUCCESS, but the resulting end pose is 5-10 cm beyond the object.

**Cause:** "Move to grasp pose" stage targeted the object center directly. The subsequent `MoveRelative` approach added another approach distance, overshooting.

**Fix:** Target a pre-grasp pose in the MoveTo stage (`pregrasp_pose = grasp_pose - approach_direction * approach_distance`). The Cartesian approach then ends at the grasp pose. Commit a32a3ef applied this and other MTC structure adjustments in M3.

### Runtime collision when moving to grasp pose

**Symptom:** During mock execution, `MoveGroupInterface::move()` to the grasp pose fails with `INVALID_GOAL_STATE` even though the MTC plan succeeded.

**Cause:** MTC has its own `ModifyPlanningScene allow collision` stage that allows the gripper to overlap the object during planning. The runtime planning scene has no such allowance, so the same goal pose is rejected.

**Fix:** In mock execution, attach the object before moving to the grasp pose. The fake gripper's attach removes the world `work_object` and re-anchors it as an attached collision on `grasp_link`, so the goal becomes valid. Order: pregrasp -> close -> attach -> move-to-grasp -> retreat. Commit 631bf07 implements this for execute_mock; the source-contract pytest enforces the order statically.

### `slider_gui_node` warnings on headless launch

**Symptom:** Headless launch logs Qt or X11 errors from `slider_gui_node`.

**Cause:** The slider helper requires a display and is started by both the upstream FANUC mock and this project's mock launch.

**Fix:** Acceptable. The smoke checks grep for `Traceback|Exception|ModuleNotFoundError|PackageNotFoundError`, which excludes Qt/X11 connection messages. If needed, suppress slider's start in custom launches.

## MTC and planning

### Negative pick/place planning is "too" successful

**Symptom:** A negative test case meant to fail at the place stage still finds a plan.

**Cause:** The "unreachable" pose is actually within reach.

**Fix:** Use a target with X-coordinate well beyond the robot's 1.249 m reach (the project uses x=2.0 m). The planner reliably reports `GOAL_STATE_INVALID` at "move to place pose". The negative smoke deliberately does not pin a specific failing-stage name; non-empty diagnostics is the assertion.

### Planning succeeds but trajectory has zero points

**Symptom:** `Task::plan()` returns SUCCESS but `solutions().empty()`.

**Cause:** Edge case in MTC; sometimes a non-failure error code does not imply a usable trajectory.

**Fix:** Always check `task.solutions().empty()` in addition to the error code. The project's `plan_fixed_pick_place` does this.

## Reading commit history for fixes

The fastest way to find a fix for an unfamiliar symptom is to grep the project's commit messages:

```bash
git log --oneline | grep -iE 'fix|stabilize|align'
```

M0-M3 fix commits are short and scoped to one concern. Their commit messages describe the symptom and the fix in one line.
