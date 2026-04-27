# M2 Workcell Gripper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a documented CRX-10iA/L mock gripper model, ROS 2 gripper interface, fake gripper backend, and M2 verification that planning and attach/detach work in mock mode.

**Architecture:** Keep static world collision objects in `crx10ial_bringup.mock_scene`; keep gripper state and attached-object scene diffs in `crx10ial_gripper`. MoveIt mock bringup must use the local workcell xacro as `robot_description` so `tool_link`, gripper links, and `grasp_link` are part of the planning robot model. Gazebo, physical gripper drivers, ROBOGUIDE, iRVision, and MoveIt Task Constructor remain out of this milestone.

**Tech Stack:** Ubuntu 22.04, ROS 2 Humble, colcon, ament_cmake, ament_python, rosidl service interfaces, xacro, FANUC official driver and description packages, MoveIt 2 planning scene services, Python 3.10, pytest.

---

## Scope

This plan implements only the approved design's M2 milestone:

- Model base/table/work object/camera/gripper in the workcell description.
- Document end-effector, tool, and grasp frame conventions.
- Add a small gripper command interface with fake backend.
- Support `open`, `close`, `vacuum_on`, `vacuum_off`, `attach`, `detach`, and `get_state` in mock mode.
- Verify MoveIt can plan with static collision geometry active.
- Verify fake attach/detach updates the MoveIt planning scene through `/apply_planning_scene`.

This plan does not add Gazebo, MoveIt Task Constructor pick/place, physical gripper IO, iRVision, or ROBOGUIDE integration.

## Design Decisions

- Frame hierarchy: `end_effector -> tool_link -> grasp_link`.
- Geometry hierarchy: `tool_link -> gripper_palm`, `tool_link -> left_finger`, `tool_link -> right_finger`.
- `grasp_link` convention:
  - `+X` is the approach direction from wrist toward the object.
  - `+Y` is the parallel-jaw opening axis.
  - `+Z` completes the right-handed frame and points upward from the palm.
- MTC in M3 should place the object at `grasp_link`; pre-grasp retreat is along `-X`, approach is along `+X`.
- `mock_scene_publisher` owns static world objects only: table, free work object, and camera stand.
- `fake_gripper` owns attached-object transitions only: remove `work_object` from world, attach it to `grasp_link`, then restore it to world on detach.
- Vacuum commands are implemented in the fake backend as state toggles without physical IO.

## File Structure

Create or modify these files:

```text
docs/gripper_frames.md
docs/superpowers/plans/2026-04-28-m2-workcell-gripper.md
src/crx10ial_interfaces/CMakeLists.txt
src/crx10ial_interfaces/package.xml
src/crx10ial_interfaces/README.md
src/crx10ial_interfaces/srv/AttachObject.srv
src/crx10ial_interfaces/srv/CommandGripper.srv
src/crx10ial_interfaces/srv/DetachObject.srv
src/crx10ial_interfaces/srv/GetGripperState.srv
src/crx10ial_cell_description/package.xml
src/crx10ial_cell_description/test/test_cell_description.py
src/crx10ial_cell_description/urdf/crx10ial_cell.urdf.xacro
src/crx10ial_bringup/launch/mock.launch.py
src/crx10ial_bringup/test/test_mock_scene.py
src/crx10ial_gripper/CMakeLists.txt
src/crx10ial_gripper/package.xml
src/crx10ial_gripper/README.md
src/crx10ial_gripper/resource/crx10ial_gripper
src/crx10ial_gripper/setup.cfg
src/crx10ial_gripper/setup.py
src/crx10ial_gripper/crx10ial_gripper/__init__.py
src/crx10ial_gripper/crx10ial_gripper/fake_gripper.py
src/crx10ial_gripper/crx10ial_gripper/fake_gripper_node.py
src/crx10ial_gripper/test/test_fake_gripper.py
src/crx10ial_gripper/test/test_fake_gripper_node.py
```

Responsibilities:

- `docs/gripper_frames.md` documents frame names, axes, and ownership boundaries for M2 and M3.
- `crx10ial_interfaces` owns small ROS 2 service definitions for gripper commands and state.
- `crx10ial_cell_description` owns robot/tool/workcell geometry and xacro tests.
- `crx10ial_bringup` owns mock launch composition and static collision-object publication.
- `crx10ial_gripper` owns fake gripper state, service server, and MoveIt planning-scene attach/detach diffs.

## Task 0: Prepare M2 Branch and Reconfirm M1 Baseline

**Files:**
- No repository files are modified.

- [ ] **Step 1: Start from the pushed M0/M1 branch**

Run:

```bash
cd ~/Develop/Fanuc/Fanuc_Robotics
git fetch origin
git switch --detach origin/m0-m1-humble-workspace
git switch -c m2-workcell-gripper
git status --short --branch
```

Expected: status prints `## m2-workcell-gripper` and no modified files.

- [ ] **Step 2: Reconfirm dependencies and build baseline**

Run:

```bash
source /opt/ros/humble/setup.bash
./scripts/import_dependencies.sh third_party.humble.lock.repos
# Humble rosdep has no rule for the buildtool key `ament_python`; the ROS install already provides it.
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble --skip-keys ament_python
colcon build --symlink-install
```

Expected: `colcon build` finishes with all workspace packages built. Warnings from upstream `fanuc_libs` or `fanuc_controllers` do not fail this step.

- [ ] **Step 3: Reconfirm M1 tests**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon test --packages-select crx10ial_cell_description crx10ial_bringup
colcon test-result --verbose
```

Expected: no test failures.

## Task 1: Add Gripper Service Interfaces

**Files:**
- Modify: `src/crx10ial_interfaces/CMakeLists.txt`
- Modify: `src/crx10ial_interfaces/package.xml`
- Modify: `src/crx10ial_interfaces/README.md`
- Create: `src/crx10ial_interfaces/srv/AttachObject.srv`
- Create: `src/crx10ial_interfaces/srv/CommandGripper.srv`
- Create: `src/crx10ial_interfaces/srv/DetachObject.srv`
- Create: `src/crx10ial_interfaces/srv/GetGripperState.srv`

- [ ] **Step 1: Write the service definitions**

Create `src/crx10ial_interfaces/srv/CommandGripper.srv`:

```srv
uint8 OPEN=1
uint8 CLOSE=2
uint8 VACUUM_ON=3
uint8 VACUUM_OFF=4

uint8 command
float64 width_m
float64 force_n
---
bool success
string message
uint8 state
float64 width_m
float64 force_n
string attached_object_id
bool vacuum_enabled
```

Create `src/crx10ial_interfaces/srv/AttachObject.srv`:

```srv
string object_id
---
bool success
string message
string attached_object_id
```

Create `src/crx10ial_interfaces/srv/DetachObject.srv`:

```srv
---
bool success
string message
string detached_object_id
```

Create `src/crx10ial_interfaces/srv/GetGripperState.srv`:

```srv
uint8 IDLE=0
uint8 OPEN=1
uint8 CLOSED=2
uint8 HOLDING=3

---
uint8 state
float64 width_m
float64 force_n
string attached_object_id
bool vacuum_enabled
```

- [ ] **Step 2: Wire interface generation**

Replace `src/crx10ial_interfaces/CMakeLists.txt` with:

```cmake
cmake_minimum_required(VERSION 3.8)
project(crx10ial_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/AttachObject.srv"
  "srv/CommandGripper.srv"
  "srv/DetachObject.srv"
  "srv/GetGripperState.srv"
)

ament_export_dependencies(rosidl_default_runtime)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

