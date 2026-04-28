# Glossary

Short definitions for terms used across the project.

## A

**ACM (Allowed Collision Matrix)**
MoveIt's per-pair toggle of which links and objects are allowed to be in contact. Used during grasping to allow the gripper to touch the object.

**ament_cmake / ament_python**
ROS 2 package build types. `ament_cmake` is for C++ packages and packages that ship configuration files. `ament_python` is for pure-Python ROS 2 nodes. Each top-level project package picks one.

**ADR (Architecture Decision Record)**
A short Markdown document recording a single technical decision: why it was made, what was decided, and the trade-offs accepted. See [docs/decisions/](../decisions/).

## C

**colcon**
The ROS 2 build tool. Builds the workspace from `src/` into `install/`.

**CommonMark**
The Markdown specification used by this repository's docs.

**Controller (ros2_control)**
A plugin that uses the hardware interface to drive a joint or sensor. Examples: `joint_trajectory_controller`, `joint_state_broadcaster`.

**CRX-10iA/L**
The FANUC collaborative robot the project targets. 6 axes, 1.249 m reach, 10 kg payload.

## D

**DCS (Dual Check Safety)**
FANUC's safety-rated subsystem on the controller. Independent of ROS 2.

**DI / DO / GI / GO / RI / RO**
FANUC controller I/O families. Digital In/Out, Group In/Out, Robot In/Out.

## E

**end_effector**
The link in this project's cell xacro that anchors gripper geometry. Sits between `flange` (FANUC) and `tool_link` (project).

## F

**fake_gripper**
The mock backend that owns runtime planning-scene attach/detach. See [decisions/0003](../decisions/0003-fake-gripper-as-runtime-scene-owner.md).

**flange**
FANUC's mechanical tool mounting frame. Tools attach here.

## G

**Gazebo Fortress**
Ignition Fortress, the LTS simulator targeted by M4. Supports `gz_ros2_control`.

**grasp_link**
Project frame at which objects are attached during grasping. Convention: +X approach, +Y jaw opening, +Z up. See [frames.md](../frames.md).

**gz_ros2_control**
The Gazebo Fortress bridge to ros2_control.

## H

**Humble (Hawksbill)**
ROS 2 LTS release for Ubuntu 22.04. The project's primary target.

## I

**iRVision**
FANUC's built-in vision system. Runs on the controller. Results are exposed through I/O and registers.

## J

**J1..J6**
The six joints of the CRX-10iA/L, numbered from base to wrist.

**J519 Stream Motion**
FANUC software option that exposes high-rate joint streaming. Required by the FANUC ROS 2 driver.

## M

**MoveIt 2**
The motion-planning framework. Hosts the `move_group` node.

**MoveIt Task Constructor (MTC)**
Stage-based task orchestration on top of MoveIt 2. The project uses it for fixed pick/place.

**Mock mode**
Project run mode with no Gazebo, no ROBOGUIDE, and no physical robot. Uses FANUC's mock hardware interface.

## O

**OMPL**
The default motion-planning library MoveIt 2 uses for sampling-based planning.

## P

**PR[]**
Position register on the FANUC controller. Stores Cartesian or joint poses. Used by iRVision result readback when supported.

**Planning scene**
MoveIt's view of the world: robot state, world collision objects, attached collision objects, ACM.

## R

**R[]**
Numeric register on the FANUC controller. Used to pass scalar values such as iRVision result codes.

**R-30iB Mini Plus**
FANUC controller used with the CRX series.

**R912 Remote Motion Interface (RMI)**
FANUC software option for command/status remote control.

**ROBOGUIDE**
FANUC's Windows-only virtual controller and cell simulator. Used in M6 to validate the driver before real hardware.

**ros2_control**
ROS 2's standard hardware abstraction framework.

**rosdep**
ROS 2's dependency installer. Reads `package.xml` and installs system packages.

## S

**S636 External Control Package**
FANUC software option, alternative to J519/R912 for external command.

**SRDF**
MoveIt's Semantic Robot Description Format. Adds groups, end-effectors, named states on top of URDF.

## T

**Task (MTC)**
A MoveIt Task Constructor task: a tree of stages plus a planner. `Task::plan()` finds solutions; `Task::execute()` is intentionally not used in this project.

**Teach Pendant**
The handheld operator interface for FANUC controllers. Also where DCS and safety are configured.

**tool0 / tool_link**
`tool0` is FANUC's default tool frame at flange. `tool_link` is this project's extension where the gripper geometry attaches.

## U

**URDF**
Unified Robot Description Format. The rigid-body model of the robot.

## V

**vcs (vcstool)**
Tool that fetches multiple git repositories listed in a `.repos` YAML file. Used for FANUC source dependencies.

## W

**world**
Top frame of the planning scene. Static.
