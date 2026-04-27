# Ubuntu 22.04 / ROS 2 Humble Design for FANUC CRX-10iA/L

Status: Draft for user review
Date: 2026-04-27
Target repository: `pasorobo/Fanuc_Robotics`

## 1. Decision Summary

This project will target Ubuntu 22.04 LTS with ROS 2 Humble Hawksbill. The primary robot stack will be FANUC's official ROS 2 driver and description packages, with MoveIt 2 for planning, MoveIt Task Constructor for pick-and-place tasks, and Gazebo Sim Fortress with `gz_ros2_control` for simulation.

The previous Ubuntu 24.04 / ROS 2 Jazzy direction is not the primary path for this repository because the requested environment is Ubuntu 22.04. Jazzy may remain a future migration target, but the initial workspace, package layout, dependency manifests, and verification flow will be built around Humble.

Primary choices:

- OS: Ubuntu 22.04 LTS.
- ROS 2 distribution: Humble Hawksbill.
- Robot model: FANUC CRX-10iA/L, URDF model name `crx10ia_l`.
- Driver: `FANUC-CORPORATION/fanuc_driver`, Humble-compatible source build.
- Description: `FANUC-CORPORATION/fanuc_description`.
- Planning: MoveIt 2 and MoveIt Task Constructor.
- Simulation: Gazebo Sim Fortress through `gz_ros2_control`.
- Vision integration: a project-local ROS 2 bridge around FANUC iRVision results exposed through controller I/O, numeric registers, and position registers.

## 2. Goals

The project should support staged validation of a CRX-10iA/L workcell:

- Visualize and plan with the CRX-10iA/L in RViz.
- Validate ROS 2 control paths in mock, simulation, ROBOGUIDE, and physical hardware modes.
- Simulate pick-and-place with a table, work objects, end effector, and camera mounting frame.
- Build reusable grasp and place tasks with MoveIt Task Constructor.
- Integrate iRVision without requiring an unsupported or speculative ROS 2 iRVision driver.
- Provide a consistent interface for simulated vision, iRVision, and later camera-based perception.
- Keep hardware-specific setup isolated so development remains possible without the physical robot.

## 3. Non-Goals

The first design does not include:

- A custom replacement for FANUC's official ROS 2 driver.
- A complete iRVision implementation inside ROS 2.
- Safety-rated control implemented in ROS 2.
- Production deployment on the robot without a separate safety review.
- Multi-robot coordination.
- Full migration to Ubuntu 24.04 / Jazzy / Gazebo Harmonic in the initial milestone.

## 4. Environment Baseline

The baseline development host is:

- Ubuntu 22.04 LTS, amd64 first. arm64 can be considered after desktop validation.
- ROS 2 Humble desktop install.
- C++17 and Python 3.10, following the Humble platform baseline.
- `colcon`, `rosdep`, `vcs`, `git-lfs`, and standard ROS 2 developer tools.
- Native install as the first-class path. Docker is supported for repeatable build/test setup, but GUI tools such as RViz and Gazebo need explicit X11/Wayland/GPU handling.

The FANUC hardware path requires confirming the actual controller and installed options before physical testing:

- Controller family and software version.
- J519 Stream Motion and R912 Remote Motion, or S636 External Control Package.
- Whether the controller supports position register access through the selected driver version.
- Robot IP address, ROS PC IP address, subnet, and network isolation.
- Teach pendant safety settings, DCS constraints, payload schedule, and reduced speed workflow.

## 5. Upstream Dependencies

The project should use these upstream projects and documents as the baseline:

- FANUC ROS 2 Driver: `https://github.com/FANUC-CORPORATION/fanuc_driver`
- FANUC robot descriptions: `https://github.com/FANUC-CORPORATION/fanuc_description`
- FANUC supported URDF models: `https://fanuc-corporation.github.io/fanuc_driver_doc/main/docs/fanuc_description/supported_models.html`
- FANUC Humble quick start and requirements: `https://fanuc-corporation.github.io/fanuc_driver_doc/v1.1.1/docs/quick_start/quick_start.html`
- FANUC driver overview and feature list: `https://fanuc-corporation.github.io/fanuc_driver_doc/main/docs/fanuc_driver/fanuc_driver_overview.html`
- FANUC GPIO controller customization: `https://fanuc-corporation.github.io/fanuc_driver_doc/main/docs/fanuc_driver/controller_customization.html`
- ROS 2 Humble release/platform information: `https://docs.ros.org/en/humble/Releases/Release-Humble-Hawksbill.html`
- ROS 2 REP 2000 release schedule and Humble support duration: `https://www.ros.org/reps/rep-2000.html`
- MoveIt 2 Humble documentation: `https://moveit.picknik.ai/humble/`
- MoveIt Task Constructor pick-and-place tutorial: `https://moveit.picknik.ai/humble/doc/tutorials/pick_and_place_with_moveit_task_constructor/pick_and_place_with_moveit_task_constructor.html`
- `gz_ros2_control` Humble documentation: `https://control.ros.org/humble/doc/gz_ros2_control/doc/index.html`
- Gazebo release lifecycle: `https://gazebosim.org/docs/garden/releases/`
- ROS-Industrial Fanuc, reference only: `https://github.com/ros-industrial/fanuc`
- Unofficial ROS 2 Fanuc interface, reference only: `https://github.com/paolofrance/ros2_fanuc_interface`