Replace `src/crx10ial_interfaces/package.xml` with:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>crx10ial_interfaces</name>
  <version>0.1.0</version>
  <description>Shared interfaces for the CRX-10iA/L workcell.</description>
  <maintainer email="codex@openai.com">Fanuc Robotics Maintainers</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>rosidl_default_generators</buildtool_depend>

  <exec_depend>rosidl_default_runtime</exec_depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <member_of_group>rosidl_interface_packages</member_of_group>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Replace `src/crx10ial_interfaces/README.md` with:

```markdown
# crx10ial_interfaces

Shared ROS 2 interfaces for the CRX-10iA/L workcell.

## Gripper services

- `CommandGripper`: command the fake gripper to open, close, enable vacuum state, or disable vacuum state.
- `AttachObject`: attach a known world collision object to the configured gripper link.
- `DetachObject`: detach the currently held object and restore it as a world collision object.
- `GetGripperState`: read the fake gripper state.
```

- [ ] **Step 3: Build interface package**

Run:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select crx10ial_interfaces
```

Expected: `crx10ial_interfaces` builds and generated Python service modules are installed.

- [ ] **Step 4: Verify generated service imports**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
python3 - <<'PY'
from crx10ial_interfaces.srv import (
    AttachObject,
    CommandGripper,
    DetachObject,
    GetGripperState,
)

assert CommandGripper.Request.OPEN == 1
assert CommandGripper.Request.CLOSE == 2
assert CommandGripper.Request.VACUUM_ON == 3
assert CommandGripper.Request.VACUUM_OFF == 4
assert GetGripperState.Request.IDLE == 0
assert GetGripperState.Request.HOLDING == 3
print("gripper service imports ok")
PY
```

Expected: prints `gripper service imports ok`.

- [ ] **Step 5: Commit interfaces**

Run:

```bash
git add src/crx10ial_interfaces
git commit -m "feat: add gripper service interfaces"
```

## Task 2: Model Gripper Frames and Document Frame Convention

**Files:**
- Create: `docs/gripper_frames.md`
- Modify: `src/crx10ial_cell_description/package.xml`
- Modify: `src/crx10ial_cell_description/test/test_cell_description.py`
- Modify: `src/crx10ial_cell_description/urdf/crx10ial_cell.urdf.xacro`

- [ ] **Step 1: Write failing xacro tests for gripper frames and control tags**

Append these tests to `src/crx10ial_cell_description/test/test_cell_description.py`:

```python
def _joint_origin(root: ET.Element, joint_name: str) -> ET.Element:
    joint = next(
        joint
        for joint in root.findall("joint")
        if joint.attrib["name"] == joint_name
    )
    return joint.find("origin")


def test_cell_xacro_contains_documented_gripper_frames():
    root = _expanded_cell_urdf()
    links = {link.attrib["name"] for link in root.findall("link")}
    joints = {joint.attrib["name"] for joint in root.findall("joint")}

    assert "tool_link" in links
    assert "gripper_palm" in links
    assert "left_finger" in links
    assert "right_finger" in links
    assert "grasp_link" in links

    assert "end_effector_to_tool_link" in joints
    assert "tool_link_to_gripper_palm" in joints
    assert "tool_link_to_left_finger" in joints
    assert "tool_link_to_right_finger" in joints
    assert "tool_link_to_grasp_link" in joints

    grasp_origin = _joint_origin(root, "tool_link_to_grasp_link")
    assert grasp_origin.attrib["xyz"] == "0.18 0 0"
    assert grasp_origin.attrib["rpy"] == "0 0 0"


def test_cell_xacro_includes_ros2_control_for_mock_moveit_bringup():
    root = _expanded_cell_urdf()
    ros2_control_names = {
        control.attrib["name"]
        for control in root.findall("ros2_control")
    }

    assert "crx10ia_l" in ros2_control_names
```

In `test_cell_xacro_expands_and_contains_static_workcell_links`, replace the `tool_stub` assertions with:

```python
    assert "tool_link" in links
    assert "gripper_palm" in links
    assert "left_finger" in links
    assert "right_finger" in links
    assert "grasp_link" in links

    assert "end_effector_to_tool_link" in joints
    assert "tool_link_to_gripper_palm" in joints
    assert "tool_link_to_left_finger" in joints
    assert "tool_link_to_right_finger" in joints
    assert "tool_link_to_grasp_link" in joints
```

In `test_cell_urdf_has_single_root_and_valid_joint_references`, replace:

```python
    assert ("end_effector", "tool_stub") in parent_child_pairs
```

with:

```python
    assert ("end_effector", "tool_link") in parent_child_pairs
    assert ("tool_link", "grasp_link") in parent_child_pairs
```

- [ ] **Step 2: Run xacro tests and verify they fail**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
pytest src/crx10ial_cell_description/test/test_cell_description.py -q
```

Expected: tests fail because `tool_link`, finger links, `grasp_link`, and `ros2_control` are not in the current cell xacro.

- [ ] **Step 3: Add frame documentation**

Create `docs/gripper_frames.md`:

````markdown
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

Physical gripper IO and vendor-specific payload behavior are outside M2. The fake backend exposes the same service surface for subsequent hardware-specific nodes.
````

- [ ] **Step 4: Update cell description package dependencies**

Add the FANUC hardware interface dependency to `src/crx10ial_cell_description/package.xml`:

```xml
  <exec_depend>fanuc_hardware_interface</exec_depend>
```

The dependency block should contain both `fanuc_crx_description` and `fanuc_hardware_interface`.

- [ ] **Step 5: Replace cell xacro with gripper and ros2_control-aware workcell**

Replace `src/crx10ial_cell_description/urdf/crx10ial_cell.urdf.xacro` with:

```xml
<?xml version="1.0"?>
<robot name="crx10ial_cell" xmlns:xacro="http://wiki.ros.org/xacro">
  <xacro:arg name="robot_ip" default="1.1.1.1"/>
  <xacro:arg name="rmi_port" default="16001"/>
  <xacro:arg name="stream_motion_port" default="60015"/>
  <xacro:arg name="gpio_configuration" default=""/>
  <xacro:arg name="payload_schedule" default="1"/>
  <xacro:arg name="out_cmd_interp_buff_target" default="8"/>
  <xacro:arg name="force_sensor_type" default="1"/>
  <xacro:arg name="use_mock" default="true"/>

  <xacro:include filename="$(find fanuc_crx_description)/urdf/crx10ia_l_urdf_macro.xacro"/>
  <xacro:if value="$(arg use_mock)">
    <xacro:include filename="$(find fanuc_hardware_interface)/config/crx_mock_ros2_control_macro.xacro"/>
  </xacro:if>
  <xacro:unless value="$(arg use_mock)">
    <xacro:include filename="$(find fanuc_hardware_interface)/config/crx_physical_ros2_control_macro.xacro"/>
  </xacro:unless>

  <link name="world"/>
  <link name="end_effector"/>

  <xacro:crx10ia_l parent="world" child="end_effector">
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </xacro:crx10ia_l>

  <link name="table">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="1.0 0.7 0.04"/></geometry>
      <material name="mat_table_gray"><color rgba="0.45 0.47 0.50 1.0"/></material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="1.0 0.7 0.04"/></geometry>
    </collision>
  </link>
  <joint name="world_to_table" type="fixed">
    <parent link="world"/><child link="table"/>
    <origin xyz="0.75 0 0.70" rpy="0 0 0"/>
  </joint>

  <link name="work_object">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="0.08 0.08 0.05"/></geometry>
      <material name="mat_work_object_blue"><color rgba="0.1 0.35 0.85 1.0"/></material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="0.08 0.08 0.05"/></geometry>
    </collision>
  </link>
  <joint name="table_to_work_object" type="fixed">
    <parent link="table"/><child link="work_object"/>
    <origin xyz="-0.20 0 0.045" rpy="0 0 0"/>
  </joint>

  <link name="camera_stand">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="0.05 0.05 0.70"/></geometry>
      <material name="mat_camera_stand_dark"><color rgba="0.12 0.12 0.12 1.0"/></material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="0.05 0.05 0.70"/></geometry>
    </collision>
  </link>
  <joint name="world_to_camera_stand" type="fixed">
    <parent link="world"/><child link="camera_stand"/>
    <origin xyz="0.35 -0.55 0.35" rpy="0 0 0"/>
  </joint>

  <link name="tool_link"/>
  <joint name="end_effector_to_tool_link" type="fixed">
    <parent link="end_effector"/><child link="tool_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

  <link name="gripper_palm">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="0.08 0.10 0.08"/></geometry>
      <material name="mat_gripper_palm_green"><color rgba="0.15 0.55 0.25 1.0"/></material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="0.08 0.10 0.08"/></geometry>
    </collision>
  </link>
  <joint name="tool_link_to_gripper_palm" type="fixed">
    <parent link="tool_link"/><child link="gripper_palm"/>
    <origin xyz="0.06 0 0" rpy="0 0 0"/>
  </joint>

  <link name="left_finger">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="0.12 0.02 0.04"/></geometry>
      <material name="mat_gripper_finger_dark"><color rgba="0.08 0.08 0.08 1.0"/></material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="0.12 0.02 0.04"/></geometry>
    </collision>
  </link>
  <joint name="tool_link_to_left_finger" type="fixed">
    <parent link="tool_link"/><child link="left_finger"/>
    <origin xyz="0.14 0.055 0" rpy="0 0 0"/>
  </joint>

  <link name="right_finger">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="0.12 0.02 0.04"/></geometry>
      <material name="mat_gripper_finger_dark"><color rgba="0.08 0.08 0.08 1.0"/></material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="0.12 0.02 0.04"/></geometry>
    </collision>
  </link>
  <joint name="tool_link_to_right_finger" type="fixed">
    <parent link="tool_link"/><child link="right_finger"/>
    <origin xyz="0.14 -0.055 0" rpy="0 0 0"/>
  </joint>

  <link name="grasp_link"/>
  <joint name="tool_link_to_grasp_link" type="fixed">
    <parent link="tool_link"/><child link="grasp_link"/>
    <origin xyz="0.18 0 0" rpy="0 0 0"/>
  </joint>

  <xacro:crx_control name="crx10ia_l"/>
