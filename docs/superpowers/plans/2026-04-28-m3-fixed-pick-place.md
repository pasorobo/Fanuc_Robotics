# M3 Fixed Pick-and-Place Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fixed-pose pick-and-place task for the CRX-10iA/L mock workcell using MoveIt Task Constructor for planning diagnostics and the M2 fake gripper as the sole runtime attached-object owner.

**Architecture:** MTC builds and solves the fixed pick/place task with internal planning-scene attach/detach stages, but M3 never calls `moveit::task_constructor::Task::execute()`. Runtime scene writes continue to flow only through `crx10ial_gripper` services; mock execution moves the arm through the same configured waypoints with `MoveGroupInterface`, then calls fake gripper attach/detach and verifies there is exactly one attached `work_object`.

**Tech Stack:** Ubuntu 22.04, ROS 2 Humble, MoveIt 2, MoveIt Task Constructor apt binaries, C++17, ament_cmake, gtest, ROS parameter YAML, existing `crx10ial_bringup` mock launch.

---

## Scope

This plan implements only the approved M3 milestone:

- MoveIt Task Constructor fixed-pose pick/place pipeline.
- Configurable object pose, grasp pose, place pose, approach vector, retreat vector, and gripper settings.
- Actionable failure diagnostics for MTC planning failures.
- Mock-mode pick/place smoke that uses `fake_gripper` for runtime attach/detach.

This plan does not add Gazebo, iRVision, ROBOGUIDE, physical hardware, vendor gripper IO, or vision-driven object pose updates.

## Critical C1 Contract

M2 defined `crx10ial_gripper.fake_gripper` as the owner of attached-object transitions in the runtime MoveIt planning scene. M3 preserves that contract.

- MTC `ModifyPlanningScene::attachObject()` and `detachObject()` are allowed only inside the MTC planning graph.
- M3 does not call `Task::execute()` because that would send an `ExecuteTaskSolution` action that can apply MTC scene diffs externally.
- Runtime attach/detach uses `/crx10ial_gripper/attach_object` and `/crx10ial_gripper/detach_object`.
- Runtime smoke checks `/get_planning_scene` after attach and asserts exactly one attached `work_object` and no duplicate world `work_object`.

## File Structure

- `src/crx10ial_tasks/config/fixed_pick_place.yaml`: ROS parameter YAML for fixed object/grasp/place and gripper settings.
- `src/crx10ial_tasks/include/crx10ial_tasks/fixed_pick_place_config.hpp`: typed config structs and parameter loader declaration.
- `src/crx10ial_tasks/src/fixed_pick_place_config.cpp`: parameter loading, vector validation, pose helpers.
- `src/crx10ial_tasks/include/crx10ial_tasks/fixed_pick_place_task.hpp`: MTC task builder and diagnostics interface.
- `src/crx10ial_tasks/src/fixed_pick_place_task.cpp`: MTC internal-scene planning pipeline and failure reporting.
- `src/crx10ial_tasks/src/fixed_pick_place_node.cpp`: node entry point for `plan`, `negative_plan`, and `execute_mock`.
- `src/crx10ial_tasks/launch/fixed_pick_place.launch.py`: launch only the task node with FANUC MoveIt parameters and the task YAML.
- `src/crx10ial_tasks/test/test_fixed_pick_place_config.cpp`: gtest for config loading and pose math.
- `src/crx10ial_tasks/test/test_task_source_contract.py`: pytest source-contract checks for C1.
- `src/crx10ial_tasks/test/test_fixed_pick_place_yaml.py`: pytest YAML schema checks.
- `src/crx10ial_tasks/README.md`: M3 usage notes and apt binary record.
- `src/crx10ial_tasks/CMakeLists.txt`, `src/crx10ial_tasks/package.xml`: C++ build, dependencies, tests, install rules.

## Task 0: Branch Baseline and MTC Apt Dependency Verification

**Files:**
- Modify: `src/crx10ial_tasks/README.md`

- [ ] **Step 1: Confirm branch and baseline**

Run:

```bash
git status --short --branch
git branch --show-current
git rev-parse HEAD
```

Expected:

```text
## m3-fixed-pick-place
m3-fixed-pick-place
f84c6465b7f184f49c4d0e97a9bf68dcdc07b0a6
```

If `git branch --show-current` is not `m3-fixed-pick-place`, run:

```bash
git switch m2-workcell-gripper
git pull --ff-only
git switch -c m3-fixed-pick-place
```

- [ ] **Step 2: Verify MTC apt binaries exist**

Run:

```bash
apt-cache policy \
  ros-humble-moveit-task-constructor-core \
  ros-humble-moveit-task-constructor-msgs \
  ros-humble-moveit-task-constructor-capabilities \
  ros-humble-moveit-task-constructor-visualization
```

Expected: each package has a non-empty `Candidate:` line. On the reviewed Ubuntu 22.04 host the candidates were `0.1.3-1jammy...`.

- [ ] **Step 3: Install MTC apt packages when missing**

Run:

```bash
set -euo pipefail
missing=()
for pkg in \
  ros-humble-moveit-task-constructor-core \
  ros-humble-moveit-task-constructor-msgs \
  ros-humble-moveit-task-constructor-capabilities \
  ros-humble-moveit-task-constructor-visualization
do
  dpkg-query -W -f='${Status}' "${pkg}" 2>/dev/null | grep -q "install ok installed" || missing+=("${pkg}")
done

if [ "${#missing[@]}" -gt 0 ]; then
  sudo apt-get update
  sudo apt-get install -y "${missing[@]}"
fi
```

Expected: command exits 0. If sudo requires a password, ask the user to run the same command and continue after it completes.

- [ ] **Step 4: Record installed MTC versions**

Replace `src/crx10ial_tasks/README.md` with:

```markdown
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
```

- [ ] **Step 5: Build baseline**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --symlink-install --packages-select crx10ial_tasks
```

Expected: `crx10ial_tasks` builds.

- [ ] **Step 6: Commit dependency baseline**

Run:

```bash
git add src/crx10ial_tasks/README.md
git commit -m "docs: record MTC runtime contract"
```

## Task 1: Add Fixed Pick/Place YAML Schema and Tests

**Files:**
- Create: `src/crx10ial_tasks/config/fixed_pick_place.yaml`
- Create: `src/crx10ial_tasks/test/test_fixed_pick_place_yaml.py`
- Modify: `src/crx10ial_tasks/CMakeLists.txt`
- Modify: `src/crx10ial_tasks/package.xml`

- [ ] **Step 1: Write YAML schema test**

Create `src/crx10ial_tasks/test/test_fixed_pick_place_yaml.py`:

```python
from pathlib import Path

import yaml


def _config_path() -> Path:
    return Path(__file__).resolve().parents[1] / "config" / "fixed_pick_place.yaml"


def _params():
    data = yaml.safe_load(_config_path().read_text(encoding="utf-8"))
    return data["fixed_pick_place"]["ros__parameters"]


def test_fixed_pick_place_yaml_has_required_sections():
    params = _params()

    assert params["object.id"] == "work_object"
    assert params["object.frame_id"] == "world"
    assert params["grasp.frame_id"] == "grasp_link"
    assert params["place.frame_id"] == "world"
    assert params["gripper.open_width_m"] == 0.08
    assert params["gripper.close_width_m"] == 0.02
    assert params["gripper.close_force_n"] == 30.0


def test_pose_and_vector_lengths_are_fixed():
    params = _params()

    for key in [
        "object.pose.xyz",
        "object.pose.rpy",
        "grasp.pose.xyz",
        "grasp.pose.rpy",
        "grasp.approach.direction",
        "grasp.retreat.direction",
        "place.pose.xyz",
        "place.pose.rpy",
        "failure.place.pose.xyz",
        "failure.place.pose.rpy",
    ]:
        assert len(params[key]) == 3


def test_grasp_distances_are_positive_and_ordered():
    params = _params()

    assert 0.0 < params["grasp.approach.min"] <= params["grasp.approach.max"]
    assert 0.0 < params["grasp.retreat.min"] <= params["grasp.retreat.max"]
    assert params["failure.place.pose.xyz"][0] >= 2.0