Dependency policy:

- Use official FANUC packages as the primary source for robot description and hardware access.
- Prefer Humble branches or release tags for source dependencies.
- Pin exact commits in a lock file once the first build is verified.
- Use Debian packages where stable and available; use source builds for FANUC packages and packages unavailable or insufficient in Humble binaries.
- Treat ROS-Industrial ROS 1 assets and unofficial ROS 2 drivers as references, not runtime dependencies.

## 6. Repository Layout

The repository should be a ROS 2 workspace:

```text
Fanuc_Robotics/
  src/
    crx10ial_interfaces/
    crx10ial_cell_description/
    crx10ial_moveit_config/
    crx10ial_bringup/
    crx10ial_tasks/
    crx10ial_vision_bridge/
    crx10ial_gripper/
    crx10ial_safety/
    crx10ial_sim/
    crx10ial_tests/
  third_party.humble.repos
  third_party.humble.lock.repos
  docker/
    ubuntu22_humble/
  docs/
```

Package responsibilities:

- `crx10ial_interfaces`: project-local messages, services, and actions shared by task, vision, gripper, and safety packages.
- `crx10ial_cell_description`: workcell xacro composition. It extends the official CRX description with base, table, work objects, camera frames, end effector frames, and collision geometry.
- `crx10ial_moveit_config`: MoveIt 2 configuration for the CRX-10iA/L workcell, planning groups, end effector, kinematics, joint limits, planning scene defaults, and controller mapping.
- `crx10ial_bringup`: launch entry points and mode selection for `mock`, `gazebo`, `roboguide`, and `hardware`.
- `crx10ial_tasks`: MoveIt Task Constructor tasks for fixed-pose pick/place, vision-driven pick/place, pregrasp, retreat, and recovery flows.
- `crx10ial_vision_bridge`: uniform ROS 2 interface for fake vision, iRVision-backed detections, and future external camera perception.
- `crx10ial_gripper`: gripper abstraction over digital I/O, vacuum, Robotiq, OnRobot, or a simulated gripper.
- `crx10ial_safety`: runtime guards that are not safety-rated but help enforce project policies such as workspace limits, reduced speed mode checks, payload configuration checks, and stop/recovery service wrappers.
- `crx10ial_sim`: Gazebo world, SDF/xacro simulation extensions, `gz_ros2_control` parameters, sensors, and smoke-test worlds.
- `crx10ial_tests`: launch tests, xacro checks, planning smoke tests, and simulation smoke tests.

## 7. Runtime Modes

The same high-level task API should be usable across four modes:

### mock

Purpose: fastest local development path.

- Uses MoveIt 2 and mock hardware.
- Requires no Gazebo, ROBOGUIDE, or physical controller.
- First acceptance target: load CRX-10iA/L, create a planning scene, plan to named poses, and execute against mock hardware.

### gazebo

Purpose: validate workcell geometry, object collisions, gripper behavior, and task sequencing.

- Uses Gazebo Sim Fortress on Ubuntu 22.04/Humble.
- Uses `ros-humble-gz-ros2-control` where possible.
- Gazebo-specific files stay in `crx10ial_sim` so the workcell description and task logic are not tied to Fortress.
- Fortress reaches end-of-life in September 2026, so this package must be kept replaceable for a later Harmonic/Jazzy migration.

### roboguide

Purpose: validate the official FANUC driver against a FANUC virtual controller before real hardware.

- Runs ROBOGUIDE on Windows.
- ROS 2 workspace remains on Ubuntu 22.04.
- Network settings are documented separately from launch files.
- Used to validate connection, trajectory commands, I/O, numeric registers, position registers when supported, payload settings, and failure recovery.

### hardware

Purpose: controlled low-speed validation on the physical CRX-10iA/L.

- Requires documented controller version, FANUC software options, IP settings, safety limits, payload settings, and operator procedure.
- ROS 2 is not treated as a safety-rated layer.
- Launch files must require explicit `mode:=hardware` and `robot_ip:=...`.
- Hardware tests start with read-only status and I/O checks, then single-joint or small Cartesian motions, then planned task execution.