</robot>
```

- [ ] **Step 6: Run xacro tests**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
pytest src/crx10ial_cell_description/test/test_cell_description.py -q
```

Expected: all `crx10ial_cell_description` tests pass.

- [ ] **Step 7: Verify expanded URDF contains gripper links**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
xacro src/crx10ial_cell_description/urdf/crx10ial_cell.urdf.xacro > /tmp/crx10ial_cell_m2.urdf
grep -q 'link name="grasp_link"' /tmp/crx10ial_cell_m2.urdf
grep -q 'joint name="tool_link_to_grasp_link"' /tmp/crx10ial_cell_m2.urdf
grep -q 'ros2_control name="crx10ia_l"' /tmp/crx10ial_cell_m2.urdf
```

Expected: all `grep` commands succeed.

- [ ] **Step 8: Commit gripper model and frame docs**

Run:

```bash
git add docs/gripper_frames.md src/crx10ial_cell_description
git commit -m "feat: model CRX mock gripper frames"
```

## Task 3: Implement Fake Gripper Backend Logic

**Files:**
- Modify: `src/crx10ial_gripper/package.xml`
- Create: `src/crx10ial_gripper/setup.cfg`
- Create: `src/crx10ial_gripper/setup.py`
- Create: `src/crx10ial_gripper/resource/crx10ial_gripper`
- Create: `src/crx10ial_gripper/crx10ial_gripper/__init__.py`
- Create: `src/crx10ial_gripper/crx10ial_gripper/fake_gripper.py`
- Create: `src/crx10ial_gripper/test/test_fake_gripper.py`
- Delete: `src/crx10ial_gripper/CMakeLists.txt`

- [ ] **Step 1: Write failing backend tests**

Create `src/crx10ial_gripper/test/test_fake_gripper.py`:

```python
import pytest
from moveit_msgs.msg import CollisionObject

from crx10ial_gripper.fake_gripper import (
    COMMAND_CLOSE,
    COMMAND_OPEN,
    COMMAND_VACUUM_OFF,
    COMMAND_VACUUM_ON,
    FakeGripperBackend,
    GRIPPER_STATE_CLOSED,
    GRIPPER_STATE_HOLDING,
    GRIPPER_STATE_OPEN,
)


def test_command_open_and_close_update_state():
    backend = FakeGripperBackend()

    opened = backend.command(COMMAND_OPEN, width_m=0.08, force_n=0.0)
    assert opened.state == GRIPPER_STATE_OPEN
    assert opened.width_m == 0.08
    assert opened.force_n == 0.0

    closed = backend.command(COMMAND_CLOSE, width_m=0.02, force_n=40.0)
    assert closed.state == GRIPPER_STATE_CLOSED
    assert closed.width_m == 0.02
    assert closed.force_n == 40.0


def test_vacuum_commands_toggle_fake_state():
    backend = FakeGripperBackend()

    state = backend.command(COMMAND_VACUUM_ON, width_m=0.0, force_n=0.0)
    assert state.vacuum_enabled is True

    state = backend.command(COMMAND_VACUUM_OFF, width_m=0.0, force_n=0.0)
    assert state.vacuum_enabled is False


def test_rejects_invalid_width_force_and_command():
    backend = FakeGripperBackend()

    with pytest.raises(ValueError, match="width_m"):
        backend.command(COMMAND_OPEN, width_m=-0.01, force_n=0.0)

    with pytest.raises(ValueError, match="width_m"):
        backend.command(COMMAND_OPEN, width_m=0.20, force_n=0.0)

    with pytest.raises(ValueError, match="force_n"):
        backend.command(COMMAND_CLOSE, width_m=0.02, force_n=-1.0)

    with pytest.raises(ValueError, match="command"):
        backend.command(99, width_m=0.02, force_n=1.0)


def test_attach_scene_diff_removes_world_object_and_attaches_to_grasp_link():
    backend = FakeGripperBackend()

    scene = backend.attach_object("work_object")

    assert backend.state.attached_object_id == "work_object"
    assert backend.state.state == GRIPPER_STATE_HOLDING
    assert scene.is_diff is True
    assert scene.robot_state.is_diff is True
    assert len(scene.world.collision_objects) == 1
    assert scene.world.collision_objects[0].id == "work_object"
    assert scene.world.collision_objects[0].operation == CollisionObject.REMOVE

    attached = scene.robot_state.attached_collision_objects[0]
    assert attached.link_name == "grasp_link"
    assert attached.object.id == "work_object"
    assert attached.object.header.frame_id == "grasp_link"
    assert attached.object.operation == CollisionObject.ADD
    assert set(attached.touch_links) == {
        "end_effector",
        "tool_link",
        "gripper_palm",
        "left_finger",
        "right_finger",
        "grasp_link",
    }


def test_detach_scene_diff_removes_attached_object_and_restores_world_object():
    backend = FakeGripperBackend()
    backend.attach_object("work_object")

    scene = backend.detach_object()

    assert backend.state.attached_object_id == ""
    assert scene.robot_state.attached_collision_objects[0].object.id == "work_object"
    assert scene.robot_state.attached_collision_objects[0].object.operation == CollisionObject.REMOVE

    restored = scene.world.collision_objects[0]
    assert restored.id == "work_object"
    assert restored.header.frame_id == "world"
    assert restored.operation == CollisionObject.ADD
    assert restored.primitive_poses[0].position.x == 0.55
    assert restored.primitive_poses[0].position.y == 0.0
    assert restored.primitive_poses[0].position.z == 0.745