```

- [ ] **Step 2: Run YAML test and verify it fails**

Run:

```bash
python3 -m pytest src/crx10ial_tasks/test/test_fixed_pick_place_yaml.py -q
```

Expected: fails because `fixed_pick_place.yaml` does not exist.

- [ ] **Step 3: Add fixed pick/place config**

Create `src/crx10ial_tasks/config/fixed_pick_place.yaml`:

```yaml
fixed_pick_place:
  ros__parameters:
    arm_group_name: manipulator
    eef_name: tool_link
    hand_frame: grasp_link
    world_frame: world
    object.id: work_object
    object.frame_id: world
    object.dimensions: [0.08, 0.08, 0.05]
    object.pose.xyz: [0.55, 0.0, 0.745]
    object.pose.rpy: [0.0, 0.0, 0.0]
    grasp.frame_id: grasp_link
    grasp.pose.xyz: [-0.10, 0.0, 0.255]
    grasp.pose.rpy: [0.0, 0.0, 0.0]
    grasp.approach.direction: [1.0, 0.0, 0.0]
    grasp.approach.min: 0.05
    grasp.approach.max: 0.10
    grasp.retreat.direction: [-1.0, 0.0, 0.0]
    grasp.retreat.min: 0.05
    grasp.retreat.max: 0.10
    place.frame_id: world
    place.pose.xyz: [0.45, 0.20, 1.00]
    place.pose.rpy: [0.0, 0.0, 0.0]
    failure.place.pose.xyz: [2.00, 0.00, 1.00]
    failure.place.pose.rpy: [0.0, 0.0, 0.0]
    gripper.open_width_m: 0.08
    gripper.close_width_m: 0.02
    gripper.close_force_n: 30.0
    planning.max_solutions: 1
    planning.timeout_sec: 10.0
    execution.enabled: false
```

- [ ] **Step 4: Add pytest integration to CMake**

Replace `src/crx10ial_tasks/CMakeLists.txt` with:

```cmake
cmake_minimum_required(VERSION 3.8)
project(crx10ial_tasks)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_pytest REQUIRED)

install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  ament_add_pytest_test(fixed_pick_place_yaml
    test/test_fixed_pick_place_yaml.py
  )
endif()

ament_package()
```

Add to `src/crx10ial_tasks/package.xml`:

```xml
  <test_depend>ament_cmake_pytest</test_depend>
  <test_depend>python3-yaml</test_depend>
```

- [ ] **Step 5: Run YAML tests**

Run:

```bash
python3 -m pytest src/crx10ial_tasks/test/test_fixed_pick_place_yaml.py -q
source /opt/ros/humble/setup.bash
colcon test --packages-select crx10ial_tasks
colcon test-result --verbose
```

Expected: pytest passes and `crx10ial_tasks` has no test failures.

- [ ] **Step 6: Commit config schema**

Run:

```bash
git add src/crx10ial_tasks
git commit -m "feat: add fixed pick place config"
```

## Task 2: Add C++ Config Loader and Unit Tests

**Files:**
- Create: `src/crx10ial_tasks/include/crx10ial_tasks/fixed_pick_place_config.hpp`
- Create: `src/crx10ial_tasks/src/fixed_pick_place_config.cpp`
- Create: `src/crx10ial_tasks/test/test_fixed_pick_place_config.cpp`
- Modify: `src/crx10ial_tasks/CMakeLists.txt`
- Modify: `src/crx10ial_tasks/package.xml`

- [ ] **Step 1: Write config loader gtest**

Create `src/crx10ial_tasks/test/test_fixed_pick_place_config.cpp`:

```cpp
#include <gtest/gtest.h>
#include <rclcpp/rclcpp.hpp>

#include <crx10ial_tasks/fixed_pick_place_config.hpp>

namespace {
rclcpp::NodeOptions options_with_overrides() {
  rclcpp::NodeOptions options;
  options.parameter_overrides({
      rclcpp::Parameter("arm_group_name", "manipulator"),
      rclcpp::Parameter("eef_name", "tool_link"),
      rclcpp::Parameter("hand_frame", "grasp_link"),
      rclcpp::Parameter("world_frame", "world"),
      rclcpp::Parameter("object.id", "work_object"),
      rclcpp::Parameter("object.frame_id", "world"),
      rclcpp::Parameter("object.dimensions", std::vector<double>{0.08, 0.08, 0.05}),
      rclcpp::Parameter("object.pose.xyz", std::vector<double>{0.55, 0.0, 0.745}),
      rclcpp::Parameter("object.pose.rpy", std::vector<double>{0.0, 0.0, 0.0}),
      rclcpp::Parameter("grasp.frame_id", "grasp_link"),
      rclcpp::Parameter("grasp.pose.xyz", std::vector<double>{-0.10, 0.0, 0.255}),
      rclcpp::Parameter("grasp.pose.rpy", std::vector<double>{0.0, 0.0, 0.0}),
      rclcpp::Parameter("grasp.approach.direction", std::vector<double>{1.0, 0.0, 0.0}),
      rclcpp::Parameter("grasp.approach.min", 0.05),
      rclcpp::Parameter("grasp.approach.max", 0.10),
      rclcpp::Parameter("grasp.retreat.direction", std::vector<double>{-1.0, 0.0, 0.0}),
      rclcpp::Parameter("grasp.retreat.min", 0.05),
      rclcpp::Parameter("grasp.retreat.max", 0.10),
      rclcpp::Parameter("place.frame_id", "world"),
      rclcpp::Parameter("place.pose.xyz", std::vector<double>{0.45, 0.20, 1.00}),
      rclcpp::Parameter("place.pose.rpy", std::vector<double>{0.0, 0.0, 0.0}),
      rclcpp::Parameter("failure.place.pose.xyz", std::vector<double>{2.0, 0.0, 1.00}),
      rclcpp::Parameter("failure.place.pose.rpy", std::vector<double>{0.0, 0.0, 0.0}),
      rclcpp::Parameter("gripper.open_width_m", 0.08),
      rclcpp::Parameter("gripper.close_width_m", 0.02),
      rclcpp::Parameter("gripper.close_force_n", 30.0),
      rclcpp::Parameter("planning.max_solutions", 1),
      rclcpp::Parameter("planning.timeout_sec", 10.0),
      rclcpp::Parameter("execution.enabled", false),
  });
  return options;
}
}  // namespace

TEST(FixedPickPlaceConfig, LoadsTypedParameters) {
  rclcpp::init(0, nullptr);
  auto node = std::make_shared<rclcpp::Node>("config_test", options_with_overrides());

  const auto config = crx10ial_tasks::load_fixed_pick_place_config(*node);

  EXPECT_EQ(config.arm_group_name, "manipulator");
  EXPECT_EQ(config.object.id, "work_object");
  EXPECT_EQ(config.hand_frame, "grasp_link");
  EXPECT_DOUBLE_EQ(config.place.pose.position.y, 0.20);
  EXPECT_DOUBLE_EQ(config.gripper.close_force_n, 30.0);
  EXPECT_EQ(config.planning.max_solutions, 1u);
  EXPECT_FALSE(config.execution_enabled);

  rclcpp::shutdown();
}

TEST(FixedPickPlaceConfig, RejectsInvalidVectorLength) {
  rclcpp::init(0, nullptr);
  auto options = options_with_overrides();
  options.parameter_overrides().push_back(
      rclcpp::Parameter("object.pose.xyz", std::vector<double>{0.55, 0.0}));
  auto node = std::make_shared<rclcpp::Node>("invalid_config_test", options);

  EXPECT_THROW(
      static_cast<void>(crx10ial_tasks::load_fixed_pick_place_config(*node)),
      std::runtime_error);

  rclcpp::shutdown();
}
```

- [ ] **Step 2: Run config gtest and verify it fails**

Run:

```bash
source /opt/ros/humble/setup.bash
colcon test --packages-select crx10ial_tasks --event-handlers console_direct+
```

Expected: fails because the config header and source do not exist.

- [ ] **Step 3: Add config header**

Create `src/crx10ial_tasks/include/crx10ial_tasks/fixed_pick_place_config.hpp`:

```cpp
#pragma once

