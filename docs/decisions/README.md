# Architecture Decision Records

This directory holds the project's Architecture Decision Records (ADRs).

ADRs use the [Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) format with four sections: Status, Context, Decision, Consequences. Filenames follow the `0001-<kebab-title>.md` convention so [adr-tools](https://github.com/npryce/adr-tools) can be adopted later without renaming.

## How to add a new ADR

1. Pick the next available number.
2. Create `docs/decisions/NNNN-<kebab-title>.md` with the four required sections.
3. Add an entry to the table below.
4. If the new ADR supersedes an older one, set the older ADR's `## Status` line to `Superseded by ADR-NNNN (<date>)`.
5. If the project later switches to `adr-tools`, run `adr generate toc > README.md` and the existing files require no changes.

## Index

| ID | Title | Status |
|---|---|---|
| 0001 | [Adopt Ubuntu 22.04 / ROS 2 Humble](0001-adopt-ubuntu22-humble.md) | Accepted |
| 0002 | [Use FANUC Official ROS 2 Driver](0002-use-fanuc-official-driver.md) | Accepted |
| 0003 | [fake_gripper as Runtime Scene Owner (C1 Contract)](0003-fake-gripper-as-runtime-scene-owner.md) | Accepted |
| 0004 | [MoveIt Task Constructor Without Task::execute()](0004-mtc-without-task-execute.md) | Accepted |
| 0005 | [Cell xacro as Single robot_description Source](0005-cell-xacro-as-single-robot-description.md) | Accepted |