def test_attach_rejects_unknown_or_duplicate_object_and_detach_requires_object():
    backend = FakeGripperBackend()

    with pytest.raises(ValueError, match="unknown object_id"):
        backend.attach_object("missing")

    backend.attach_object("work_object")
    with pytest.raises(ValueError, match="already attached"):
        backend.attach_object("work_object")

    backend.detach_object()
    with pytest.raises(ValueError, match="no object attached"):
        backend.detach_object()
```

- [ ] **Step 2: Convert gripper package to ament_python skeleton**

Replace `src/crx10ial_gripper/package.xml` with:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>crx10ial_gripper</name>
  <version>0.1.0</version>
  <description>Gripper abstraction package for the CRX-10iA/L workcell.</description>
  <maintainer email="codex@openai.com">Fanuc Robotics Maintainers</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_python</buildtool_depend>

  <exec_depend>crx10ial_interfaces</exec_depend>
  <exec_depend>geometry_msgs</exec_depend>
  <exec_depend>moveit_msgs</exec_depend>
  <exec_depend>rclpy</exec_depend>
  <exec_depend>shape_msgs</exec_depend>

  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

Create `src/crx10ial_gripper/setup.cfg`:

```ini
[develop]
script_dir=$base/lib/crx10ial_gripper
[install]
install_scripts=$base/lib/crx10ial_gripper
```

Create `src/crx10ial_gripper/setup.py`:

```python
from setuptools import find_packages, setup

package_name = "crx10ial_gripper"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Fanuc Robotics Maintainers",
    maintainer_email="codex@openai.com",
    description="Gripper abstraction package for the CRX-10iA/L workcell.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "fake_gripper = crx10ial_gripper.fake_gripper_node:main",
        ],
    },
)
```

Create empty marker files:

```bash
mkdir -p src/crx10ial_gripper/resource src/crx10ial_gripper/crx10ial_gripper
touch src/crx10ial_gripper/resource/crx10ial_gripper
touch src/crx10ial_gripper/crx10ial_gripper/__init__.py
rm src/crx10ial_gripper/CMakeLists.txt
```

- [ ] **Step 3: Run backend tests and verify they fail**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
pytest src/crx10ial_gripper/test/test_fake_gripper.py -q
```

Expected: tests fail because `crx10ial_gripper.fake_gripper` does not exist yet.

- [ ] **Step 4: Implement fake gripper backend**

Create `src/crx10ial_gripper/crx10ial_gripper/fake_gripper.py`:

```python
from dataclasses import dataclass
from typing import Dict, Sequence

from geometry_msgs.msg import Pose
from moveit_msgs.msg import AttachedCollisionObject, CollisionObject, PlanningScene
from shape_msgs.msg import SolidPrimitive


COMMAND_OPEN = 1
COMMAND_CLOSE = 2
COMMAND_VACUUM_ON = 3
COMMAND_VACUUM_OFF = 4

GRIPPER_STATE_IDLE = 0
GRIPPER_STATE_OPEN = 1
GRIPPER_STATE_CLOSED = 2
GRIPPER_STATE_HOLDING = 3

MAX_WIDTH_M = 0.12


@dataclass(frozen=True)
class ObjectSpec:
    object_id: str
    dimensions: tuple[float, float, float]
    world_xyz: tuple[float, float, float]


@dataclass
class GripperState:
    state: int = GRIPPER_STATE_IDLE
    width_m: float = MAX_WIDTH_M
    force_n: float = 0.0
    attached_object_id: str = ""
    vacuum_enabled: bool = False


WORK_OBJECT = ObjectSpec(
    object_id="work_object",
    dimensions=(0.08, 0.08, 0.05),
    world_xyz=(0.55, 0.0, 0.745),
)


def _identity_pose(x: float, y: float, z: float) -> Pose:
    pose = Pose()
    pose.position.x = x
    pose.position.y = y
    pose.position.z = z
    pose.orientation.w = 1.0
    return pose


def _box_primitive(dimensions: Sequence[float]) -> SolidPrimitive:
    primitive = SolidPrimitive()
    primitive.type = SolidPrimitive.BOX
    primitive.dimensions = list(dimensions)
    return primitive


def _collision_object_add(spec: ObjectSpec, frame_id: str, pose: Pose) -> CollisionObject:
    obj = CollisionObject()
    obj.header.frame_id = frame_id
    obj.id = spec.object_id
    obj.primitives.append(_box_primitive(spec.dimensions))
    obj.primitive_poses.append(pose)
    obj.operation = CollisionObject.ADD
    return obj


def _collision_object_remove(object_id: str, frame_id: str) -> CollisionObject:
    obj = CollisionObject()
    obj.header.frame_id = frame_id
    obj.id = object_id
    obj.operation = CollisionObject.REMOVE
    return obj


class FakeGripperBackend:
    def __init__(
        self,
        attach_link: str = "grasp_link",
        world_frame: str = "world",
        touch_links: Sequence[str] | None = None,
        object_specs: Sequence[ObjectSpec] = (WORK_OBJECT,),
    ) -> None:
        self.attach_link = attach_link
        self.world_frame = world_frame
        self.touch_links = list(
            touch_links
            if touch_links is not None
            else (
                "end_effector",
                "tool_link",
                "gripper_palm",
                "left_finger",
                "right_finger",
                "grasp_link",
            )
        )
        self.object_specs: Dict[str, ObjectSpec] = {
            spec.object_id: spec for spec in object_specs
        }
        self.state = GripperState()

    def command(self, command: int, width_m: float, force_n: float) -> GripperState:
        self._validate_width(width_m)
        self._validate_force(force_n)

        if command == COMMAND_OPEN:
            self.state.state = GRIPPER_STATE_OPEN
            self.state.width_m = width_m
            self.state.force_n = force_n
        elif command == COMMAND_CLOSE:
            self.state.state = GRIPPER_STATE_CLOSED
            self.state.width_m = width_m
            self.state.force_n = force_n
        elif command == COMMAND_VACUUM_ON:
            self.state.vacuum_enabled = True
        elif command == COMMAND_VACUUM_OFF:
            self.state.vacuum_enabled = False
        else:
            raise ValueError(f"unsupported command: {command}")

        return self.state

    def attach_object(self, object_id: str) -> PlanningScene:
        if object_id not in self.object_specs:
            raise ValueError(f"unknown object_id: {object_id}")
        if self.state.attached_object_id:
            raise ValueError(f"object already attached: {self.state.attached_object_id}")

        spec = self.object_specs[object_id]
        scene = PlanningScene()
        scene.is_diff = True
        scene.robot_state.is_diff = True

        scene.world.collision_objects.append(
            _collision_object_remove(spec.object_id, self.world_frame)
        )

        attached = AttachedCollisionObject()
        attached.link_name = self.attach_link
        attached.touch_links = list(self.touch_links)
        attached.object = _collision_object_add(
            spec,
            self.attach_link,
            _identity_pose(0.0, 0.0, 0.0),
        )
        scene.robot_state.attached_collision_objects.append(attached)

        self.state.attached_object_id = object_id
        self.state.state = GRIPPER_STATE_HOLDING
        return scene

    def detach_object(self) -> PlanningScene:
        if not self.state.attached_object_id:
            raise ValueError("no object attached")

        object_id = self.state.attached_object_id
        spec = self.object_specs[object_id]

        scene = PlanningScene()
        scene.is_diff = True
        scene.robot_state.is_diff = True

        attached_remove = AttachedCollisionObject()
        attached_remove.link_name = self.attach_link
        attached_remove.object.id = object_id
        attached_remove.object.operation = CollisionObject.REMOVE
        scene.robot_state.attached_collision_objects.append(attached_remove)

        scene.world.collision_objects.append(
            _collision_object_add(
                spec,
                self.world_frame,
                _identity_pose(*spec.world_xyz),
            )
        )

        self.state.attached_object_id = ""
        if self.state.state == GRIPPER_STATE_HOLDING:
            self.state.state = GRIPPER_STATE_OPEN
        return scene

    @staticmethod
    def _validate_width(width_m: float) -> None:
        if width_m < 0.0 or width_m > MAX_WIDTH_M:
            raise ValueError(f"width_m must be between 0.0 and {MAX_WIDTH_M}")

    @staticmethod
    def _validate_force(force_n: float) -> None:
        if force_n < 0.0:
            raise ValueError("force_n must be non-negative")
```