#include <geometry_msgs/msg/pose.hpp>
#include <geometry_msgs/msg/vector3.hpp>
#include <rclcpp/node.hpp>

#include <array>
#include <cstddef>
#include <string>

namespace crx10ial_tasks {

struct ObjectConfig {
  std::string id;
  std::string frame_id;
  std::array<double, 3> dimensions;
  geometry_msgs::msg::Pose pose;
};

struct ApproachConfig {
  geometry_msgs::msg::Vector3 direction;
  double min_distance;
  double max_distance;
};

struct GraspConfig {
  std::string frame_id;
  geometry_msgs::msg::Pose pose;
  ApproachConfig approach;
  ApproachConfig retreat;
};

struct PlaceConfig {
  std::string frame_id;
  geometry_msgs::msg::Pose pose;
};

struct GripperConfig {
  double open_width_m;
  double close_width_m;
  double close_force_n;
};

struct PlanningConfig {
  std::size_t max_solutions;
  double timeout_sec;
};

struct FixedPickPlaceConfig {
  std::string arm_group_name;
  std::string eef_name;
  std::string hand_frame;
  std::string world_frame;
  ObjectConfig object;
  GraspConfig grasp;
  PlaceConfig place;
  PlaceConfig failure_place;
  GripperConfig gripper;
  PlanningConfig planning;
  bool execution_enabled;
};

FixedPickPlaceConfig load_fixed_pick_place_config(rclcpp::Node& node);
geometry_msgs::msg::Pose compose_pose(
    const geometry_msgs::msg::Pose& base,
    const geometry_msgs::msg::Pose& offset);

}  // namespace crx10ial_tasks
```

- [ ] **Step 4: Add config implementation**

Create `src/crx10ial_tasks/src/fixed_pick_place_config.cpp`:

```cpp
#include <crx10ial_tasks/fixed_pick_place_config.hpp>

#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Transform.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

#include <stdexcept>
#include <vector>

namespace crx10ial_tasks {
namespace {

std::vector<double> declare_double_array(rclcpp::Node& node, const std::string& name) {
  node.declare_parameter<std::vector<double>>(name);
  auto values = node.get_parameter(name).as_double_array();
  if (values.size() != 3) {
    throw std::runtime_error(name + " must contain exactly 3 values");
  }
  return values;
}

std::array<double, 3> to_array3(const std::vector<double>& values) {
  return {values[0], values[1], values[2]};
}

geometry_msgs::msg::Pose pose_from_parameters(
    rclcpp::Node& node,
    const std::string& prefix) {
  const auto xyz = declare_double_array(node, prefix + ".xyz");
  const auto rpy = declare_double_array(node, prefix + ".rpy");

  tf2::Quaternion q;
  q.setRPY(rpy[0], rpy[1], rpy[2]);
  q.normalize();

  geometry_msgs::msg::Pose pose;
  pose.position.x = xyz[0];
  pose.position.y = xyz[1];
  pose.position.z = xyz[2];
  pose.orientation = tf2::toMsg(q);
  return pose;
}

geometry_msgs::msg::Vector3 vector_from_parameters(
    rclcpp::Node& node,
    const std::string& name) {
  const auto values = declare_double_array(node, name);
  geometry_msgs::msg::Vector3 vector;
  vector.x = values[0];
  vector.y = values[1];
  vector.z = values[2];
  return vector;
}

double positive_double(rclcpp::Node& node, const std::string& name) {
  node.declare_parameter<double>(name);
  const double value = node.get_parameter(name).as_double();
  if (value <= 0.0) {
    throw std::runtime_error(name + " must be positive");
  }
  return value;
}

}  // namespace

FixedPickPlaceConfig load_fixed_pick_place_config(rclcpp::Node& node) {
  FixedPickPlaceConfig config;

  config.arm_group_name = node.declare_parameter<std::string>("arm_group_name");
  config.eef_name = node.declare_parameter<std::string>("eef_name");
  config.hand_frame = node.declare_parameter<std::string>("hand_frame");
  config.world_frame = node.declare_parameter<std::string>("world_frame");

  config.object.id = node.declare_parameter<std::string>("object.id");
  config.object.frame_id = node.declare_parameter<std::string>("object.frame_id");
  config.object.dimensions = to_array3(declare_double_array(node, "object.dimensions"));
  config.object.pose = pose_from_parameters(node, "object.pose");

  config.grasp.frame_id = node.declare_parameter<std::string>("grasp.frame_id");
  config.grasp.pose = pose_from_parameters(node, "grasp.pose");
  config.grasp.approach.direction =
      vector_from_parameters(node, "grasp.approach.direction");
  config.grasp.approach.min_distance =
      positive_double(node, "grasp.approach.min");
  config.grasp.approach.max_distance =
      positive_double(node, "grasp.approach.max");
  config.grasp.retreat.direction =
      vector_from_parameters(node, "grasp.retreat.direction");
  config.grasp.retreat.min_distance =
      positive_double(node, "grasp.retreat.min");
  config.grasp.retreat.max_distance =
      positive_double(node, "grasp.retreat.max");

  if (config.grasp.approach.min_distance > config.grasp.approach.max_distance) {
    throw std::runtime_error("grasp.approach.min must be <= grasp.approach.max");
  }
  if (config.grasp.retreat.min_distance > config.grasp.retreat.max_distance) {
    throw std::runtime_error("grasp.retreat.min must be <= grasp.retreat.max");
  }

  config.place.frame_id = node.declare_parameter<std::string>("place.frame_id");
  config.place.pose = pose_from_parameters(node, "place.pose");
  config.failure_place.frame_id = config.place.frame_id;
  config.failure_place.pose = pose_from_parameters(node, "failure.place.pose");

  config.gripper.open_width_m = positive_double(node, "gripper.open_width_m");
  config.gripper.close_width_m = positive_double(node, "gripper.close_width_m");
  config.gripper.close_force_n = positive_double(node, "gripper.close_force_n");

  node.declare_parameter<int>("planning.max_solutions");
  const int max_solutions = node.get_parameter("planning.max_solutions").as_int();
  if (max_solutions <= 0) {
    throw std::runtime_error("planning.max_solutions must be positive");
  }
  config.planning.max_solutions = static_cast<std::size_t>(max_solutions);
  config.planning.timeout_sec = positive_double(node, "planning.timeout_sec");
  config.execution_enabled = node.declare_parameter<bool>("execution.enabled");

  return config;
}

geometry_msgs::msg::Pose compose_pose(
    const geometry_msgs::msg::Pose& base,
    const geometry_msgs::msg::Pose& offset) {
  tf2::Transform base_tf;
  tf2::Transform offset_tf;
  tf2::fromMsg(base, base_tf);
  tf2::fromMsg(offset, offset_tf);
  return tf2::toMsg(base_tf * offset_tf);
}

}  // namespace crx10ial_tasks
```

- [ ] **Step 5: Update CMake and dependencies**

Replace `src/crx10ial_tasks/CMakeLists.txt` with:

```cmake
cmake_minimum_required(VERSION 3.8)
project(crx10ial_tasks)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_gtest REQUIRED)
find_package(ament_cmake_pytest REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)

set(CONFIG_DEPS
  geometry_msgs
  rclcpp
  tf2
  tf2_geometry_msgs
)

