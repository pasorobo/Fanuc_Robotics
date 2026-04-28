# 1. Adopt Ubuntu 22.04 / ROS 2 Humble

## Status

Accepted (2026-04-27)

## Context

The project targets a FANUC CRX-10iA/L workcell that must support staged validation in mock, simulation, ROBOGUIDE, and physical-hardware modes. The choice of OS and ROS 2 distribution shapes every downstream dependency: simulator (Gazebo Fortress vs Garden vs Harmonic), MoveIt branch, FANUC driver compatibility, available apt binaries.

Three credible options were considered:

- Ubuntu 22.04 + ROS 2 Humble Hawksbill (LTS, supported through May 2027 per REP 2000).
- Ubuntu 24.04 + ROS 2 Jazzy Jalisco (newer LTS, supported through May 2029).
- Ubuntu 22.04 + ROS 2 Iron (interim, EOL November 2024).

External constraints affecting the choice:

- The FANUC official ROS 2 driver (`FANUC-CORPORATION/fanuc_driver`) ships a `humble` branch. A `jazzy` branch is not yet stable as of project start.
- MoveIt Task Constructor apt binaries (`ros-humble-moveit-task-constructor-*`) are stable on Humble. Jazzy availability is uneven.
- Gazebo Fortress is the LTS Ignition release that pairs with Humble. Gazebo Harmonic pairs with Jazzy.
- The user's existing engineering hosts run Ubuntu 22.04.

## Decision

Adopt **Ubuntu 22.04 LTS + ROS 2 Humble Hawksbill** as the primary target for M0-M7.

A future migration to Ubuntu 24.04 / ROS 2 Jazzy / Gazebo Harmonic is acknowledged as a follow-on track but is explicitly outside the initial milestones. Code is kept "migration aware" by isolating simulator-specific assets in `crx10ial_sim` (see [ADR-0005](0005-cell-xacro-as-single-robot-description.md)) and by avoiding Humble-only API surfaces where Jazzy equivalents are well-known.

## Consequences

Positive:

- All upstream dependencies (FANUC driver, MoveIt 2, MTC, Gazebo Fortress, gz_ros2_control) are available as supported binaries or first-class source builds.
- Humble's two-year LTS window covers the project's planned M0-M7 timeline.
- Onboarding documentation can assume the standard ROS 2 Humble setup procedure.

Negative:

- Gazebo Fortress reaches end of life in September 2026, before Humble's own EOL. The project must plan a Fortress-to-Harmonic transition during the Humble window or carry an unsupported simulator briefly.
- Some packages and ecosystem trends move ahead on Jazzy first; back-porting fixes occasionally slows.

Mitigations:

- Track REP 2000 and the Gazebo release lifecycle from `docs/concepts/software_overview.md`.
- Keep simulator-specific code in `crx10ial_sim` so a Fortress-to-Harmonic swap is a contained change, not a workspace-wide rewrite.
- Re-evaluate the Jazzy migration after M7 lands and the Humble path is fully validated.