- [ ] **Step 5: Run backend tests**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
pytest src/crx10ial_gripper/test/test_fake_gripper.py -q
```

Expected: all backend tests pass.

- [ ] **Step 6: Build gripper package**

Run:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select crx10ial_interfaces crx10ial_gripper
```

Expected: both packages build.

- [ ] **Step 7: Commit backend**

Run:

```bash
git add src/crx10ial_gripper
git commit -m "feat: add fake gripper backend"
```

## Task 4: Add Fake Gripper ROS Node Services

**Files:**
- Create: `src/crx10ial_gripper/crx10ial_gripper/fake_gripper_node.py`
- Create: `src/crx10ial_gripper/test/test_fake_gripper_node.py`
- Modify: `src/crx10ial_gripper/README.md`

- [ ] **Step 1: Write failing node tests**

Create `src/crx10ial_gripper/test/test_fake_gripper_node.py`:

```python
import rclpy

from crx10ial_gripper.fake_gripper import (
    COMMAND_CLOSE,
    GRIPPER_STATE_CLOSED,
    GRIPPER_STATE_HOLDING,
)
from crx10ial_gripper.fake_gripper_node import FakeGripperNode
from crx10ial_interfaces.srv import AttachObject, CommandGripper, DetachObject, GetGripperState


def _init_rclpy():
    if not rclpy.ok():
        rclpy.init()


def test_command_callback_maps_request_to_backend_state():
    _init_rclpy()
    node = FakeGripperNode(start_apply_scene_client=False)
    try:
        request = CommandGripper.Request()
        request.command = COMMAND_CLOSE
        request.width_m = 0.02
        request.force_n = 30.0
        response = node.handle_command(request, CommandGripper.Response())

        assert response.success is True
        assert response.state == GRIPPER_STATE_CLOSED
        assert response.width_m == 0.02
        assert response.force_n == 30.0
        assert response.attached_object_id == ""
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_attach_and_detach_callbacks_apply_scene_and_update_state():
    _init_rclpy()
    node = FakeGripperNode(start_apply_scene_client=False)
    applied_scenes = []
    node.apply_scene = applied_scenes.append
    try:
        attach_request = AttachObject.Request()
        attach_request.object_id = "work_object"
        attach_response = node.handle_attach_object(
            attach_request,
            AttachObject.Response(),
        )

        assert attach_response.success is True
        assert attach_response.attached_object_id == "work_object"
        assert node.backend.state.state == GRIPPER_STATE_HOLDING
        assert len(applied_scenes) == 1

        state_response = node.handle_get_state(
            GetGripperState.Request(),
            GetGripperState.Response(),
        )
        assert state_response.attached_object_id == "work_object"

        detach_response = node.handle_detach_object(
            DetachObject.Request(),
            DetachObject.Response(),
        )
        assert detach_response.success is True
        assert detach_response.detached_object_id == "work_object"
        assert node.backend.state.attached_object_id == ""
        assert len(applied_scenes) == 2
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_attach_callback_returns_failure_for_unknown_object():
    _init_rclpy()
    node = FakeGripperNode(start_apply_scene_client=False)
    try:
        request = AttachObject.Request()
        request.object_id = "missing"
        response = node.handle_attach_object(request, AttachObject.Response())

        assert response.success is False
        assert "unknown object_id" in response.message
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

- [ ] **Step 2: Run node tests and verify they fail**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
pytest src/crx10ial_gripper/test/test_fake_gripper_node.py -q
```

Expected: tests fail because `fake_gripper_node.py` does not exist yet.

- [ ] **Step 3: Implement fake gripper node**

Create `src/crx10ial_gripper/crx10ial_gripper/fake_gripper_node.py`:

```python
import threading

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from moveit_msgs.srv import ApplyPlanningScene
from rclpy.node import Node

from crx10ial_gripper.fake_gripper import FakeGripperBackend
from crx10ial_interfaces.srv import (
    AttachObject,
    CommandGripper,
    DetachObject,
    GetGripperState,
)


class FakeGripperNode(Node):
    def __init__(self, start_apply_scene_client: bool = True) -> None:
        super().__init__("fake_gripper")

        self.declare_parameter("attach_link", "grasp_link")
        self.declare_parameter("world_frame", "world")

        self.backend = FakeGripperBackend(
            attach_link=str(self.get_parameter("attach_link").value),
            world_frame=str(self.get_parameter("world_frame").value),
        )
        self._callback_group = ReentrantCallbackGroup()

        self._apply_scene_client = None
        if start_apply_scene_client:
            self._apply_scene_client = self.create_client(
                ApplyPlanningScene,
                "/apply_planning_scene",
                callback_group=self._callback_group,
            )

        self.create_service(
            CommandGripper,
            "command",
            self.handle_command,
            callback_group=self._callback_group,
        )
        self.create_service(
            AttachObject,
            "attach_object",
            self.handle_attach_object,
            callback_group=self._callback_group,
        )
        self.create_service(
            DetachObject,
            "detach_object",
            self.handle_detach_object,
            callback_group=self._callback_group,
        )
        self.create_service(
            GetGripperState,
            "get_state",
            self.handle_get_state,
            callback_group=self._callback_group,
        )

    def handle_command(
        self,
        request: CommandGripper.Request,
        response: CommandGripper.Response,
    ) -> CommandGripper.Response:
        try:
            state = self.backend.command(request.command, request.width_m, request.force_n)
        except ValueError as exc:
            response.success = False
            response.message = str(exc)
            self._copy_state(response)
            return response

        response.success = True
        response.message = "ok"
        self._copy_state(response, state)
        return response

    def handle_attach_object(
        self,
        request: AttachObject.Request,
        response: AttachObject.Response,
    ) -> AttachObject.Response:
        try:
            scene = self.backend.attach_object(request.object_id)
            self.apply_scene(scene)
        except (RuntimeError, ValueError) as exc:
            response.success = False
            response.message = str(exc)
            response.attached_object_id = self.backend.state.attached_object_id
            return response

        response.success = True
        response.message = "ok"
        response.attached_object_id = self.backend.state.attached_object_id
        return response

    def handle_detach_object(
        self,
        request: DetachObject.Request,
        response: DetachObject.Response,
    ) -> DetachObject.Response:
        del request
        detached_object_id = self.backend.state.attached_object_id
        try:
            scene = self.backend.detach_object()
            self.apply_scene(scene)
        except (RuntimeError, ValueError) as exc:
            response.success = False
            response.message = str(exc)
            response.detached_object_id = ""
            return response

        response.success = True
        response.message = "ok"
        response.detached_object_id = detached_object_id
        return response

    def handle_get_state(
        self,
        request: GetGripperState.Request,
        response: GetGripperState.Response,
    ) -> GetGripperState.Response:
        del request
        state = self.backend.state
        response.state = state.state
        response.width_m = state.width_m
        response.force_n = state.force_n
        response.attached_object_id = state.attached_object_id
        response.vacuum_enabled = state.vacuum_enabled
        return response

    def apply_scene(self, scene) -> None:
        if self._apply_scene_client is None:
            return

        if not self._apply_scene_client.wait_for_service(timeout_sec=5.0):
            raise RuntimeError("/apply_planning_scene service is not available")

        request = ApplyPlanningScene.Request()
        request.scene = scene
        future = self._apply_scene_client.call_async(request)
        finished = threading.Event()
        future.add_done_callback(lambda _: finished.set())

        if not finished.wait(timeout=10.0):
            raise RuntimeError("/apply_planning_scene call timed out")

        result = future.result()
        if result is None or not result.success:
            raise RuntimeError("/apply_planning_scene returned failure")

    def _copy_state(self, response, state=None) -> None:
        current = state if state is not None else self.backend.state
        response.state = current.state
        response.width_m = current.width_m
        response.force_n = current.force_n
        response.attached_object_id = current.attached_object_id
        response.vacuum_enabled = current.vacuum_enabled


def main() -> None:
    rclpy.init()
    node = FakeGripperNode()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Update gripper README**

Replace `src/crx10ial_gripper/README.md` with:

```markdown
# crx10ial_gripper