add_library(fixed_pick_place_config
  src/fixed_pick_place_config.cpp
)
target_include_directories(fixed_pick_place_config PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(fixed_pick_place_config ${CONFIG_DEPS})

install(TARGETS fixed_pick_place_config
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)
install(DIRECTORY include/
  DESTINATION include
)
install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  ament_add_pytest_test(fixed_pick_place_yaml
    test/test_fixed_pick_place_yaml.py
  )

  ament_add_gtest(test_fixed_pick_place_config
    test/test_fixed_pick_place_config.cpp
  )
  target_link_libraries(test_fixed_pick_place_config fixed_pick_place_config)
  ament_target_dependencies(test_fixed_pick_place_config ${CONFIG_DEPS})
endif()

ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
ament_export_dependencies(${CONFIG_DEPS})
ament_package()
```

Add to `src/crx10ial_tasks/package.xml`:

```xml
  <depend>geometry_msgs</depend>
  <depend>rclcpp</depend>
  <depend>tf2</depend>
  <depend>tf2_geometry_msgs</depend>

  <test_depend>ament_cmake_gtest</test_depend>
```

- [ ] **Step 6: Run config tests**

Run:

```bash
source /opt/ros/humble/setup.bash
colcon test --packages-select crx10ial_tasks --event-handlers console_direct+
colcon test-result --verbose
```

Expected: YAML and C++ config tests pass.

- [ ] **Step 7: Commit config loader**

Run:

```bash
git add src/crx10ial_tasks
git commit -m "feat: load fixed pick place config"
```

## Task 3: Add MTC Planning Task and C1 Source Contract Tests

**Files:**
- Create: `src/crx10ial_tasks/include/crx10ial_tasks/fixed_pick_place_task.hpp`
- Create: `src/crx10ial_tasks/src/fixed_pick_place_task.cpp`
- Create: `src/crx10ial_tasks/test/test_task_source_contract.py`
- Modify: `src/crx10ial_tasks/CMakeLists.txt`
- Modify: `src/crx10ial_tasks/package.xml`

- [ ] **Step 1: Write source contract tests**

Create `src/crx10ial_tasks/test/test_task_source_contract.py`:

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_mtc_task_uses_internal_attach_and_detach_stages():
    source = _read("src/fixed_pick_place_task.cpp")

    assert 'ModifyPlanningScene>("internal attach object"' in source
    assert ".attachObject(config.object.id, config.hand_frame)" in source
    assert 'ModifyPlanningScene>("internal detach object"' in source
    assert ".detachObject(config.object.id, config.hand_frame)" in source


def test_m3_does_not_call_mtc_task_execute():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "src" / "fixed_pick_place_task.cpp",
            ROOT / "src" / "fixed_pick_place_node.cpp",
        ]
        if path.exists()
    )

    assert ".execute(" not in combined
    assert "execute_task_solution" not in combined


def test_mtc_failure_diagnostics_are_reported():
    source = _read("src/fixed_pick_place_task.cpp")

    assert "task.explainFailure" in source
    assert "task.printState" in source
    assert "solutions().empty()" in source


def test_mtc_moves_to_pregrasp_before_approach():
    source = _read("src/fixed_pick_place_task.cpp")

    assert 'MoveTo>("move to pregrasp pose"' in source
    assert "const auto pregrasp_pose = translated_pose(" in source
    assert "stage->setGoal(stamped_pose(config.object.frame_id, pregrasp_pose));" in source


def test_execute_mock_attaches_before_grasp_motion_when_node_exists():
    node_path = ROOT / "src" / "fixed_pick_place_node.cpp"
    if not node_path.exists():
        return

    source = node_path.read_text(encoding="utf-8")
    attach_index = source.index("attach_object(node, config);")
    grasp_index = source.index(
        'move_to_pose(move_group, grasp_world_pose, config.hand_frame, "grasp");'
    )

    assert attach_index < grasp_index
```

- [ ] **Step 2: Run contract tests and verify they fail**

Run:

```bash
python3 -m pytest src/crx10ial_tasks/test/test_task_source_contract.py -q
```

Expected: fails because `fixed_pick_place_task.cpp` does not exist.

- [ ] **Step 3: Add MTC task header**

Create `src/crx10ial_tasks/include/crx10ial_tasks/fixed_pick_place_task.hpp`:

```cpp
#pragma once

#include <crx10ial_tasks/fixed_pick_place_config.hpp>

#include <moveit/task_constructor/task.h>
#include <rclcpp/node.hpp>

#include <memory>
#include <string>

namespace crx10ial_tasks {

struct FixedPickPlaceResult {
  bool success;
  std::string diagnostics;
  std::size_t solution_count;
};

moveit::task_constructor::Task build_fixed_pick_place_task(
    const rclcpp::Node::SharedPtr& node,
    const FixedPickPlaceConfig& config,
    const geometry_msgs::msg::Pose& place_pose);

FixedPickPlaceResult plan_fixed_pick_place(
    const rclcpp::Node::SharedPtr& node,
    const FixedPickPlaceConfig& config,
    bool use_failure_place);

}  // namespace crx10ial_tasks
```

- [ ] **Step 4: Add MTC task implementation**

Create `src/crx10ial_tasks/src/fixed_pick_place_task.cpp`:

```cpp
#include <crx10ial_tasks/fixed_pick_place_task.hpp>

#include <moveit/task_constructor/container.h>
#include <moveit/task_constructor/solvers/cartesian_path.h>
#include <moveit/task_constructor/solvers/pipeline_planner.h>
#include <moveit/task_constructor/stages/connect.h>
#include <moveit/task_constructor/stages/current_state.h>
#include <moveit/task_constructor/stages/modify_planning_scene.h>
#include <moveit/task_constructor/stages/move_relative.h>
#include <moveit/task_constructor/stages/move_to.h>

#include <geometry_msgs/msg/pose_stamped.hpp>

#include <sstream>
#include <utility>

namespace crx10ial_tasks {
namespace mtc = moveit::task_constructor;
namespace stages = moveit::task_constructor::stages;
namespace solvers = moveit::task_constructor::solvers;

namespace {

geometry_msgs::msg::PoseStamped stamped_pose(
    const std::string& frame_id,
    const geometry_msgs::msg::Pose& pose) {
  geometry_msgs::msg::PoseStamped stamped;
  stamped.header.frame_id = frame_id;
  stamped.pose = pose;
  return stamped;
}

geometry_msgs::msg::Vector3Stamped stamped_vector(
    const std::string& frame_id,
    const geometry_msgs::msg::Vector3& vector) {
  geometry_msgs::msg::Vector3Stamped stamped;
  stamped.header.frame_id = frame_id;
  stamped.vector = vector;
  return stamped;
}

geometry_msgs::msg::Pose translated_pose(
    geometry_msgs::msg::Pose pose,
    const geometry_msgs::msg::Vector3& direction,
    double distance) {
  pose.position.x += direction.x * distance;
  pose.position.y += direction.y * distance;
  pose.position.z += direction.z * distance;
  return pose;
}

}  // namespace

mtc::Task build_fixed_pick_place_task(
    const rclcpp::Node::SharedPtr& node,
    const FixedPickPlaceConfig& config,
    const geometry_msgs::msg::Pose& place_pose) {
  mtc::Task task("crx10ial fixed pick place");
  task.loadRobotModel(node);
  task.setProperty("group", config.arm_group_name);
  task.setProperty("eef", config.eef_name);
  task.setProperty("hand", config.eef_name);
  task.setProperty("hand_grasping_frame", config.hand_frame);
  task.setProperty("ik_frame", config.hand_frame);
  task.setTimeout(config.planning.timeout_sec);

  auto sampling_planner = std::make_shared<solvers::PipelinePlanner>(node);
  sampling_planner->setProperty("goal_joint_tolerance", 1e-4);

  auto cartesian_planner = std::make_shared<solvers::CartesianPath>();
  cartesian_planner->setMaxVelocityScalingFactor(0.2);
  cartesian_planner->setMaxAccelerationScalingFactor(0.2);
  cartesian_planner->setStepSize(0.01);

  task.add(std::make_unique<stages::CurrentState>("current state"));

  const auto grasp_world_pose = compose_pose(config.object.pose, config.grasp.pose);
  const auto pregrasp_pose = translated_pose(
      grasp_world_pose,
      config.grasp.approach.direction,
      -config.grasp.approach.max_distance);

  {
    auto stage = std::make_unique<stages::MoveTo>("move to pregrasp pose", sampling_planner);
    stage->setGroup(config.arm_group_name);
    stage->setIKFrame(config.hand_frame);
    stage->setGoal(stamped_pose(config.object.frame_id, pregrasp_pose));
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::MoveRelative>("approach object", cartesian_planner);
    stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
    stage->properties().set("link", config.hand_frame);
    stage->setMinMaxDistance(
        config.grasp.approach.min_distance,
        config.grasp.approach.max_distance);
    stage->setDirection(
        stamped_vector(config.hand_frame, config.grasp.approach.direction));
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::ModifyPlanningScene>(
        "allow collision gripper object");
    stage->allowCollisions(
        config.object.id,
        {config.eef_name, "gripper_palm", "left_finger", "right_finger", config.hand_frame},
        true);
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::ModifyPlanningScene>(
        "internal attach object");
    stage->attachObject(config.object.id, config.hand_frame);
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::MoveRelative>("retreat with object", cartesian_planner);
    stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
    stage->properties().set("link", config.hand_frame);
    stage->setMinMaxDistance(
        config.grasp.retreat.min_distance,
        config.grasp.retreat.max_distance);
    stage->setDirection(
        stamped_vector(config.hand_frame, config.grasp.retreat.direction));
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::Connect>(
        "move to place",
        stages::Connect::GroupPlannerVector{{config.arm_group_name, sampling_planner}});
    stage->setTimeout(config.planning.timeout_sec);
    stage->properties().configureInitFrom(mtc::Stage::PARENT);
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::MoveTo>("move to place pose", sampling_planner);
    stage->setGroup(config.arm_group_name);
    stage->setIKFrame(config.hand_frame);
    stage->setGoal(stamped_pose(config.place.frame_id, place_pose));
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::ModifyPlanningScene>(
        "internal detach object");
    stage->detachObject(config.object.id, config.hand_frame);
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::MoveRelative>("retreat after place", cartesian_planner);
    stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
    stage->properties().set("link", config.hand_frame);
    stage->setMinMaxDistance(
        config.grasp.retreat.min_distance,
        config.grasp.retreat.max_distance);
    stage->setDirection(
        stamped_vector(config.hand_frame, config.grasp.retreat.direction));
    task.add(std::move(stage));
  }

  task.init();
  return task;
}

FixedPickPlaceResult plan_fixed_pick_place(
    const rclcpp::Node::SharedPtr& node,
    const FixedPickPlaceConfig& config,
    bool use_failure_place) {
  const auto& target_place =
      use_failure_place ? config.failure_place.pose : config.place.pose;

  auto task = build_fixed_pick_place_task(node, config, target_place);
  const auto error_code = task.plan(config.planning.max_solutions);

  std::ostringstream diagnostics;
  task.printState(diagnostics);
  if (task.solutions().empty()) {
    task.explainFailure(diagnostics);
  }

  return FixedPickPlaceResult{
      static_cast<bool>(error_code) && !task.solutions().empty(),
      diagnostics.str(),
      task.solutions().size()};
}

}  // namespace crx10ial_tasks
```

- [ ] **Step 5: Update CMake and dependencies for MTC**

Add to `src/crx10ial_tasks/CMakeLists.txt` after the existing `find_package` calls:

```cmake
find_package(moveit_core REQUIRED)
find_package(moveit_ros_planning REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(moveit_task_constructor_core REQUIRED)
find_package(moveit_task_constructor_msgs REQUIRED)
```

Add after `fixed_pick_place_config`:

```cmake
set(MTC_DEPS
  moveit_core
  moveit_ros_planning
  moveit_ros_planning_interface
  moveit_task_constructor_core
  moveit_task_constructor_msgs
)

add_library(fixed_pick_place_task
  src/fixed_pick_place_task.cpp
)
target_include_directories(fixed_pick_place_task PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
target_link_libraries(fixed_pick_place_task fixed_pick_place_config)
ament_target_dependencies(fixed_pick_place_task ${CONFIG_DEPS} ${MTC_DEPS})

install(TARGETS fixed_pick_place_task
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)
```

Add `fixed_pick_place_task` to `ament_export_dependencies` dependency coverage by changing the final export line to:

```cmake
ament_export_dependencies(${CONFIG_DEPS} ${MTC_DEPS})
```

Add to `src/crx10ial_tasks/package.xml`:

```xml
  <depend>moveit_core</depend>
  <depend>moveit_ros_planning</depend>
  <depend>moveit_ros_planning_interface</depend>
  <depend>moveit_task_constructor_core</depend>
  <depend>moveit_task_constructor_msgs</depend>
```

Add a pytest entry to the `BUILD_TESTING` block in CMake:

```cmake
  ament_add_pytest_test(task_source_contract
    test/test_task_source_contract.py
  )
```

- [ ] **Step 6: Run source contract and build checks**

Run:

```bash
python3 -m pytest src/crx10ial_tasks/test/test_task_source_contract.py -q
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --symlink-install --packages-select crx10ial_tasks
colcon test --packages-select crx10ial_tasks
colcon test-result --verbose
```

Expected: contract tests pass, C++ builds, package tests pass.

- [ ] **Step 7: Commit MTC planner**

Run:

```bash
git add src/crx10ial_tasks
git commit -m "feat: add fixed pick place MTC planner"
```

## Task 4: Add Fixed Pick/Place Node and Launch

**Files:**
- Create: `src/crx10ial_tasks/src/fixed_pick_place_node.cpp`
- Create: `src/crx10ial_tasks/launch/fixed_pick_place.launch.py`
- Modify: `src/crx10ial_tasks/CMakeLists.txt`
- Modify: `src/crx10ial_tasks/package.xml`

- [ ] **Step 1: Add node source**

Create `src/crx10ial_tasks/src/fixed_pick_place_node.cpp`:

```cpp
#include <crx10ial_tasks/fixed_pick_place_config.hpp>
#include <crx10ial_tasks/fixed_pick_place_task.hpp>

#include <rclcpp/rclcpp.hpp>

#include <string>

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("fixed_pick_place");

  try {
    const auto mode = node->declare_parameter<std::string>("run_mode", "plan");
    const auto config = crx10ial_tasks::load_fixed_pick_place_config(*node);

    if (mode == "plan") {
      const auto result =
          crx10ial_tasks::plan_fixed_pick_place(node, config, false);
      RCLCPP_INFO_STREAM(node->get_logger(), result.diagnostics);
      if (!result.success) {
        RCLCPP_ERROR(node->get_logger(), "M3 fixed pick/place planning failed");
        rclcpp::shutdown();
        return 2;
      }
      RCLCPP_INFO(
          node->get_logger(),
          "M3 fixed pick/place planning succeeded with %zu solution(s)",
          result.solution_count);
      rclcpp::shutdown();
      return 0;
    }

    if (mode == "negative_plan") {
      const auto result =
          crx10ial_tasks::plan_fixed_pick_place(node, config, true);
      RCLCPP_INFO_STREAM(node->get_logger(), result.diagnostics);
      if (result.success || result.diagnostics.empty()) {
        RCLCPP_ERROR(
            node->get_logger(),
            "M3 negative planning was expected to fail with diagnostics");
        rclcpp::shutdown();
        return 3;
      }
      RCLCPP_INFO(node->get_logger(), "M3 negative planning produced diagnostics");
      rclcpp::shutdown();
      return 0;
    }

    RCLCPP_ERROR(node->get_logger(), "unsupported run_mode: %s", mode.c_str());
    rclcpp::shutdown();
    return 4;
  } catch (const std::exception& exc) {
    RCLCPP_ERROR(node->get_logger(), "fixed pick/place failed: %s", exc.what());
    rclcpp::shutdown();
    return 1;
  }
}
```

- [ ] **Step 2: Add launch file**

Create `src/crx10ial_tasks/launch/fixed_pick_place.launch.py`:

```python
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def launch_setup(context, *args, **kwargs):
    del args, kwargs

    robot_model = LaunchConfiguration("robot_model")
    run_mode = LaunchConfiguration("run_mode")
    config_file = LaunchConfiguration("config_file")

    robot_model_value = robot_model.perform(context)
    description_arguments = {
        "robot_ip": "1.1.1.1",
        "use_mock": "true",
        "gpio_configuration": os.path.join(
            get_package_share_directory("fanuc_hardware_interface"),
            "config",
            "example_gpio_config.yaml",
        ),
    }

    cell_xacro_path = os.path.join(
        get_package_share_directory("crx10ial_cell_description"),
        "urdf",
        "crx10ial_cell.urdf.xacro",
    )

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

    fixed_pick_place = Node(
        package="crx10ial_tasks",
        executable="fixed_pick_place",
        name="fixed_pick_place",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            config_file,
            {"run_mode": run_mode},
        ],
    )

    return [fixed_pick_place]


def generate_launch_description():
    default_config = os.path.join(
        get_package_share_directory("crx10ial_tasks"),
        "config",
        "fixed_pick_place.yaml",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "robot_model",
                default_value="crx10ia_l",
                choices=["crx10ia_l"],
            ),
            DeclareLaunchArgument(
                "run_mode",
                default_value="plan",
                choices=["plan", "negative_plan", "execute_mock"],
            ),
            DeclareLaunchArgument(
                "config_file",
                default_value=default_config,
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
```

- [ ] **Step 3: Update build files**

Add to `src/crx10ial_tasks/CMakeLists.txt`:

```cmake
add_executable(fixed_pick_place
  src/fixed_pick_place_node.cpp
)
target_link_libraries(fixed_pick_place
  fixed_pick_place_config
  fixed_pick_place_task
)
ament_target_dependencies(fixed_pick_place ${CONFIG_DEPS} ${MTC_DEPS})

install(TARGETS fixed_pick_place
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)
```

Add to `src/crx10ial_tasks/package.xml`:

```xml
  <exec_depend>crx10ial_cell_description</exec_depend>
  <exec_depend>fanuc_hardware_interface</exec_depend>
  <exec_depend>fanuc_moveit_config</exec_depend>
  <exec_depend>moveit_configs_utils</exec_depend>
```

- [ ] **Step 4: Build node**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --symlink-install --packages-select crx10ial_tasks
```

Expected: `fixed_pick_place` executable is installed.

- [ ] **Step 5: Commit node and launch**

Run:

```bash
git add src/crx10ial_tasks
git commit -m "feat: launch fixed pick place planner"
```

## Task 5: Add Mock Runtime Orchestration and Duplicate Attach Check

**Files:**
- Modify: `src/crx10ial_tasks/src/fixed_pick_place_node.cpp`
- Create: `src/crx10ial_tasks/test/check_single_attached_object.py`
- Modify: `src/crx10ial_tasks/CMakeLists.txt`
- Modify: `src/crx10ial_tasks/package.xml`

- [ ] **Step 1: Add planning-scene duplicate check script**

Create `src/crx10ial_tasks/test/check_single_attached_object.py`:

```python
import argparse
import sys

import rclpy
from moveit_msgs.srv import GetPlanningScene
from moveit_msgs.msg import PlanningSceneComponents


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-attached", type=int, required=True)
    parser.add_argument("--expected-world", type=int, required=True)
    args = parser.parse_args()

    rclpy.init()
    node = rclpy.create_node("check_single_attached_object")
    client = node.create_client(GetPlanningScene, "/get_planning_scene")
    if not client.wait_for_service(timeout_sec=30.0):
        print("ERROR: /get_planning_scene unavailable", file=sys.stderr)
        return 1

    request = GetPlanningScene.Request()
    request.components.components = (
        PlanningSceneComponents.WORLD_OBJECT_GEOMETRY
        | PlanningSceneComponents.ROBOT_STATE_ATTACHED_OBJECTS
    )
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future, timeout_sec=30.0)
    if not future.done() or future.result() is None:
        print("ERROR: /get_planning_scene call failed", file=sys.stderr)
        return 1

    scene = future.result().scene
    attached = [
        obj.object.id
        for obj in scene.robot_state.attached_collision_objects
        if obj.object.id == "work_object"
    ]
    world = [
        obj.id
        for obj in scene.world.collision_objects
        if obj.id == "work_object"
    ]

    print(f"attached_work_object_count={len(attached)}")
    print(f"world_work_object_count={len(world)}")

    node.destroy_node()
    rclpy.shutdown()
    return 0 if len(attached) == args.expected_attached and len(world) == args.expected_world else 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Replace node with execute_mock support**

