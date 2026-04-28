# 3. fake_gripper as Runtime Scene Owner (C1 Contract)

## Status

Accepted (2026-04-28)

## Context

In MoveIt 2, attached collision objects are usually written to the runtime planning scene by whichever component grabs an object: a MoveIt Task Constructor stage, a MoveGroupInterface client, or a custom node. The standard MTC pick/place tutorial uses MTC's `ModifyPlanningScene::attachObject()` and `Task::execute()` to drive both planning and runtime scene transitions.

This project has a different runtime story:

- The gripper has multiple future backends: a fake one for mock and Gazebo work, a controller-side iRVision-aware backend for ROBOGUIDE (M6), and a physical gripper backend (M7).
- Each backend updates the same runtime planning scene from a different physical pathway (Python service for fake, FANUC I/O for real).
- The planning task should not change shape when the underlying backend changes.

If MTC owns runtime attach/detach via `Task::execute()`, every backend swap requires changes to MTC stages and to the executor configuration. If MTC and the gripper service both write to `/apply_planning_scene`, ordering issues and double attachments are possible.

![C1 contract diagram](../diagrams/c1_contract.svg)

## Decision

Make `crx10ial_gripper` the sole writer to the runtime planning scene for attached collision objects.

Concretely:

- MTC stages may use `ModifyPlanningScene::attachObject()` and `detachObject()` only to update MTC's internal stage scene during planning.
- The project never calls `moveit::task_constructor::Task::execute()`. A pytest source-contract test in `crx10ial_tasks/test/test_task_source_contract.py` greps for `.execute(` and `execute_task_solution` in task and node sources and fails on either match.
- Mock execution drives motion through `MoveGroupInterface` and triggers attach/detach via the `crx10ial_gripper` services. The gripper service is the only ROS client of `/apply_planning_scene` for attach/detach diffs.
- A runtime check (`/get_planning_scene` after attach) asserts exactly one attached `work_object` and zero world `work_object` duplicates. This is part of the M3 execute_mock smoke.

## Consequences

Positive:

- Planning logic in `crx10ial_tasks` is independent of backend. Switching from fake to real iRVision-driven gripper does not change MTC stages.
- One named place to debug runtime scene corruption: any duplicate or missing attached object is by definition a `crx10ial_gripper` issue.
- Static enforcement (source-contract test) catches accidental violations during code review or auto-generated changes.

Negative:

- Mock execution must reorder operations relative to the textbook MTC flow. Specifically: pregrasp -> close -> attach -> move-to-grasp, instead of pregrasp -> move-to-grasp -> close -> attach. Without the reorder, the runtime scene still has the world `work_object` when the arm tries to reach the grasp pose, and goal collision rejects the plan.
- New contributors are unfamiliar with this convention because it differs from the MoveIt MTC tutorial. Mitigated by this ADR plus the documentation in `docs/architecture.md`.

## Enforcement

- `crx10ial_tasks/test/test_task_source_contract.py` greps for forbidden symbols and required structural patterns (pregrasp stage, attach-before-grasp ordering).
- M3 execute_mock smoke calls `/get_planning_scene` after attach and after detach; the C++ helper `verify_single_runtime_attachment` enforces the single-attached invariant.
- An external pytest, `check_single_attached_object.py`, verifies post-run state (`attached=0`, `world=1`).