Gripper control abstraction for the CRX-10iA/L mock workcell.

## Fake backend

The `fake_gripper` executable provides services under its namespace:

- `command`
- `attach_object`
- `detach_object`
- `get_state`

The backend updates MoveIt through `/apply_planning_scene` for attach/detach. Static world collision objects remain owned by `crx10ial_bringup.mock_scene`.
```

- [ ] **Step 5: Run gripper package tests**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
pytest src/crx10ial_gripper/test -q
```

Expected: all gripper tests pass.

- [ ] **Step 6: Build gripper and interface packages**

Run:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select crx10ial_interfaces crx10ial_gripper
```

Expected: both packages build.

- [ ] **Step 7: Commit fake gripper node**

Run:

```bash
git add src/crx10ial_gripper
git commit -m "feat: expose fake gripper services"
```

## Task 5: Use Local Workcell Robot Description in Mock Bringup

**Files:**
- Modify: `src/crx10ial_bringup/launch/mock.launch.py`
- Modify: `src/crx10ial_bringup/package.xml`
- Modify: `src/crx10ial_bringup/setup.py`
- Modify: `src/crx10ial_bringup/test/test_mock_scene.py`

- [ ] **Step 1: Add failing launch structure tests**

Append these tests to `src/crx10ial_bringup/test/test_mock_scene.py`:

```python
import ast
from pathlib import Path


def _mock_launch_source_tree() -> ast.AST:
    launch_path = Path(__file__).parents[1] / "launch" / "mock.launch.py"
    return ast.parse(launch_path.read_text(encoding="utf-8"))


def test_mock_launch_uses_local_cell_description_xacro():
    tree = _mock_launch_source_tree()
    constants = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }

    assert "crx10ial_cell_description" in constants
    assert "crx10ial_cell.urdf.xacro" in constants


def test_mock_launch_starts_robot_state_publisher_and_fake_gripper():
    tree = _mock_launch_source_tree()
    node_packages = []
    node_executables = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or getattr(node.func, "id", None) != "Node":
            continue
        for keyword in node.keywords:
            if keyword.arg == "package" and isinstance(keyword.value, ast.Constant):
                node_packages.append(keyword.value.value)
            if keyword.arg == "executable" and isinstance(keyword.value, ast.Constant):
                node_executables.append(keyword.value.value)

    assert "robot_state_publisher" in node_packages
    assert "crx10ial_gripper" in node_packages
    assert "fake_gripper" in node_executables
```

- [ ] **Step 2: Run launch tests and verify they fail**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
pytest src/crx10ial_bringup/test/test_mock_scene.py -q
```

Expected: new tests fail because mock launch still uses FANUC upstream xacro and does not start `fake_gripper`.

- [ ] **Step 3: Add bringup dependencies**

Add these dependencies to `src/crx10ial_bringup/package.xml`:

```xml
  <exec_depend>crx10ial_cell_description</exec_depend>
  <exec_depend>crx10ial_gripper</exec_depend>
```

- [ ] **Step 4: Replace mock launch**

Replace `src/crx10ial_bringup/launch/mock.launch.py` with:

```python
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder


def _robot_description_command(cell_xacro_path, description_arguments):
    return Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            cell_xacro_path,
            " ",
            "robot_ip:=",
            description_arguments["robot_ip"],
            " ",
            "use_mock:=",
            description_arguments["use_mock"],
            " ",
            "gpio_configuration:=",
            description_arguments["gpio_configuration"],
            " ",
        ]
    )


def _controller_spawner(controller_name):
    return ExecuteProcess(
        cmd=[
            "ros2 run controller_manager spawner "
            f"--controller-manager-timeout 180 {controller_name}"
        ],
        shell=True,
        output="screen",
    )


def launch_setup(context, *args, **kwargs):
    del args, kwargs

    robot_model = LaunchConfiguration("robot_model")
    robot_ip = LaunchConfiguration("robot_ip")
    launch_rviz = LaunchConfiguration("launch_rviz")
    publish_scene = LaunchConfiguration("publish_scene")
    launch_gripper = LaunchConfiguration("launch_gripper")
    ros2_control_config = LaunchConfiguration("ros2_control_config")
    gpio_configuration = LaunchConfiguration("gpio_configuration")

    robot_model_value = robot_model.perform(context)
    description_arguments = {
        "robot_ip": robot_ip.perform(context),
        "use_mock": "true",
        "gpio_configuration": gpio_configuration.perform(context),
    }

    cell_xacro_path = os.path.join(
        get_package_share_directory("crx10ial_cell_description"),
        "urdf",
        "crx10ial_cell.urdf.xacro",
    )

    robot_description_content = _robot_description_command(
        cell_xacro_path,
        description_arguments,
    )
    robot_description = {
        "robot_description": ParameterValue(
            value=robot_description_content,
            value_type=str,
        )
    }

    moveit_config = (
        MoveItConfigsBuilder(robot_model_value, package_name="fanuc_moveit_config")
        .robot_description(file_path=cell_xacro_path, mappings=description_arguments)
        .robot_description_semantic(file_path=f"srdf/{robot_model_value}.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_scene_monitor(
            publish_robot_description=True,
            publish_robot_description_semantic=True,
        )
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )

    # The cell xacro already expands FANUC's ros2_control macro. Start the same
    # mock control nodes as FANUC upstream here so MoveIt and ros2_control share
    # this single robot_description instead of expanding two independent URDFs.
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, ros2_control_config],
        output="both",
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    slider = Node(
        package="slider_publisher",
        executable="slider_gui_node",
        name="slider_gui_node",
        output="both",
    )

    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="both",
        parameters=[moveit_config.to_dict()],
    )

    rviz_config = PathJoinSubstitution(
        [FindPackageShare("fanuc_moveit_config"), "rviz", "view_robot.rviz"]
    )
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="both",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.planning_pipelines,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
        ],
        arguments=["--display-config", rviz_config],
        condition=IfCondition(launch_rviz),
    )

    scene_publisher = Node(
        package="crx10ial_bringup",
        executable="publish_mock_scene",
        name="mock_scene_publisher",
        output="both",
        parameters=[{"frame_id": "world", "publish_period_sec": 2.0}],
        condition=IfCondition(publish_scene),
    )

    fake_gripper = Node(
        package="crx10ial_gripper",
        executable="fake_gripper",
        namespace="crx10ial_gripper",
        name="fake_gripper",
        output="both",
        parameters=[{"attach_link": "grasp_link", "world_frame": "world"}],
        condition=IfCondition(launch_gripper),
    )

    return [
        control_node,
        robot_state_publisher,
        slider,
        _controller_spawner("joint_state_broadcaster"),
        _controller_spawner("joint_trajectory_controller"),
        _controller_spawner("fanuc_gpio_controller"),
        _controller_spawner("fanuc_force_sensor_broadcaster"),
        _controller_spawner("force_torque_sensor_broadcaster"),
        move_group,
        rviz,
        scene_publisher,
        fake_gripper,
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "robot_model",
                default_value="crx10ia_l",
                choices=["crx10ia_l"],
                description="FANUC CRX model to launch.",
            ),
            DeclareLaunchArgument(
                "robot_ip",
                default_value="1.1.1.1",
                description="Unused mock IP passed through the FANUC xacro mappings.",
            ),
            DeclareLaunchArgument(
                "launch_rviz",
                default_value="true",
                choices=["true", "false"],
                description="Start RViz.",
            ),
            DeclareLaunchArgument(
                "publish_scene",
                default_value="true",
                choices=["true", "false"],
                description="Publish static planning-scene collision objects.",
            ),
            DeclareLaunchArgument(
                "launch_gripper",
                default_value="true",
                choices=["true", "false"],
                description="Start the fake gripper service node.",
            ),
            DeclareLaunchArgument(
                "ros2_control_config",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("fanuc_hardware_interface"),
                        "config",
                        "ros2_controllers.yaml",
                    ]
                ),
                description="Controller configuration used by FANUC mock control.",
            ),
            DeclareLaunchArgument(
                "gpio_configuration",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("fanuc_hardware_interface"),
                        "config",
                        "example_gpio_config.yaml",
                    ]
                ),
                description="GPIO configuration passed through to FANUC xacro and mock control.",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
```