Replace `src/crx10ial_tasks/src/fixed_pick_place_node.cpp` with:

```cpp
#include <crx10ial_tasks/fixed_pick_place_config.hpp>
#include <crx10ial_tasks/fixed_pick_place_task.hpp>

#include <crx10ial_interfaces/srv/attach_object.hpp>
#include <crx10ial_interfaces/srv/command_gripper.hpp>
#include <crx10ial_interfaces/srv/detach_object.hpp>
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit_msgs/msg/move_it_error_codes.hpp>
#include <moveit_msgs/msg/planning_scene_components.hpp>
#include <moveit_msgs/srv/get_planning_scene.hpp>
#include <rclcpp/rclcpp.hpp>

#include <chrono>
#include <memory>
#include <stdexcept>
#include <string>
#include <thread>

namespace {
using namespace std::chrono_literals;

template <typename ServiceT>
typename ServiceT::Response::SharedPtr call_service(
    const rclcpp::Node::SharedPtr& node,
    const std::string& service_name,
    const typename ServiceT::Request::SharedPtr& request,
    std::chrono::seconds timeout = 30s) {
  auto client = node->create_client<ServiceT>(service_name);
  if (!client->wait_for_service(timeout)) {
    throw std::runtime_error(service_name + " is not available");
  }
  auto future = client->async_send_request(request);
  if (future.wait_for(timeout) != std::future_status::ready) {
    throw std::runtime_error(service_name + " call timed out");
  }
  return future.get();
}

geometry_msgs::msg::Pose translated_pose(
    geometry_msgs::msg::Pose pose,
    const geometry_msgs::msg::Vector3& direction,
    double distance) {
  pose.position.x += direction.x * distance;
  pose.position.y += direction.y * distance;
  pose.position.z += direction.z * distance;
  return pose;
}

void move_to_pose(
    moveit::planning_interface::MoveGroupInterface& move_group,
    const geometry_msgs::msg::Pose& pose,
    const std::string& link_name,
    const std::string& label) {
  move_group.setStartStateToCurrentState();
  move_group.setPoseTarget(pose, link_name);
  const auto result = move_group.move();
  move_group.clearPoseTargets();
  if (result.val != moveit_msgs::msg::MoveItErrorCodes::SUCCESS) {
    throw std::runtime_error(label + " motion failed with code " + std::to_string(result.val));
  }
}

void command_gripper(
    const rclcpp::Node::SharedPtr& node,
    const crx10ial_tasks::FixedPickPlaceConfig& config,
    int command) {
  auto request = std::make_shared<crx10ial_interfaces::srv::CommandGripper::Request>();
  request->command = command;
  if (command == 1) {
    request->width_m = config.gripper.open_width_m;
    request->force_n = 0.0;
  } else {
    request->width_m = config.gripper.close_width_m;
    request->force_n = config.gripper.close_force_n;
  }
  const auto response =
      call_service<crx10ial_interfaces::srv::CommandGripper>(
          node, "/crx10ial_gripper/command", request);
  if (!response->success) {
    throw std::runtime_error("gripper command failed: " + response->message);
  }
}

void attach_object(
    const rclcpp::Node::SharedPtr& node,
    const crx10ial_tasks::FixedPickPlaceConfig& config) {
  auto request = std::make_shared<crx10ial_interfaces::srv::AttachObject::Request>();
  request->object_id = config.object.id;
  const auto response =
      call_service<crx10ial_interfaces::srv::AttachObject>(
          node, "/crx10ial_gripper/attach_object", request);
  if (!response->success || response->attached_object_id != config.object.id) {
    throw std::runtime_error("attach failed: " + response->message);
  }
}

void detach_object(const rclcpp::Node::SharedPtr& node) {
  auto request = std::make_shared<crx10ial_interfaces::srv::DetachObject::Request>();
  const auto response =
      call_service<crx10ial_interfaces::srv::DetachObject>(
          node, "/crx10ial_gripper/detach_object", request);
  if (!response->success || response->detached_object_id != "work_object") {
    throw std::runtime_error("detach failed: " + response->message);
  }
}

void verify_single_runtime_attachment(
    const rclcpp::Node::SharedPtr& node,
    const std::string& object_id) {
  auto request = std::make_shared<moveit_msgs::srv::GetPlanningScene::Request>();
  request->components.components =
      moveit_msgs::msg::PlanningSceneComponents::WORLD_OBJECT_GEOMETRY |
      moveit_msgs::msg::PlanningSceneComponents::ROBOT_STATE_ATTACHED_OBJECTS;
  const auto response =
      call_service<moveit_msgs::srv::GetPlanningScene>(
          node, "/get_planning_scene", request);

  std::size_t attached_count = 0;
  for (const auto& attached : response->scene.robot_state.attached_collision_objects) {
    if (attached.object.id == object_id) {
      ++attached_count;
    }
  }

  std::size_t world_count = 0;
  for (const auto& object : response->scene.world.collision_objects) {
    if (object.id == object_id) {
      ++world_count;
    }
  }

  if (attached_count != 1 || world_count != 0) {
    throw std::runtime_error(
        "expected one attached object and zero world duplicates for " + object_id);
  }
}

int run_plan_mode(
    const rclcpp::Node::SharedPtr& node,
    const crx10ial_tasks::FixedPickPlaceConfig& config,
    bool negative) {
  const auto result = crx10ial_tasks::plan_fixed_pick_place(node, config, negative);
  RCLCPP_INFO_STREAM(node->get_logger(), result.diagnostics);

  if (negative) {
    if (result.success || result.diagnostics.empty()) {
      RCLCPP_ERROR(
          node->get_logger(),
          "M3 negative planning was expected to fail with diagnostics");
      return 3;
    }
    RCLCPP_INFO(node->get_logger(), "M3 negative planning produced diagnostics");
    return 0;
  }

  if (!result.success) {
    RCLCPP_ERROR(node->get_logger(), "M3 fixed pick/place planning failed");
    return 2;
  }

  RCLCPP_INFO(
      node->get_logger(),
      "M3 fixed pick/place planning succeeded with %zu solution(s)",
      result.solution_count);
  return 0;
}

int run_execute_mock(
    const rclcpp::Node::SharedPtr& node,
    const crx10ial_tasks::FixedPickPlaceConfig& config) {
  const int plan_code = run_plan_mode(node, config, false);
  if (plan_code != 0) {
    return plan_code;
  }

  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);
  std::thread spinner([&executor]() { executor.spin(); });

  try {
    moveit::planning_interface::MoveGroupInterface move_group(node, config.arm_group_name);
    move_group.setPlanningTime(config.planning.timeout_sec);
    move_group.setMaxVelocityScalingFactor(0.2);
    move_group.setMaxAccelerationScalingFactor(0.2);

    const auto grasp_world_pose =
        crx10ial_tasks::compose_pose(config.object.pose, config.grasp.pose);
    const auto pregrasp_pose = translated_pose(
        grasp_world_pose,
        config.grasp.approach.direction,
        -config.grasp.approach.max_distance);
    const auto retreat_pose = translated_pose(
        grasp_world_pose,
        config.grasp.retreat.direction,
        config.grasp.retreat.max_distance);
    const auto post_place_pose = translated_pose(
        config.place.pose,
        config.grasp.retreat.direction,
        config.grasp.retreat.max_distance);

    command_gripper(node, config, 1);
    move_to_pose(move_group, pregrasp_pose, config.hand_frame, "pregrasp");
    command_gripper(node, config, 2);
    attach_object(node, config);
    verify_single_runtime_attachment(node, config.object.id);
    RCLCPP_INFO(node->get_logger(), "M3 single attached object verified");
    move_to_pose(move_group, grasp_world_pose, config.hand_frame, "grasp");
    move_to_pose(move_group, retreat_pose, config.hand_frame, "retreat");
    move_to_pose(move_group, config.place.pose, config.hand_frame, "place");
    detach_object(node);
    move_to_pose(move_group, post_place_pose, config.hand_frame, "post place retreat");
    RCLCPP_INFO(node->get_logger(), "M3 mock pick/place execution succeeded");
  } catch (...) {
    executor.cancel();
    if (spinner.joinable()) {
      spinner.join();
    }
    throw;
  }

  executor.cancel();
  if (spinner.joinable()) {
    spinner.join();
  }
  return 0;
}

}  // namespace

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("fixed_pick_place");

  try {
    const auto mode = node->declare_parameter<std::string>("run_mode", "plan");
    const auto config = crx10ial_tasks::load_fixed_pick_place_config(*node);

    int exit_code = 0;
    if (mode == "plan") {
      exit_code = run_plan_mode(node, config, false);
    } else if (mode == "negative_plan") {
      exit_code = run_plan_mode(node, config, true);
    } else if (mode == "execute_mock") {
      exit_code = run_execute_mock(node, config);
    } else {
      RCLCPP_ERROR(node->get_logger(), "unsupported run_mode: %s", mode.c_str());
      exit_code = 4;
    }

    rclcpp::shutdown();
    return exit_code;
  } catch (const std::exception& exc) {
    RCLCPP_ERROR(node->get_logger(), "fixed pick/place failed: %s", exc.what());
    rclcpp::shutdown();
    return 1;
  }
}
```