## 8. Control Architecture

The architecture has four layers:

```text
Task layer
  MoveIt Task Constructor, grasp/place state machines, task-level recovery

Planning layer
  MoveIt 2, planning scene, kinematics, collision checking, trajectory generation

Control adapter layer
  bringup modes, controller selection, gripper abstraction, vision bridge, safety checks

Execution layer
  mock hardware, gz_ros2_control, ROBOGUIDE via FANUC driver, physical controller via FANUC driver
```

The task layer should never call FANUC register services directly. It should call project-local interfaces such as `DetectObject`, `SetGripper`, or `PreparePayload`. The bridge packages own the mapping from those project interfaces to simulation, ROBOGUIDE, or real controller APIs.

This boundary keeps the pick-and-place logic stable while controller, iRVision, gripper, and simulator details evolve.

## 9. iRVision Integration Design

No robust, maintained, general-purpose ROS 2 iRVision OSS driver is assumed. iRVision is treated as a FANUC controller feature. ROS 2 integrates with it by using controller-visible state.

Nominal flow:

```text
crx10ial_tasks
  -> calls crx10ial_vision_bridge/DetectObject
  -> bridge sets configured DO/F/Group I/O or starts a configured TP program
  -> TP program runs iRVision process
  -> TP program writes result code to R[] or numeric register
  -> TP program writes found pose or offset to PR[] when supported
  -> bridge reads R[] and PR[] through FANUC driver services
  -> bridge returns PoseStamped and metadata to task layer
  -> task layer updates PlanningScene and builds MTC grasp stages
```

The first implementation should support three backends behind the same ROS 2 interface:

- `fake`: returns configured object poses for unit tests and mock demos.
- `sim`: returns poses from Gazebo ground truth or simulated perception.
- `fanuc_irvision`: triggers controller-side vision and reads back result registers.

The bridge must make register mappings explicit in YAML:

```yaml
vision_jobs:
  pick_part_a:
    trigger_io:
      type: DO
      index: 101
    busy_io:
      type: DI
      index: 101
    complete_io:
      type: DI
      index: 102
    result_register: 101
    found_pose_register: 50
    frame_id: vision_fixture
    output_frame_id: base_link
```

If the controller/driver combination cannot read PR[] directly, the fallback is to encode pose values into numeric registers or use a small FANUC TP/KAREL/socket bridge. That fallback is not part of M1-M4 and should only be added after ROBOGUIDE confirms the limitation.

## 10. Gripper Design

The gripper package exposes a small action/service surface independent of the physical end effector:

- Open.
- Close.
- Grasp with force/width hints when supported.
- Vacuum on/off when applicable.
- Read grasp status.
- Attach/detach simulated collision object in mock and simulation modes.

Initial implementation can use a simple digital output gripper or simulated parallel gripper. Specific hardware support for Robotiq, OnRobot, or vacuum tooling should be added after the actual end effector is selected.

## 11. Safety and Operations

Safety assumptions:

- ROS 2 application code is not safety-rated.
- FANUC safety functions, DCS, teach pendant settings, external emergency stop, speed limits, payload configuration, and operator procedure remain authoritative.
- Hardware mode must require explicit launch arguments and should print the target robot IP, controller mode, and configured payload before enabling motion.

Project-level safeguards:

- Separate `hardware` launch mode from `mock`, `gazebo`, and `roboguide`.
- Require a positive confirmation parameter such as `allow_motion:=true` for physical motion.
- Keep initial speed and acceleration scaling conservative.
- Add workspace-limit checks before sending plans.
- Log all hardware commands and controller results.
- Provide recovery procedures for connection loss, RMI timeout, robot fault, E-stop, and planning failure.

## 12. Milestones

### M0: Workspace Foundation

Deliverables:

- `third_party.humble.repos`.
- Ubuntu 22.04/Humble setup notes.
- Optional Dockerfile for repeatable build.
- Empty ROS 2 package skeletons.

Acceptance checks:

- `vcs import src < third_party.humble.repos`.
- `rosdep install --from-paths src --ignore-src -r -y`.
- `colcon build --symlink-install` reaches the expected baseline for installed dependencies.

### M1: RViz and MoveIt Mock

Deliverables:

- CRX-10iA/L workcell description loads in RViz.
- MoveIt config launches with mock hardware.
- Named poses and simple joint-space planning work.

Acceptance checks:

- Xacro expansion succeeds.
- `robot_state_publisher` publishes the expected TF tree.
- MoveIt planning scene contains table, work object, and end effector collision geometry.

### M2: Workcell and Gripper Model

Deliverables:

- Base/table/work objects/camera/gripper modeled.
- End-effector frames and grasp frames documented.
- Gripper interface and fake backend implemented.

Acceptance checks:

- Planning avoids static collision geometry.
- Gripper fake backend supports open/close and attach/detach in mock mode.

### M3: Fixed Pick-and-Place

Deliverables:

- MoveIt Task Constructor fixed-pose pick/place pipeline.
- Configurable object pose, grasp pose, place pose, and retreat vectors.

Acceptance checks:

- Mock mode completes a full pick/place task.
- Failed planning stages report actionable diagnostics.

### M4: Gazebo Fortress Simulation

Deliverables:

- Gazebo world and robot spawn.
- `gz_ros2_control` controller configuration.
- Basic gripper and object interaction smoke test.

Acceptance checks:

- Gazebo launches headless.
- Joint state broadcaster and trajectory controller are active.
- A short planned trajectory executes in simulation.

### M5: Vision Interface and Fake/Sim Backends

Deliverables:

- `DetectObject` interface.
- Fake backend.
- Gazebo or simulated perception backend.
- Task integration that consumes detected pose.

Acceptance checks:

- Same pick/place task runs with fixed pose and detected pose modes.
- Frame transforms are explicit and tested.

### M6: ROBOGUIDE Integration

Deliverables:

- ROBOGUIDE connection notes.
- Launch profile for virtual controller.
- I/O, numeric register, position register, status, and trajectory checks.

Acceptance checks:

- ROS 2 connects to virtual controller.
- Read/write I/O works.
- Read/write register path needed by iRVision bridge is confirmed or fallback is documented.
- A conservative trajectory executes in ROBOGUIDE.

### M7: Physical Hardware Bringup

Deliverables:

- Hardware checklist.
- Low-speed launch profile.
- Payload and workspace configuration.
- iRVision trigger/readback validation.

Acceptance checks:

- Read-only status and I/O checks pass.
- Single small motion test passes under supervision.
- Full pick/place is attempted only after safety and recovery procedures are reviewed.

## 13. Testing Strategy

Automated tests:

- Xacro expansion tests for the workcell.
- Package lint checks.
- Launch tests for mock mode.
- Unit tests for vision result parsing and frame conversion.
- Unit tests for gripper backend behavior.
- Planning smoke tests for named poses and one fixed pick/place scene.
- Gazebo headless smoke test after simulation is introduced.

Manual or hardware-in-the-loop tests:

- ROBOGUIDE connection and register mapping.
- Physical robot network setup.
- Physical I/O read/write.
- Position register read/write, if supported.
- iRVision TP program trigger and result readback.
- Low-speed trajectory execution.

## 14. Key Risks

### Controller option mismatch

Risk: the physical controller may not have the options or software version expected by the official ROS 2 driver.

Mitigation: make hardware work dependent on a controller inventory checklist before implementing physical launch defaults.

### Position register access may depend on driver/controller version

Risk: the iRVision design prefers PR[] readback, but PR[] access depends on driver and controller capability.

Mitigation: validate in ROBOGUIDE first. Keep numeric-register encoding or TP/KAREL/socket fallback as a later extension.

### Gazebo Fortress lifecycle

Risk: Fortress is a good fit for Ubuntu 22.04/Humble but reaches EOL in September 2026.

Mitigation: isolate simulator-specific code in `crx10ial_sim` and keep task, description, and bridge interfaces simulator-independent.

### End-effector unknowns

Risk: gripper type affects collision geometry, grasp planning, I/O mapping, and payload.

Mitigation: start with a generic gripper abstraction and a fake backend. Add physical gripper support after hardware is selected.

### iRVision frame calibration

Risk: found poses are only useful if FANUC frames, ROS TF frames, camera frames, tool frames, and calibration assumptions are consistent.

Mitigation: document every transform, add frame validation tests, and make `frame_id` and `output_frame_id` explicit in bridge configuration.

## 15. Open Inputs Needed

Before hardware and iRVision implementation, collect:

- Robot controller model and software version.
- Installed FANUC options: J519, R912, S636, iRVision, KAREL/socket options if any.
- Actual CRX-10iA/L payload and end effector.
- Gripper make/model and control method.
- iRVision job names, result codes, register assignments, and coordinate frame convention.
- ROBOGUIDE availability and version.
- Preferred development mode: native Ubuntu, Docker, WSL2, or mixed.
- Whether the PC must also support GPU-accelerated Gazebo GUI.

## 16. Next Step After User Review

After this design is reviewed and accepted, create an implementation plan that starts with M0 and M1 only. The first implementation plan should not attempt hardware or iRVision integration. It should establish a buildable Humble workspace, import official FANUC dependencies, and prove that CRX-10iA/L mock planning works.