- [ ] **Step 5: Run bringup tests**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
pytest src/crx10ial_bringup/test/test_mock_scene.py -q
```

Expected: all bringup tests pass.

- [ ] **Step 6: Build changed packages**

Run:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select \
  crx10ial_cell_description \
  crx10ial_interfaces \
  crx10ial_gripper \
  crx10ial_bringup
```

Expected: selected packages build.

- [ ] **Step 7: Commit mock bringup integration**

Run:

```bash
git add src/crx10ial_bringup
git commit -m "feat: launch local gripper-aware mock cell"
```

## Task 6: Add M2 Runtime Verification Checks

**Files:**
- No new long-lived scripts are required.

- [ ] **Step 1: Run full package tests**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon test --packages-select \
  crx10ial_cell_description \
  crx10ial_interfaces \
  crx10ial_gripper \
  crx10ial_bringup
colcon test-result --verbose
```

Expected: no failures.

- [ ] **Step 2: Run mock launch smoke with gripper enabled**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
set +e
timeout 45s ros2 launch crx10ial_bringup mock.launch.py \
  launch_rviz:=false \
  publish_scene:=true \
  launch_gripper:=true \
  2>&1 | tee /tmp/crx10ial_m2_mock_launch.log
status=${PIPESTATUS[0]}
set -e
printf 'timeout_status=%s\n' "${status}"
test "${status}" -eq 124
! grep -E "Traceback|Exception|ModuleNotFoundError|PackageNotFoundError" /tmp/crx10ial_m2_mock_launch.log
grep -E "move_group|fake_gripper|mock_scene_publisher|joint_state_broadcaster|joint_trajectory_controller" /tmp/crx10ial_m2_mock_launch.log
```

Expected: timeout status is `124`, no error pattern appears, and logs show `move_group`, `fake_gripper`, `mock_scene_publisher`, `joint_state_broadcaster`, and `joint_trajectory_controller`.

- [ ] **Step 3: Verify static-scene planning succeeds and trajectory states are valid**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
set -euo pipefail

rm -f /tmp/crx10ial_m2_scene_plan_launch.log /tmp/crx10ial_m2_scene_plan_check.log

ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=false publish_scene:=true launch_gripper:=true \
  > /tmp/crx10ial_m2_scene_plan_launch.log 2>&1 &
LAUNCH_PID=$!