- [ ] **Step 3: Update build dependencies**

Add to `src/crx10ial_tasks/package.xml`:

```xml
  <depend>crx10ial_interfaces</depend>
  <depend>moveit_msgs</depend>
```

Add this dependency list in `src/crx10ial_tasks/CMakeLists.txt` after `MTC_DEPS`:

```cmake
set(RUNTIME_DEPS
  crx10ial_interfaces
  moveit_msgs
)
```

Change the `fixed_pick_place` target dependency line to:

```cmake
ament_target_dependencies(fixed_pick_place ${CONFIG_DEPS} ${MTC_DEPS} ${RUNTIME_DEPS})
```

Install the Python duplicate check:

```cmake
install(PROGRAMS
  test/check_single_attached_object.py
  DESTINATION lib/${PROJECT_NAME}
)
```

- [ ] **Step 4: Build runtime node**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --symlink-install --packages-select crx10ial_tasks
python3 -m pytest src/crx10ial_tasks/test/test_task_source_contract.py -q
```

Expected: build passes and C1 source contract still passes.

- [ ] **Step 5: Commit runtime orchestration**

Run:

```bash
git add src/crx10ial_tasks
git commit -m "feat: orchestrate mock pick place runtime"
```

## Task 6: Runtime Smoke Tests

**Files:**
- No long-lived files required unless a smoke command reveals a reproducible bug.

- [ ] **Step 1: Run full build and package tests**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --symlink-install
colcon test --packages-select crx10ial_tasks crx10ial_bringup crx10ial_gripper
colcon test-result --verbose
```

