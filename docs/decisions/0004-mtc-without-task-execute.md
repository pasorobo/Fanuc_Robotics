# 4. MoveIt Task Constructor Without Task::execute()

## Status

Accepted (2026-04-28)

## Context

MoveIt Task Constructor (MTC) is a natural fit for fixed pick-and-place planning: stages compose into a graph, failures localize to the offending stage, and diagnostics are built in. For M3 the project chose MTC for the planning side.

A separate question is whether to call `moveit::task_constructor::Task::execute()` to drive the actual robot motion. `Task::execute()` sends an `ExecuteTaskSolution` action that, in addition to executing the trajectory, applies the same scene diffs MTC used during planning. That side effect collides with the C1 contract from [0003](0003-fake-gripper-as-runtime-scene-owner.md).

Three execution paths were considered:

- **Use `Task::execute()`**. Most concise. Implicitly violates C1.
- **Use `Task::execute()` and rewrite the gripper service to noop on attach/detach**. Possible but inverts ownership. The gripper backend would still need to track state machine transitions for hardware support; the runtime scene write would now live in MTC, breaking the "one place to debug" property.
- **Drive motion separately via `MoveGroupInterface` and call gripper services for attach/detach**. Slightly more code but preserves C1.

## Decision

Use MTC for planning only. Drive runtime motion through `MoveGroupInterface`. Trigger attach/detach through `crx10ial_gripper` services. The project does not call `Task::execute()` in M3 or any later milestone.

Implementation specifics:

- The MTC task in `crx10ial_tasks/src/fixed_pick_place_task.cpp` builds the full pick/place graph including `ModifyPlanningScene` stages for internal attach and detach.
- `plan_fixed_pick_place()` calls `task.plan(max_solutions)` and reports diagnostics. It does not return solutions for execution.
- `run_execute_mock()` re-derives waypoints (pregrasp, grasp, retreat, place, post-place) from configuration and the cell xacro, then sequences `MoveGroupInterface` moves with `crx10ial_gripper` service calls.
- A pytest source-contract check fails on any occurrence of `.execute(` or `execute_task_solution` in task or node sources.

## Consequences

Positive:

- Backend switching (fake -> Gazebo -> ROBOGUIDE -> hardware) never requires removing or rewriting MTC executor wiring.
- Runtime planning-scene state is single-sourced through `crx10ial_gripper`.
- Failure diagnostics from `Task::plan()` (`task.printState`, `task.explainFailure`) remain available for negative cases.

Negative:

- The mock execution path duplicates some logic that MTC already encodes (waypoint derivation, frame composition). The duplication is small (`translated_pose`, `compose_pose`) and lives in one file.
- Future contributors familiar with the MTC tutorial may try to call `Task::execute()`. The source-contract test catches this.

## Enforcement

- `crx10ial_tasks/test/test_task_source_contract.py` includes:
  - `assert ".execute(" not in combined`
  - `assert "execute_task_solution" not in combined`
- `check_docs.py` does not enforce this; it is a code-level invariant.