cleanup() {
  if kill -0 "${LAUNCH_PID}" >/dev/null 2>&1; then
    kill "${LAUNCH_PID}" >/dev/null 2>&1 || true
    wait "${LAUNCH_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

for _ in $(seq 1 60); do
  if ros2 service list | grep -qx "/plan_kinematic_path" && \
     ros2 service list | grep -qx "/check_state_validity"; then
    break
  fi
  sleep 1
done

ros2 service list | grep -qx "/plan_kinematic_path"
ros2 service list | grep -qx "/check_state_validity"
sleep 10

python3 - <<'PY' | tee /tmp/crx10ial_m2_scene_plan_check.log
import sys

import rclpy
from moveit_msgs.msg import Constraints, JointConstraint, MoveItErrorCodes
from moveit_msgs.srv import GetMotionPlan, GetStateValidity
from sensor_msgs.msg import JointState


SAFE_JOINT_TARGET = {
    "J1": -0.80,
    "J2": -0.45,
    "J3": 0.95,
    "J4": 0.0,
    "J5": -1.10,
    "J6": 0.0,
}


def build_plan_request() -> GetMotionPlan.Request:
    request = GetMotionPlan.Request()
    motion_request = request.motion_plan_request
    motion_request.group_name = "manipulator"
    motion_request.num_planning_attempts = 10
    motion_request.allowed_planning_time = 10.0
    motion_request.max_velocity_scaling_factor = 0.1
    motion_request.max_acceleration_scaling_factor = 0.1
    motion_request.start_state.is_diff = True

    goal = Constraints()
    goal.name = "m2_static_scene_safe_joint_target"
    for joint_name, joint_value in SAFE_JOINT_TARGET.items():
        constraint = JointConstraint()
        constraint.joint_name = joint_name
        constraint.position = joint_value
        constraint.tolerance_above = 0.02
        constraint.tolerance_below = 0.02
        constraint.weight = 1.0
        goal.joint_constraints.append(constraint)
    motion_request.goal_constraints.append(goal)
    return request


def state_validity_request(joint_names, point) -> GetStateValidity.Request:
    request = GetStateValidity.Request()
    request.group_name = "manipulator"
    request.robot_state.joint_state = JointState()
    request.robot_state.joint_state.name = list(joint_names)
    request.robot_state.joint_state.position = list(point.positions)
    request.robot_state.is_diff = True
    return request


def target_validity_request() -> GetStateValidity.Request:
    request = GetStateValidity.Request()
    request.group_name = "manipulator"
    request.robot_state.joint_state = JointState()
    request.robot_state.joint_state.name = list(SAFE_JOINT_TARGET.keys())
    request.robot_state.joint_state.position = list(SAFE_JOINT_TARGET.values())
    request.robot_state.is_diff = True
    return request


def main() -> int:
    rclpy.init()
    node = rclpy.create_node("check_m2_static_scene_plan")
    try:
        plan_client = node.create_client(GetMotionPlan, "/plan_kinematic_path")
        validity_client = node.create_client(GetStateValidity, "/check_state_validity")
        if not plan_client.wait_for_service(timeout_sec=30.0):
            print("ERROR: /plan_kinematic_path unavailable", file=sys.stderr)
            return 1
        if not validity_client.wait_for_service(timeout_sec=30.0):
            print("ERROR: /check_state_validity unavailable", file=sys.stderr)
            return 1

        target_future = validity_client.call_async(target_validity_request())
        rclpy.spin_until_future_complete(node, target_future, timeout_sec=15.0)
        target_validity = target_future.result()
        if target_validity is None or not target_validity.valid:
            print("ERROR: SAFE_JOINT_TARGET is invalid in the static scene", file=sys.stderr)
            return 1

        future = plan_client.call_async(build_plan_request())
        rclpy.spin_until_future_complete(node, future, timeout_sec=45.0)
        response = future.result()
        if response is None:
            print("ERROR: planning returned no response", file=sys.stderr)
            return 1
        if response.motion_plan_response.error_code.val != MoveItErrorCodes.SUCCESS:
            print(
                f"ERROR: planning failed with code {response.motion_plan_response.error_code.val}",
                file=sys.stderr,
            )
            return 1

        trajectory = response.motion_plan_response.trajectory.joint_trajectory
        if not trajectory.points:
            print("ERROR: planning response has no trajectory points", file=sys.stderr)
            return 1

        for index, point in enumerate(trajectory.points):
            validity_future = validity_client.call_async(
                state_validity_request(trajectory.joint_names, point)
            )
            rclpy.spin_until_future_complete(node, validity_future, timeout_sec=15.0)
            validity = validity_future.result()
            if validity is None or not validity.valid:
                print(f"ERROR: trajectory point {index} is invalid", file=sys.stderr)
                return 1

        print("M2 static-scene planning succeeded")
        print(f"Validated trajectory points: {len(trajectory.points)}")
        return 0
    finally:
        node.destroy_node()
        rclpy.shutdown()


raise SystemExit(main())
PY

grep -q "M2 static-scene planning succeeded" /tmp/crx10ial_m2_scene_plan_check.log
! grep -E "Traceback|Exception|ModuleNotFoundError|PackageNotFoundError" /tmp/crx10ial_m2_scene_plan_launch.log

cleanup
trap - EXIT
```

Expected: Python prints `M2 static-scene planning succeeded` and a nonzero validated trajectory point count.

- [ ] **Step 4: Verify gripper open, close, attach, state, and detach services**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
set -euo pipefail

rm -f /tmp/crx10ial_m2_gripper_launch.log

ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=false publish_scene:=true launch_gripper:=true \
  > /tmp/crx10ial_m2_gripper_launch.log 2>&1 &
LAUNCH_PID=$!

cleanup() {
  if kill -0 "${LAUNCH_PID}" >/dev/null 2>&1; then
    kill "${LAUNCH_PID}" >/dev/null 2>&1 || true
    wait "${LAUNCH_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

for _ in $(seq 1 60); do
  if ros2 service list | grep -qx "/crx10ial_gripper/command" && \
     ros2 service list | grep -qx "/crx10ial_gripper/attach_object" && \
     ros2 service list | grep -qx "/crx10ial_gripper/detach_object" && \
     ros2 service list | grep -qx "/crx10ial_gripper/get_state"; then
    break
  fi
  sleep 1
done

ros2 service list | grep -qx "/crx10ial_gripper/command"
ros2 service list | grep -qx "/crx10ial_gripper/attach_object"
ros2 service list | grep -qx "/crx10ial_gripper/detach_object"
ros2 service list | grep -qx "/crx10ial_gripper/get_state"

ros2 service call /crx10ial_gripper/command crx10ial_interfaces/srv/CommandGripper \
  "{command: 1, width_m: 0.08, force_n: 0.0}" | tee /tmp/crx10ial_m2_open.log
grep -q "success=True" /tmp/crx10ial_m2_open.log

ros2 service call /crx10ial_gripper/command crx10ial_interfaces/srv/CommandGripper \
  "{command: 2, width_m: 0.02, force_n: 30.0}" | tee /tmp/crx10ial_m2_close.log
grep -q "success=True" /tmp/crx10ial_m2_close.log

ros2 service call /crx10ial_gripper/attach_object crx10ial_interfaces/srv/AttachObject \
  "{object_id: work_object}" | tee /tmp/crx10ial_m2_attach.log
grep -q "success=True" /tmp/crx10ial_m2_attach.log
grep -q "attached_object_id='work_object'" /tmp/crx10ial_m2_attach.log

ros2 service call /crx10ial_gripper/get_state crx10ial_interfaces/srv/GetGripperState \
  "{}" | tee /tmp/crx10ial_m2_state.log
grep -q "attached_object_id='work_object'" /tmp/crx10ial_m2_state.log

ros2 service call /crx10ial_gripper/detach_object crx10ial_interfaces/srv/DetachObject \
  "{}" | tee /tmp/crx10ial_m2_detach.log
grep -q "success=True" /tmp/crx10ial_m2_detach.log
grep -q "detached_object_id='work_object'" /tmp/crx10ial_m2_detach.log

! grep -E "Traceback|Exception|ModuleNotFoundError|PackageNotFoundError" /tmp/crx10ial_m2_gripper_launch.log

cleanup
trap - EXIT
```

Expected: each service call returns `success=True`; attach reports `work_object`; get_state reports `work_object`; detach reports `work_object`.

- [ ] **Step 5: Commit runtime verification support if any files changed**

Run:

```bash
git status --short
```

Expected: no modified files from runtime checks. If this prints modified files, stop and inspect the runtime failure that forced the source correction. Return to the task that introduced the changed file, update that task's test or implementation step, and commit there with that task's commit message.

## Task 7: Final M2 Verification and Push

**Files:**
- No repository files are modified unless a verification fix is required.

- [ ] **Step 1: Run full build**

Run:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

Expected: all packages build.

- [ ] **Step 2: Run full relevant tests**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon test --packages-select \
  crx10ial_cell_description \
  crx10ial_interfaces \
  crx10ial_gripper \
  crx10ial_bringup
colcon test-result --verbose
```

Expected: no failures.

- [ ] **Step 3: Run launch and M2 runtime smoke checks**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
set +e
timeout 45s ros2 launch crx10ial_bringup mock.launch.py \
  launch_rviz:=false \
  publish_scene:=true \
  launch_gripper:=true \
  2>&1 | tee /tmp/crx10ial_m2_final_mock_launch.log
status=${PIPESTATUS[0]}
set -e
printf 'timeout_status=%s\n' "${status}"
test "${status}" -eq 124
! grep -E "Traceback|Exception|ModuleNotFoundError|PackageNotFoundError" /tmp/crx10ial_m2_final_mock_launch.log
grep -E "move_group|fake_gripper|mock_scene_publisher|joint_state_broadcaster|joint_trajectory_controller" /tmp/crx10ial_m2_final_mock_launch.log
```

Then rerun the full static-scene planning script from Task 6 Step 3 and the full gripper service script from Task 6 Step 4 without changing their commands.

Expected:

- mock launch reaches MoveIt readiness with fake gripper enabled.
- static-scene planning succeeds and all returned trajectory points are valid.
- open/close/attach/get_state/detach services all return success.

- [ ] **Step 4: Review repository diff**

Run:

```bash
git status --short --branch
git log --oneline origin/m0-m1-humble-workspace..HEAD
git diff --stat origin/m0-m1-humble-workspace..HEAD
```

Expected: branch is `m2-workcell-gripper`; commits are only M2 commits; diff includes interface services, gripper model, fake backend, mock launch integration, docs, and tests.

- [ ] **Step 5: Push M2 branch**

Run:

```bash
git push -u origin m2-workcell-gripper
```

Expected: branch is pushed to `origin/m2-workcell-gripper`.

## Self-Review Checklist

- [x] M2 deliverable "Base/table/work objects/camera/gripper modeled" is covered by Task 2.
- [x] M2 deliverable "End-effector frames and grasp frames documented" is covered by Task 2 and `docs/gripper_frames.md`.
- [x] M2 deliverable "Gripper interface and fake backend implemented" is covered by Task 1, Task 3, and Task 4.
- [x] M2 acceptance "Planning avoids static collision geometry" is covered by Task 6 Step 3.
- [x] M2 acceptance "Gripper fake backend supports open/close and attach/detach in mock mode" is covered by Task 4 tests and Task 6 Step 4.
- [x] Gazebo, MTC pick/place, physical hardware, ROBOGUIDE, and iRVision remain outside this plan.
- [x] `mock_scene_publisher` and `fake_gripper` responsibilities are separate.
- [x] No placeholder strings remain in the plan.