Expected: build succeeds and all selected tests pass.

- [ ] **Step 2: Run MTC plan-only smoke**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
set -euo pipefail

LOG=/tmp/crx10ial_m3_mock_launch.log
PLAN=/tmp/crx10ial_m3_plan.log
rm -f "${LOG}" "${PLAN}"

ros2 launch crx10ial_bringup mock.launch.py \
  launch_rviz:=false publish_scene:=true launch_gripper:=true \
  > "${LOG}" 2>&1 &
LAUNCH_PID=$!

cleanup() {
  if kill -0 "${LAUNCH_PID}" >/dev/null 2>&1; then
    kill "${LAUNCH_PID}" >/dev/null 2>&1 || true
    wait "${LAUNCH_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

for _ in $(seq 1 90); do
  ros2 service list > /tmp/crx10ial_m3_services.txt
  if grep -Fxq "/plan_kinematic_path" /tmp/crx10ial_m3_services.txt && \
     grep -Fxq "/get_planning_scene" /tmp/crx10ial_m3_services.txt && \
     grep -Fxq "/crx10ial_gripper/attach_object" /tmp/crx10ial_m3_services.txt; then
    break
  fi
  sleep 1
done

sleep 5

ros2 launch crx10ial_tasks fixed_pick_place.launch.py run_mode:=plan \
  2>&1 | tee "${PLAN}"

grep -q "M3 fixed pick/place planning succeeded" "${PLAN}"
! grep -E "Traceback|Exception|ModuleNotFoundError|PackageNotFoundError|Semantic description is not specified" "${LOG}"

cleanup
trap - EXIT
```

Expected: plan-only smoke reports success.

- [ ] **Step 3: Run negative planning smoke**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
set -euo pipefail

LOG=/tmp/crx10ial_m3_negative_mock_launch.log
NEG=/tmp/crx10ial_m3_negative.log
rm -f "${LOG}" "${NEG}"

ros2 launch crx10ial_bringup mock.launch.py \
  launch_rviz:=false publish_scene:=true launch_gripper:=true \
  > "${LOG}" 2>&1 &
LAUNCH_PID=$!

cleanup() {
  if kill -0 "${LAUNCH_PID}" >/dev/null 2>&1; then
    kill "${LAUNCH_PID}" >/dev/null 2>&1 || true
    wait "${LAUNCH_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

for _ in $(seq 1 90); do
  ros2 service list > /tmp/crx10ial_m3_negative_services.txt
  if grep -Fxq "/plan_kinematic_path" /tmp/crx10ial_m3_negative_services.txt && \
     grep -Fxq "/get_planning_scene" /tmp/crx10ial_m3_negative_services.txt && \
     grep -Fxq "/crx10ial_gripper/attach_object" /tmp/crx10ial_m3_negative_services.txt; then
    break
  fi
  sleep 1
done

sleep 5

ros2 launch crx10ial_tasks fixed_pick_place.launch.py run_mode:=negative_plan \
  2>&1 | tee "${NEG}"

grep -q "M3 negative planning produced diagnostics" "${NEG}"
grep -E "move to place pose|crx10ial fixed pick place|0 /" "${NEG}"
! grep -E "Traceback|Exception|ModuleNotFoundError|PackageNotFoundError|Semantic description is not specified" "${LOG}"

cleanup
trap - EXIT
```

Expected: negative smoke exits 0 because failure diagnostics were produced. The test does not pin one exact failing stage name; it requires non-empty MTC diagnostics.

- [ ] **Step 4: Run execute_mock smoke and duplicate attach check**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
set -euo pipefail

LOG=/tmp/crx10ial_m3_execute_mock_launch.log
EXEC=/tmp/crx10ial_m3_execute_mock.log
ATTACHED=/tmp/crx10ial_m3_attached_check.log
rm -f "${LOG}" "${EXEC}" "${ATTACHED}"

ros2 launch crx10ial_bringup mock.launch.py \
  launch_rviz:=false publish_scene:=true launch_gripper:=true \
  > "${LOG}" 2>&1 &
LAUNCH_PID=$!

cleanup() {
  if kill -0 "${LAUNCH_PID}" >/dev/null 2>&1; then
    kill "${LAUNCH_PID}" >/dev/null 2>&1 || true
    wait "${LAUNCH_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

for _ in $(seq 1 90); do
  ros2 service list > /tmp/crx10ial_m3_execute_services.txt
  if grep -Fxq "/plan_kinematic_path" /tmp/crx10ial_m3_execute_services.txt && \
     grep -Fxq "/crx10ial_gripper/attach_object" /tmp/crx10ial_m3_execute_services.txt && \
     grep -Fxq "/get_planning_scene" /tmp/crx10ial_m3_execute_services.txt; then
    break
  fi
  sleep 1
done

sleep 5

ros2 launch crx10ial_tasks fixed_pick_place.launch.py run_mode:=execute_mock \
  2>&1 | tee "${EXEC}"

grep -q "M3 fixed pick/place planning succeeded" "${EXEC}"
grep -q "M3 single attached object verified" "${EXEC}"
grep -q "M3 mock pick/place execution succeeded" "${EXEC}"

ros2 run crx10ial_tasks check_single_attached_object.py \
  --expected-attached 0 --expected-world 1 \
  2>&1 | tee "${ATTACHED}"
grep -q "attached_work_object_count=0" "${ATTACHED}"
grep -q "world_work_object_count=1" "${ATTACHED}"

! grep -E "Traceback|Exception|ModuleNotFoundError|PackageNotFoundError|Semantic description is not specified" "${LOG}"

cleanup
trap - EXIT
```

Expected: mock execution succeeds, fake gripper owns one attached `work_object`, and world collision objects do not contain a duplicate `work_object`.

- [ ] **Step 5: Commit runtime fixes if required**

If Task 6 required source changes, commit them:

```bash
git add src/crx10ial_bringup src/crx10ial_cell_description src/crx10ial_tasks
git commit -m "fix: stabilize fixed pick place smoke"
```

If no files changed, skip this step.

Runtime fixes found during execution:

- `work_object` is attachable PlanningScene state only. The cell URDF keeps static fixtures (`table`, `camera_stand`), while `mock_scene.py` publishes only the attachable `work_object`. This avoids duplicate URDF-link/collision-object self-collisions in MTC.
- The default grasp/place poses were raised to reachable, collision-free `grasp_link` targets. `grasp.pose` is object-relative and `place.pose` is the world-frame hand target used by MTC and execute_mock.
- The MTC task uses explicit forward-only `MoveTo` stages for pregrasp, approach, retreat, place, and post-place retreat. This avoids Humble MTC `PropagatingEitherWay` direction inference issues and CartesianPath flakiness while preserving configurable approach/retreat vectors for target calculation.
- Smoke waits include `/get_planning_scene` and a short settle delay. `/execute_trajectory` is not a service in this Humble/MoveIt setup, so Step 4 does not wait for it through `ros2 service list`.
- `check_single_attached_object.py` must be executable when using `--symlink-install`, otherwise `ros2 run` cannot discover it.

## Task 7: Final Verification and Push

**Files:**
- No new files.

- [ ] **Step 1: Run final verification**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --symlink-install
colcon test --packages-select \
  crx10ial_cell_description \
  crx10ial_interfaces \
  crx10ial_gripper \
  crx10ial_bringup \
  crx10ial_tasks
colcon test-result --verbose
```

Expected: full build succeeds and selected tests have 0 failures.

- [ ] **Step 2: Re-run Task 6 smoke commands**

Run Task 6 Step 2, Step 3, and Step 4 exactly as written.

Expected:

- Plan-only smoke reports `M3 fixed pick/place planning succeeded`.
- Negative smoke reports `M3 negative planning produced diagnostics`.
- Execute smoke reports `M3 mock pick/place execution succeeded`.
- During execution, the node reports `M3 single attached object verified` immediately after fake-gripper attach.
- After completion, attached-object check reports `attached_work_object_count=0` and `world_work_object_count=1`.

- [ ] **Step 3: Inspect diff and status**

Run:

```bash
git status --short --branch
git log --oneline origin/m3-fixed-pick-place..HEAD || true
git diff --stat origin/m2-workcell-gripper..HEAD
```

Expected: working tree is clean and commits are only M3 work.

- [ ] **Step 4: Push**

Run:

```bash
git push -u origin m3-fixed-pick-place
git rev-parse HEAD
git ls-remote origin refs/heads/m3-fixed-pick-place
```

Expected: local HEAD SHA matches the remote branch SHA.

## Self-Review Checklist

- [x] MTC apt binary availability is checked before source changes.
- [x] `crx10ial_tasks` remains an `ament_cmake` package and gains gtest/pytest coverage.
- [x] Object, grasp, place, approach, retreat, and gripper values are configurable in YAML.
- [x] MTC is used for fixed pick/place planning.
- [x] `Task::execute()` is explicitly forbidden by source-contract test.
- [x] Runtime attach/detach remains owned by `fake_gripper`.
- [x] Duplicate attached object is checked through `/get_planning_scene`.
- [x] Negative planning smoke requires diagnostics without pinning one flaky stage name.
- [x] Gazebo, iRVision, ROBOGUIDE, and hardware remain outside M3.
