# M0 M1 Humble Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Ubuntu 22.04 / ROS 2 Humble workspace foundation and prove CRX-10iA/L RViz/MoveIt mock planning can launch without physical hardware.

**Architecture:** The repository remains a ROS 2 workspace. Official FANUC packages are imported as third-party source dependencies, while project-local packages add workcell description, mock bringup, scene collision objects, tests, and setup documentation. Hardware, ROBOGUIDE, Gazebo, iRVision, and gripper-specific behavior are intentionally outside this first plan.

**Tech Stack:** Ubuntu 22.04, ROS 2 Humble, colcon, vcs, rosdep, ament_cmake, ament_python, xacro, FANUC `fanuc_description`, FANUC `fanuc_driver`, MoveIt 2, Python 3.10, pytest.

---

## Scope

This plan implements only the approved design's M0 and M1 milestones:

- M0: workspace foundation, dependency manifests, setup documentation, package skeletons.
- M1: CRX-10iA/L cell xacro, mock MoveIt launch, static planning-scene collision publisher, and tests.

This plan does not add Gazebo, ROBOGUIDE, physical hardware, iRVision, MoveIt Task Constructor, or physical gripper control.

## File Structure

Create or modify these files:

```text
.gitignore
README.md
third_party.humble.repos
third_party.humble.lock.repos
scripts/import_dependencies.sh
docs/setup/ubuntu22_humble.md
docker/ubuntu22_humble/Dockerfile
src/crx10ial_interfaces/CMakeLists.txt
src/crx10ial_interfaces/package.xml
src/crx10ial_interfaces/README.md
src/crx10ial_cell_description/CMakeLists.txt
src/crx10ial_cell_description/package.xml
src/crx10ial_cell_description/README.md
src/crx10ial_cell_description/launch/view_cell.launch.py
src/crx10ial_cell_description/rviz/view_cell.rviz
src/crx10ial_cell_description/test/test_cell_description.py
src/crx10ial_cell_description/urdf/crx10ial_cell.urdf.xacro
src/crx10ial_bringup/package.xml
src/crx10ial_bringup/setup.cfg
src/crx10ial_bringup/setup.py
src/crx10ial_bringup/README.md
src/crx10ial_bringup/resource/crx10ial_bringup
src/crx10ial_bringup/crx10ial_bringup/__init__.py
src/crx10ial_bringup/crx10ial_bringup/mock_scene.py
src/crx10ial_bringup/crx10ial_bringup/mock_scene_node.py
src/crx10ial_bringup/launch/mock.launch.py
src/crx10ial_bringup/test/test_mock_scene.py
src/crx10ial_tasks/CMakeLists.txt
src/crx10ial_tasks/package.xml
src/crx10ial_tasks/README.md
src/crx10ial_vision_bridge/CMakeLists.txt
src/crx10ial_vision_bridge/package.xml
src/crx10ial_vision_bridge/README.md
src/crx10ial_gripper/CMakeLists.txt
src/crx10ial_gripper/package.xml
src/crx10ial_gripper/README.md
src/crx10ial_safety/CMakeLists.txt
src/crx10ial_safety/package.xml
src/crx10ial_safety/README.md
src/crx10ial_sim/CMakeLists.txt
src/crx10ial_sim/package.xml
src/crx10ial_sim/README.md
src/crx10ial_tests/CMakeLists.txt
src/crx10ial_tests/package.xml
src/crx10ial_tests/README.md
```

Responsibilities:

- Top-level files document the workspace and pin official FANUC source dependencies.
- `crx10ial_cell_description` owns the CRX-10iA/L workcell xacro, RViz visualization launch, and xacro expansion test.
- `crx10ial_bringup` owns the mock MoveIt launch and static collision publisher used by the M1 demo.
- Other `crx10ial_*` packages are minimal ROS 2 packages that reserve the approved architecture boundaries for later milestones while remaining buildable now.

## Task 0: Verify Pinned FANUC Upstream Layout

**Files:**
- No repository files are created or modified.

- [ ] **Step 1: Install or verify required tooling**

Run:

```bash
if ! command -v git >/dev/null 2>&1; then
  sudo apt update
  sudo apt install -y git
fi

if ! command -v vcs >/dev/null 2>&1; then
  if sudo -n true 2>/dev/null; then
    sudo apt update
    sudo apt install -y python3-vcstool
  else
    python3 -m pip install --user vcstool
    export PATH="${HOME}/.local/bin:${PATH}"
  fi
fi

command -v git
command -v vcs
python3 --version
```

Expected: `git` and `vcs` paths are printed, and Python prints its version. In non-interactive environments without passwordless sudo, `vcs` may resolve from `${HOME}/.local/bin`.

- [ ] **Step 2: Create a temporary locked upstream manifest**

Run:

```bash
rm -rf /tmp/fanuc_humble_upstream_check
mkdir -p /tmp/fanuc_humble_upstream_check/src
cd /tmp/fanuc_humble_upstream_check

cat > fanuc_upstream.lock.repos <<'YAML'
repositories:
  fanuc_description:
    type: git
    url: https://github.com/FANUC-CORPORATION/fanuc_description.git
    version: de27dcbc36e2e6268ec3a5b4fd49d87c71d42928
  fanuc_driver:
    type: git
    url: https://github.com/FANUC-CORPORATION/fanuc_driver.git
    version: 8dc93117618515f0cdd5ec51df0dbeaee3971d4f
YAML
```

Expected: `/tmp/fanuc_humble_upstream_check/fanuc_upstream.lock.repos` exists.

- [ ] **Step 3: Import the pinned upstream repositories**

Run:

```bash
cd /tmp/fanuc_humble_upstream_check
vcs import src < fanuc_upstream.lock.repos
git -C src/fanuc_driver submodule update --init --recursive
```

Expected: `src/fanuc_description` and `src/fanuc_driver` exist, and `fanuc_driver` submodules finish without errors.

- [ ] **Step 4: Verify imported commits match the plan pins**

Run:

```bash
cd /tmp/fanuc_humble_upstream_check
test "$(git -C src/fanuc_description rev-parse HEAD)" = "de27dcbc36e2e6268ec3a5b4fd49d87c71d42928"
test "$(git -C src/fanuc_driver rev-parse HEAD)" = "8dc93117618515f0cdd5ec51df0dbeaee3971d4f"
```

Expected: both `test` commands exit `0`.

- [ ] **Step 5: Verify required upstream ROS package names**

Run:

```bash
cd /tmp/fanuc_humble_upstream_check
find src/fanuc_description src/fanuc_driver -maxdepth 2 -name package.xml -print | sort | tee package_files.txt
grep -Fx "src/fanuc_description/fanuc_crx_description/package.xml" package_files.txt
grep -Fx "src/fanuc_driver/fanuc_hardware_interface/package.xml" package_files.txt
grep -Fx "src/fanuc_driver/fanuc_moveit_config/package.xml" package_files.txt
grep -Fx "src/fanuc_driver/fanuc_msgs/package.xml" package_files.txt
```

Expected: each `grep` prints the matching package path. These package names are the names used by later xacro, launch, and MoveIt steps.

- [ ] **Step 6: Verify CRX-10iA/L description and macro signature**

Run:

```bash
cd /tmp/fanuc_humble_upstream_check
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET

macro_path = Path("src/fanuc_description/fanuc_crx_description/urdf/crx10ia_l_urdf_macro.xacro")
robot_path = Path("src/fanuc_description/fanuc_crx_description/robot/crx10ia_l.urdf.xacro")

assert macro_path.is_file(), macro_path
assert robot_path.is_file(), robot_path

root = ET.parse(macro_path).getroot()
macro = None
for element in root.iter():
    if element.tag.endswith("macro") and element.attrib.get("name") == "crx10ia_l":
        macro = element
        break

assert macro is not None, "crx10ia_l macro not found"
params = macro.attrib["params"].split()
for required in ["parent", "*origin", "child"]:
    assert required in params, f"missing macro parameter: {required}"

robot_text = robot_path.read_text()
assert '<xacro:crx10ia_l parent="world" child="ee_link">' in robot_text
print("crx10ia_l macro signature ok")
PY
```

Expected: Python prints `crx10ia_l macro signature ok`.

- [ ] **Step 7: Verify FANUC driver files used by mock launch and MoveIt**

Run:

```bash
cd /tmp/fanuc_humble_upstream_check
test -f src/fanuc_driver/fanuc_hardware_interface/robot/crx10ia_l.urdf.xacro
test -f src/fanuc_driver/fanuc_hardware_interface/launch/fanuc_mock_control.launch.py
test -f src/fanuc_driver/fanuc_moveit_config/launch/fanuc_moveit.launch.py
test -f src/fanuc_driver/fanuc_moveit_config/srdf/crx10ia_l.srdf

python3 - <<'PY'
from pathlib import Path

hardware_xacro = Path("src/fanuc_driver/fanuc_hardware_interface/robot/crx10ia_l.urdf.xacro").read_text()
mock_launch = Path("src/fanuc_driver/fanuc_hardware_interface/launch/fanuc_mock_control.launch.py").read_text()
moveit_launch = Path("src/fanuc_driver/fanuc_moveit_config/launch/fanuc_moveit.launch.py").read_text()
srdf = Path("src/fanuc_driver/fanuc_moveit_config/srdf/crx10ia_l.srdf").read_text()

assert '<xacro:arg name="use_mock" default="false"/>' in hardware_xacro
assert '<xacro:crx10ia_l parent="world" child="end_effector">' in hardware_xacro
assert '<xacro:crx_control name="crx10ia_l"/>' in hardware_xacro
assert "fanuc_mock_control.launch.py" in moveit_launch
assert "robot_model" in mock_launch
assert "robot_series" in mock_launch
assert '<group name="manipulator">' in srdf
assert '<chain base_link="base_link" tip_link="flange"/>' in srdf
assert '<group_state name="default" group="manipulator">' in srdf
for expected_joint in [
    '<joint name="J1" value="0"/>',
    '<joint name="J2" value="0"/>',
    '<joint name="J3" value="0"/>',
    '<joint name="J4" value="0"/>',
    '<joint name="J5" value="-1.5708"/>',
    '<joint name="J6" value="0"/>',
]:
    assert expected_joint in srdf
print("fanuc mock and MoveIt files ok")
PY
```

Expected: Python prints `fanuc mock and MoveIt files ok`.

- [ ] **Step 8: Leave the repository unchanged**

Run from the project repository:

```bash
cd /home/dev/Develop/Fanuc/Fanuc_Robotics
git status --short --branch
```

Expected: the project repository has no changes caused by Task 0.

## Task 1: Add Workspace Metadata and Dependency Manifests

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Create: `third_party.humble.repos`
- Create: `third_party.humble.lock.repos`
- Create: `scripts/import_dependencies.sh`

- [ ] **Step 1: Verify the expected files are missing**

Run:

```bash
test ! -f README.md
test ! -f third_party.humble.repos
test ! -f third_party.humble.lock.repos
test ! -f scripts/import_dependencies.sh
```

Expected: all commands exit `0`.

- [ ] **Step 2: Create `.gitignore`**

Create `.gitignore`:

```gitignore
build/
install/
log/
.colcon/
*.pyc
__pycache__/
.pytest_cache/
.mypy_cache/
.vscode/
.idea/
*.swp
*.swo
src/fanuc_description/
src/fanuc_driver/
```

- [ ] **Step 3: Create `third_party.humble.repos`**

Create `third_party.humble.repos`:

```yaml
repositories:
  fanuc_description:
    type: git
    url: https://github.com/FANUC-CORPORATION/fanuc_description.git
    version: v1.2.2
  fanuc_driver:
    type: git
    url: https://github.com/FANUC-CORPORATION/fanuc_driver.git
    version: humble
```

- [ ] **Step 4: Create `third_party.humble.lock.repos`**

Create `third_party.humble.lock.repos`:

```yaml
repositories:
  fanuc_description:
    type: git
    url: https://github.com/FANUC-CORPORATION/fanuc_description.git
    version: de27dcbc36e2e6268ec3a5b4fd49d87c71d42928
  fanuc_driver:
    type: git
    url: https://github.com/FANUC-CORPORATION/fanuc_driver.git
    version: 8dc93117618515f0cdd5ec51df0dbeaee3971d4f
```

- [ ] **Step 5: Create `scripts/import_dependencies.sh`**

Create directory `scripts` and file `scripts/import_dependencies.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

mkdir -p src

manifest="${1:-third_party.humble.repos}"

if ! command -v vcs >/dev/null 2>&1; then
  echo "vcs is not installed. Install python3-vcstool first." >&2
  exit 1
fi

vcs import src < "${manifest}"

if [ -d src/fanuc_driver/.git ]; then
  git -C src/fanuc_driver submodule update --init --recursive
fi

if [ -d src/fanuc_description/.git ]; then
  if git -C src/fanuc_description lfs version >/dev/null 2>&1; then
    git -C src/fanuc_description lfs install --local
    git -C src/fanuc_description lfs pull
  else
    echo "git-lfs is not installed; skipping FANUC mesh LFS download." >&2
  fi
fi
```

Make it executable:

```bash
chmod +x scripts/import_dependencies.sh
```

- [ ] **Step 6: Create `README.md`**

Create `README.md`:

````markdown
# Fanuc_Robotics

ROS 2 Humble workspace for validating FANUC CRX-10iA/L visualization, MoveIt mock planning, and later staged integration with simulation, ROBOGUIDE, hardware, and iRVision.

## Target Environment

- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill
- Robot model: FANUC CRX-10iA/L (`crx10ia_l`)
- Primary upstream stack: FANUC official ROS 2 driver and description packages

## Bootstrap

```bash
source /opt/ros/humble/setup.bash
sudo apt update
sudo apt install -y git git-lfs python3-vcstool python3-colcon-common-extensions python3-rosdep
./scripts/import_dependencies.sh
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
colcon build --symlink-install
source install/setup.bash
```

## Mock Launch

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=true publish_scene:=true
```

For headless smoke checks:

```bash
timeout 45s ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=false publish_scene:=true
```

The timeout command is expected to exit with code `124` after launch has remained alive long enough to inspect startup logs.
````

- [ ] **Step 7: Verify YAML and script syntax**

Run:

```bash
python3 - <<'PY'
import pathlib
import yaml
for path in ["third_party.humble.repos", "third_party.humble.lock.repos"]:
    data = yaml.safe_load(pathlib.Path(path).read_text())
    assert "repositories" in data
    assert "fanuc_description" in data["repositories"]
    assert "fanuc_driver" in data["repositories"]
PY
bash -n scripts/import_dependencies.sh
```

Expected: both commands exit `0`.

- [ ] **Step 8: Commit**

Run:

```bash
git add .gitignore README.md third_party.humble.repos third_party.humble.lock.repos scripts/import_dependencies.sh
git commit -m "chore: add Humble workspace dependency manifests"
```

Expected: commit succeeds.

## Task 2: Add Ubuntu 22.04 Setup Documentation and Docker Baseline

**Files:**
- Create: `docs/setup/ubuntu22_humble.md`
- Create: `docker/ubuntu22_humble/Dockerfile`

- [ ] **Step 1: Verify the documentation files are missing**

Run:

```bash
test ! -f docs/setup/ubuntu22_humble.md
test ! -f docker/ubuntu22_humble/Dockerfile
```

Expected: both commands exit `0`.

- [ ] **Step 2: Create `docs/setup/ubuntu22_humble.md`**

Create `docs/setup/ubuntu22_humble.md`:

````markdown
# Ubuntu 22.04 / ROS 2 Humble Setup

## Supported Host

Use Ubuntu 22.04 LTS with ROS 2 Humble. This repository does not target Ubuntu 24.04 or ROS 2 Jazzy in the first milestones.

## Native Setup

```bash
sudo apt update
sudo apt install -y software-properties-common curl gnupg lsb-release
sudo apt install -y git git-lfs python3-vcstool python3-colcon-common-extensions python3-rosdep
```

Install ROS 2 Humble Desktop from the official ROS 2 packages, then initialize rosdep if it has not already been initialized on the machine:

```bash
sudo rosdep init
rosdep update
```

If `sudo rosdep init` reports that `/etc/ros/rosdep/sources.list.d/20-default.list` already exists, run only:

```bash
rosdep update
```

## Workspace Setup

```bash
cd ~/Develop/Fanuc/Fanuc_Robotics
source /opt/ros/humble/setup.bash
./scripts/import_dependencies.sh
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
colcon build --symlink-install
source install/setup.bash
```

## Mock Validation

```bash
ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=true publish_scene:=true
```

Use the headless variant in CI-like terminals:

```bash
timeout 45s ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=false publish_scene:=true
```

The headless command should stay alive until `timeout` stops it. Investigate Python tracebacks, missing package errors, controller spawn failures, or MoveIt configuration errors.

## Hardware Boundary

Do not use this M0/M1 setup to move a physical robot. Physical controller work requires a separate hardware plan, controller option inventory, safety review, and explicit `mode:=hardware` launch profile.
````

- [ ] **Step 3: Create `docker/ubuntu22_humble/Dockerfile`**

Create `docker/ubuntu22_humble/Dockerfile`:

```dockerfile
FROM osrf/ros:humble-desktop

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    git-lfs \
    python3-colcon-common-extensions \
    python3-pip \
    python3-rosdep \
    python3-vcstool \
    && rm -rf /var/lib/apt/lists/*

RUN git lfs install --system

WORKDIR /workspace/Fanuc_Robotics

CMD ["bash"]
```

- [ ] **Step 4: Verify Dockerfile parses**

Run:

```bash
docker build --no-cache -t fanuc-robotics:humble -f docker/ubuntu22_humble/Dockerfile .
```

Expected: image build exits `0`.

If Docker is not installed on the host, run this syntax-only check instead:

```bash
python3 - <<'PY'
from pathlib import Path
text = Path("docker/ubuntu22_humble/Dockerfile").read_text()
assert text.startswith("FROM osrf/ros:humble-desktop")
assert "python3-vcstool" in text
assert "WORKDIR /workspace/Fanuc_Robotics" in text
PY
```

Expected: syntax-only check exits `0`.

- [ ] **Step 5: Commit**

Run:

```bash
git add docs/setup/ubuntu22_humble.md docker/ubuntu22_humble/Dockerfile
git commit -m "docs: add Ubuntu 22 Humble setup notes"
```

Expected: commit succeeds.

## Task 3: Create Buildable ROS 2 Package Skeletons

**Files:**
- Create: `src/crx10ial_interfaces/CMakeLists.txt`
- Create: `src/crx10ial_interfaces/package.xml`
- Create: `src/crx10ial_interfaces/README.md`
- Create: `src/crx10ial_tasks/CMakeLists.txt`
- Create: `src/crx10ial_tasks/package.xml`
- Create: `src/crx10ial_tasks/README.md`
- Create: `src/crx10ial_vision_bridge/CMakeLists.txt`
- Create: `src/crx10ial_vision_bridge/package.xml`
- Create: `src/crx10ial_vision_bridge/README.md`
- Create: `src/crx10ial_gripper/CMakeLists.txt`
- Create: `src/crx10ial_gripper/package.xml`
- Create: `src/crx10ial_gripper/README.md`
- Create: `src/crx10ial_safety/CMakeLists.txt`
- Create: `src/crx10ial_safety/package.xml`
- Create: `src/crx10ial_safety/README.md`
- Create: `src/crx10ial_sim/CMakeLists.txt`
- Create: `src/crx10ial_sim/package.xml`
- Create: `src/crx10ial_sim/README.md`
- Create: `src/crx10ial_tests/CMakeLists.txt`
- Create: `src/crx10ial_tests/package.xml`
- Create: `src/crx10ial_tests/README.md`

- [ ] **Step 1: Verify skeleton packages are missing**

Run:

```bash
for pkg in crx10ial_interfaces crx10ial_tasks crx10ial_vision_bridge crx10ial_gripper crx10ial_safety crx10ial_sim crx10ial_tests; do
  test ! -d "src/${pkg}"
done
```

Expected: command exits `0`.

- [ ] **Step 2: Create `crx10ial_interfaces` files**

Create `src/crx10ial_interfaces/package.xml`:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>crx10ial_interfaces</name>
  <version>0.1.0</version>
  <description>Shared interfaces for the CRX-10iA/L workcell.</description>
  <maintainer email="codex@openai.com">Fanuc Robotics Maintainers</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>
  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Create `src/crx10ial_interfaces/CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(crx10ial_interfaces)

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

Create `src/crx10ial_interfaces/README.md`:

```markdown
# crx10ial_interfaces

Shared ROS 2 interfaces for later task, vision, gripper, and safety packages.
```

- [ ] **Step 3: Create `crx10ial_tasks` files**

Create `src/crx10ial_tasks/package.xml`:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>crx10ial_tasks</name>
  <version>0.1.0</version>
  <description>Task-level planning package for the CRX-10iA/L workcell.</description>
  <maintainer email="codex@openai.com">Fanuc Robotics Maintainers</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>
  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Create `src/crx10ial_tasks/CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(crx10ial_tasks)

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

Create `src/crx10ial_tasks/README.md`:

```markdown
# crx10ial_tasks

Task-level planning package reserved for MoveIt Task Constructor work in the fixed pick-and-place milestone.
```

- [ ] **Step 4: Create `crx10ial_vision_bridge` files**

Create `src/crx10ial_vision_bridge/package.xml`:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>crx10ial_vision_bridge</name>
  <version>0.1.0</version>
  <description>Vision bridge package for simulated vision and FANUC iRVision result adapters.</description>
  <maintainer email="codex@openai.com">Fanuc Robotics Maintainers</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>
  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Create `src/crx10ial_vision_bridge/CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(crx10ial_vision_bridge)

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

Create `src/crx10ial_vision_bridge/README.md`:

```markdown
# crx10ial_vision_bridge

Vision adapter boundary for fake detections, simulated detections, and controller-backed iRVision results.
```

- [ ] **Step 5: Create `crx10ial_gripper` files**

Create `src/crx10ial_gripper/package.xml`:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>crx10ial_gripper</name>
  <version>0.1.0</version>
  <description>Gripper abstraction package for the CRX-10iA/L workcell.</description>
  <maintainer email="codex@openai.com">Fanuc Robotics Maintainers</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>
  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Create `src/crx10ial_gripper/CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(crx10ial_gripper)

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

Create `src/crx10ial_gripper/README.md`:

```markdown
# crx10ial_gripper

Gripper control abstraction for simulated and physical end effectors.
```

- [ ] **Step 6: Create `crx10ial_safety` files**

Create `src/crx10ial_safety/package.xml`:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>crx10ial_safety</name>
  <version>0.1.0</version>
  <description>Non-safety-rated runtime guard package for the CRX-10iA/L workcell.</description>
  <maintainer email="codex@openai.com">Fanuc Robotics Maintainers</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>
  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Create `src/crx10ial_safety/CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(crx10ial_safety)

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

Create `src/crx10ial_safety/README.md`:

```markdown
# crx10ial_safety

Runtime guard package for workspace limits, reduced-speed checks, and recovery helpers. This package is not a safety-rated control layer.
```

- [ ] **Step 7: Create `crx10ial_sim` files**

Create `src/crx10ial_sim/package.xml`:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>crx10ial_sim</name>
  <version>0.1.0</version>
  <description>Simulation package boundary for the CRX-10iA/L workcell.</description>
  <maintainer email="codex@openai.com">Fanuc Robotics Maintainers</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>
  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Create `src/crx10ial_sim/CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(crx10ial_sim)

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

Create `src/crx10ial_sim/README.md`:

```markdown
# crx10ial_sim

Simulation package boundary for Gazebo and ros2_control work in the simulation milestone.
```

- [ ] **Step 8: Create `crx10ial_tests` files**

Create `src/crx10ial_tests/package.xml`:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>crx10ial_tests</name>
  <version>0.1.0</version>
  <description>Cross-package test assets for the CRX-10iA/L workcell.</description>
  <maintainer email="codex@openai.com">Fanuc Robotics Maintainers</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>
  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Create `src/crx10ial_tests/CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(crx10ial_tests)

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

Create `src/crx10ial_tests/README.md`:

```markdown
# crx10ial_tests

Cross-package launch and integration tests for later milestones.
```

- [ ] **Step 9: Verify package discovery**

Run:

```bash
source /opt/ros/humble/setup.bash
colcon list --base-paths src --names-only
```

Expected output includes:

```text
crx10ial_gripper
crx10ial_interfaces
crx10ial_safety
crx10ial_sim
crx10ial_tasks
crx10ial_tests
crx10ial_vision_bridge
```

- [ ] **Step 10: Build skeleton packages**

Run:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select \
  crx10ial_interfaces \
  crx10ial_tasks \
  crx10ial_vision_bridge \
  crx10ial_gripper \
  crx10ial_safety \
  crx10ial_sim \
  crx10ial_tests
```

Expected: build exits `0`.

- [ ] **Step 11: Commit**

Run:

```bash
git add src/crx10ial_interfaces src/crx10ial_tasks src/crx10ial_vision_bridge src/crx10ial_gripper src/crx10ial_safety src/crx10ial_sim src/crx10ial_tests
git commit -m "chore: add CRX package skeletons"
```

Expected: commit succeeds.

## Task 4: Add CRX-10iA/L Cell Description and Xacro Test

**Files:**
- Create: `src/crx10ial_cell_description/CMakeLists.txt`
- Create: `src/crx10ial_cell_description/package.xml`
- Create: `src/crx10ial_cell_description/README.md`
- Create: `src/crx10ial_cell_description/urdf/crx10ial_cell.urdf.xacro`
- Create: `src/crx10ial_cell_description/launch/view_cell.launch.py`
- Create: `src/crx10ial_cell_description/rviz/view_cell.rviz`
- Create: `src/crx10ial_cell_description/test/test_cell_description.py`

- [ ] **Step 1: Write the failing xacro test**

Create `src/crx10ial_cell_description/test/test_cell_description.py` before creating the xacro file:

```python
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


def test_cell_xacro_expands_and_contains_static_workcell_links():
    source_dir = Path(os.environ["CRX10IAL_CELL_DESCRIPTION_SOURCE_DIR"])
    xacro_path = source_dir / "urdf" / "crx10ial_cell.urdf.xacro"

    result = subprocess.run(
        ["xacro", str(xacro_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    root = ET.fromstring(result.stdout)
    links = {link.attrib["name"] for link in root.findall("link")}
    joints = {joint.attrib["name"] for joint in root.findall("joint")}

    assert "world" in links
    assert "base_link" in links
    assert "table" in links
    assert "work_object" in links
    assert "camera_stand" in links
    assert "tool_stub" in links

    assert "world_to_table" in joints
    assert "table_to_work_object" in joints
    assert "world_to_camera_stand" in joints
    assert "end_effector_to_tool_stub" in joints
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
source /opt/ros/humble/setup.bash
pytest -q src/crx10ial_cell_description/test/test_cell_description.py
```

Expected: fail because `CRX10IAL_CELL_DESCRIPTION_SOURCE_DIR` or the xacro file is not available yet.

- [ ] **Step 3: Create `package.xml`**

Create `src/crx10ial_cell_description/package.xml`:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>crx10ial_cell_description</name>
  <version>0.1.0</version>
  <description>Workcell description for the FANUC CRX-10iA/L mock environment.</description>
  <maintainer email="codex@openai.com">Fanuc Robotics Maintainers</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <exec_depend>fanuc_crx_description</exec_depend>
  <exec_depend>joint_state_publisher_gui</exec_depend>
  <exec_depend>robot_state_publisher</exec_depend>
  <exec_depend>rviz2</exec_depend>
  <exec_depend>xacro</exec_depend>

  <test_depend>ament_cmake_pytest</test_depend>
  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

- [ ] **Step 4: Create `CMakeLists.txt`**

Create `src/crx10ial_cell_description/CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(crx10ial_cell_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch rviz urdf
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  find_package(ament_lint_auto REQUIRED)

  ament_add_pytest_test(
    test_cell_description
    test/test_cell_description.py
    APPEND_ENV CRX10IAL_CELL_DESCRIPTION_SOURCE_DIR=${CMAKE_CURRENT_SOURCE_DIR}
  )

  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

- [ ] **Step 5: Create the workcell xacro**

Create `src/crx10ial_cell_description/urdf/crx10ial_cell.urdf.xacro`:

```xml
<?xml version="1.0"?>
<robot name="crx10ial_cell" xmlns:xacro="http://wiki.ros.org/xacro">
  <xacro:include filename="$(find fanuc_crx_description)/urdf/crx10ia_l_urdf_macro.xacro"/>

  <link name="world"/>

  <xacro:crx10ia_l parent="world" child="end_effector">
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </xacro:crx10ia_l>

  <link name="table">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="1.0 0.7 0.04"/>
      </geometry>
      <material name="mat_table_gray">
        <color rgba="0.45 0.47 0.50 1.0"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="1.0 0.7 0.04"/>
      </geometry>
    </collision>
  </link>

  <joint name="world_to_table" type="fixed">
    <parent link="world"/>
    <child link="table"/>
    <origin xyz="0.75 0 0.70" rpy="0 0 0"/>
  </joint>

  <link name="work_object">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.08 0.05"/>
      </geometry>
      <material name="mat_work_object_blue">
        <color rgba="0.1 0.35 0.85 1.0"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.08 0.05"/>
      </geometry>
    </collision>
  </link>

  <joint name="table_to_work_object" type="fixed">
    <parent link="table"/>
    <child link="work_object"/>
    <origin xyz="-0.20 0 0.045" rpy="0 0 0"/>
  </joint>

  <link name="camera_stand">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.05 0.05 0.70"/>
      </geometry>
      <material name="mat_camera_stand_dark">
        <color rgba="0.12 0.12 0.12 1.0"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.05 0.05 0.70"/>
      </geometry>
    </collision>
  </link>

  <joint name="world_to_camera_stand" type="fixed">
    <parent link="world"/>
    <child link="camera_stand"/>
    <origin xyz="0.35 -0.55 0.35" rpy="0 0 0"/>
  </joint>

  <link name="tool_stub">
    <visual>
      <origin xyz="0 0 0.04" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.08 0.08"/>
      </geometry>
      <material name="mat_tool_stub_green">
        <color rgba="0.15 0.55 0.25 1.0"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0.04" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.08 0.08"/>
      </geometry>
    </collision>
  </link>

  <joint name="end_effector_to_tool_stub" type="fixed">
    <parent link="end_effector"/>
    <child link="tool_stub"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>
</robot>
```

- [ ] **Step 6: Create `view_cell.launch.py`**

Create `src/crx10ial_cell_description/launch/view_cell.launch.py`:

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    launch_rviz = LaunchConfiguration("launch_rviz")
    xacro_file = PathJoinSubstitution(
        [
            FindPackageShare("crx10ial_cell_description"),
            "urdf",
            "crx10ial_cell.urdf.xacro",
        ]
    )

    robot_description = {
        "robot_description": ParameterValue(
            Command(["xacro", " ", xacro_file]),
            value_type=str,
        )
    }

    rviz_config = PathJoinSubstitution(
        [
            FindPackageShare("crx10ial_cell_description"),
            "rviz",
            "view_cell.rviz",
        ]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "launch_rviz",
                default_value="true",
                choices=["true", "false"],
                description="Start RViz for workcell visualization.",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                output="both",
                parameters=[robot_description],
            ),
            Node(
                package="joint_state_publisher_gui",
                executable="joint_state_publisher_gui",
                output="both",
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                output="both",
                arguments=["--display-config", rviz_config],
                condition=IfCondition(launch_rviz),
            ),
        ]
    )
```

- [ ] **Step 7: Create RViz config**

Create `src/crx10ial_cell_description/rviz/view_cell.rviz`:

```yaml
Panels:
  - Class: rviz_common/Displays
Visualization Manager:
  Class: ""
  Displays:
    - Class: rviz_default_plugins/Grid
      Name: Grid
      Enabled: true
      Value: true
    - Class: rviz_default_plugins/RobotModel
      Name: RobotModel
      Enabled: true
      Value: true
      Description Topic:
        Value: /robot_description
  Global Options:
    Fixed Frame: world
  Tools:
    - Class: rviz_default_plugins/Interact
    - Class: rviz_default_plugins/MoveCamera
    - Class: rviz_default_plugins/Select
  Value: true
```

- [ ] **Step 8: Create package README**

Create `src/crx10ial_cell_description/README.md`:

```markdown
# crx10ial_cell_description

Workcell xacro for the CRX-10iA/L mock environment. This package composes the official FANUC CRX-10iA/L robot model with a table, work object, camera stand, and simple tool stub for early visualization and planning-scene checks.
```

- [ ] **Step 9: Run the test to verify it passes**

Run:

```bash
source /opt/ros/humble/setup.bash
./scripts/import_dependencies.sh third_party.humble.lock.repos
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
colcon build --symlink-install --packages-up-to crx10ial_cell_description
colcon test --packages-select crx10ial_cell_description --event-handlers console_direct+
colcon test-result --verbose --test-result-base build/crx10ial_cell_description
```

Expected: build exits `0`; test result reports `0` failures.

- [ ] **Step 10: Commit**

Run:

```bash
git add src/crx10ial_cell_description
git commit -m "feat: add CRX workcell description"
```

Expected: commit succeeds.

## Task 5: Add Mock Planning Scene Publisher and Unit Tests

**Files:**
- Create: `src/crx10ial_bringup/package.xml`
- Create: `src/crx10ial_bringup/setup.cfg`
- Create: `src/crx10ial_bringup/setup.py`
- Create: `src/crx10ial_bringup/README.md`
- Create: `src/crx10ial_bringup/crx10ial_bringup/__init__.py`
- Create: `src/crx10ial_bringup/crx10ial_bringup/mock_scene.py`
- Create: `src/crx10ial_bringup/crx10ial_bringup/mock_scene_node.py`
- Create: `src/crx10ial_bringup/test/test_mock_scene.py`

- [ ] **Step 1: Write the failing unit test**

Create `src/crx10ial_bringup/test/test_mock_scene.py`:

```python
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive

from crx10ial_bringup.mock_scene import build_collision_objects


def test_build_collision_objects_returns_expected_ids_and_frame():
    objects = build_collision_objects(frame_id="world")

    assert [obj.id for obj in objects] == [
        "work_table",
        "work_object",
        "camera_stand",
    ]
    assert all(obj.header.frame_id == "world" for obj in objects)
    assert all(obj.operation == CollisionObject.ADD for obj in objects)


def test_work_table_dimensions_are_stable():
    objects = {obj.id: obj for obj in build_collision_objects(frame_id="world")}
    table = objects["work_table"]

    assert table.primitives[0].type == SolidPrimitive.BOX
    assert list(table.primitives[0].dimensions) == [1.0, 0.7, 0.04]
    assert table.primitive_poses[0].position.x == 0.75
    assert table.primitive_poses[0].position.y == 0.0
    assert table.primitive_poses[0].position.z == 0.70
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
source /opt/ros/humble/setup.bash
PYTHONPATH=src/crx10ial_bringup pytest -q src/crx10ial_bringup/test/test_mock_scene.py
```

Expected: fail because `crx10ial_bringup.mock_scene` does not exist yet.

- [ ] **Step 3: Create `package.xml`**

Create `src/crx10ial_bringup/package.xml`:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>crx10ial_bringup</name>
  <version>0.1.0</version>
  <description>Bringup launch files for the CRX-10iA/L workcell.</description>
  <maintainer email="codex@openai.com">Fanuc Robotics Maintainers</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_python</buildtool_depend>

  <exec_depend>controller_manager</exec_depend>
  <exec_depend>fanuc_hardware_interface</exec_depend>
  <exec_depend>fanuc_moveit_config</exec_depend>
  <exec_depend>geometry_msgs</exec_depend>
  <exec_depend>moveit_configs_utils</exec_depend>
  <exec_depend>moveit_msgs</exec_depend>
  <exec_depend>moveit_ros_move_group</exec_depend>
  <exec_depend>rclpy</exec_depend>
  <exec_depend>rviz2</exec_depend>
  <exec_depend>shape_msgs</exec_depend>

  <test_depend>pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

- [ ] **Step 4: Create Python package metadata**

Create `src/crx10ial_bringup/setup.cfg`:

```ini
[develop]
script_dir=$base/lib/crx10ial_bringup
[install]
install_scripts=$base/lib/crx10ial_bringup
```

Create `src/crx10ial_bringup/setup.py`:

```python
from glob import glob
from setuptools import find_packages, setup

package_name = "crx10ial_bringup"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Fanuc Robotics Maintainers",
    maintainer_email="codex@openai.com",
    description="Bringup launch files for the CRX-10iA/L workcell.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "publish_mock_scene = crx10ial_bringup.mock_scene_node:main",
        ],
    },
)
```

Create package resource marker:

```bash
mkdir -p src/crx10ial_bringup/resource src/crx10ial_bringup/crx10ial_bringup
touch src/crx10ial_bringup/resource/crx10ial_bringup
```

Create `src/crx10ial_bringup/crx10ial_bringup/__init__.py`:

```python
"""Bringup helpers for the CRX-10iA/L workcell."""
```

- [ ] **Step 5: Create collision object helpers**

Create `src/crx10ial_bringup/crx10ial_bringup/mock_scene.py`:

```python
from dataclasses import dataclass
from typing import Iterable, List

from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive


@dataclass(frozen=True)
class BoxSpec:
    object_id: str
    dimensions: tuple[float, float, float]
    xyz: tuple[float, float, float]


SCENE_BOXES: tuple[BoxSpec, ...] = (
    BoxSpec("work_table", (1.0, 0.7, 0.04), (0.75, 0.0, 0.70)),
    BoxSpec("work_object", (0.08, 0.08, 0.05), (0.55, 0.0, 0.745)),
    BoxSpec("camera_stand", (0.05, 0.05, 0.70), (0.35, -0.55, 0.35)),
)


def _identity_pose(x: float, y: float, z: float) -> Pose:
    pose = Pose()
    pose.position.x = x
    pose.position.y = y
    pose.position.z = z
    pose.orientation.w = 1.0
    return pose


def build_collision_object(spec: BoxSpec, frame_id: str) -> CollisionObject:
    primitive = SolidPrimitive()
    primitive.type = SolidPrimitive.BOX
    primitive.dimensions = list(spec.dimensions)

    obj = CollisionObject()
    obj.header.frame_id = frame_id
    obj.id = spec.object_id
    obj.primitives.append(primitive)
    obj.primitive_poses.append(_identity_pose(*spec.xyz))
    obj.operation = CollisionObject.ADD
    return obj


def build_collision_objects(frame_id: str = "world") -> List[CollisionObject]:
    return [build_collision_object(spec, frame_id) for spec in SCENE_BOXES]


def iter_collision_objects(frame_id: str = "world") -> Iterable[CollisionObject]:
    return iter(build_collision_objects(frame_id=frame_id))
```

- [ ] **Step 6: Create publisher node**

Create `src/crx10ial_bringup/crx10ial_bringup/mock_scene_node.py`:

```python
import rclpy
from moveit_msgs.msg import CollisionObject
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from crx10ial_bringup.mock_scene import build_collision_objects


class MockScenePublisher(Node):
    def __init__(self) -> None:
        super().__init__("mock_scene_publisher")
        self.declare_parameter("frame_id", "world")
        self.declare_parameter("publish_period_sec", 2.0)

        qos = QoSProfile(depth=10)
        qos.reliability = ReliabilityPolicy.RELIABLE
        qos.durability = DurabilityPolicy.TRANSIENT_LOCAL

        self._publisher = self.create_publisher(CollisionObject, "/collision_object", qos)
        period = float(self.get_parameter("publish_period_sec").value)
        self._timer = self.create_timer(period, self.publish_scene)
        self.publish_scene()

    def publish_scene(self) -> None:
        frame_id = str(self.get_parameter("frame_id").value)
        for obj in build_collision_objects(frame_id=frame_id):
            self._publisher.publish(obj)
            self.get_logger().debug(
                f"Published collision object '{obj.id}' in frame '{frame_id}'"
            )


def main() -> None:
    rclpy.init()
    node = MockScenePublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Create package README**

Create `src/crx10ial_bringup/README.md`:

````markdown
# crx10ial_bringup

Bringup package for M0/M1 mock validation. The mock launch starts FANUC's official mock control path, MoveIt, optional RViz, and a static planning-scene collision publisher for the table, work object, and camera stand.
````

- [ ] **Step 8: Run unit tests**

Run:

```bash
source /opt/ros/humble/setup.bash
PYTHONPATH=src/crx10ial_bringup pytest -q src/crx10ial_bringup/test/test_mock_scene.py
```

Expected: `2 passed`.

- [ ] **Step 9: Build package**

Run:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select crx10ial_bringup
```

Expected: build exits `0`.

- [ ] **Step 10: Commit**

Run:

```bash
git add src/crx10ial_bringup
git commit -m "feat: add mock planning scene publisher"
```

Expected: commit succeeds.

## Task 6: Add CRX-10iA/L Mock MoveIt Launch

**Files:**
- Create: `src/crx10ial_bringup/launch/mock.launch.py`
- Modify: `src/crx10ial_bringup/README.md`

- [ ] **Step 1: Verify launch file is missing**

Run:

```bash
test ! -f src/crx10ial_bringup/launch/mock.launch.py
```

Expected: command exits `0`.

- [ ] **Step 2: Create `mock.launch.py`**

Create `src/crx10ial_bringup/launch/mock.launch.py`:

```python
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder


def launch_setup(context, *args, **kwargs):
    robot_model = LaunchConfiguration("robot_model")
    robot_ip = LaunchConfiguration("robot_ip")
    launch_rviz = LaunchConfiguration("launch_rviz")
    publish_scene = LaunchConfiguration("publish_scene")
    ros2_control_config = LaunchConfiguration("ros2_control_config")
    gpio_configuration = LaunchConfiguration("gpio_configuration")

    robot_model_value = robot_model.perform(context)
    description_arguments = {
        "robot_ip": robot_ip.perform(context),
        "use_mock": "true",
        "gpio_configuration": gpio_configuration.perform(context),
    }

    urdf_full_path = os.path.join(
        get_package_share_directory("fanuc_hardware_interface"),
        "robot",
        f"{robot_model_value}.urdf.xacro",
    )

    moveit_config = (
        MoveItConfigsBuilder(robot_model_value, package_name="fanuc_moveit_config")
        .robot_description(file_path=urdf_full_path, mappings=description_arguments)
        .robot_description_semantic(file_path=f"srdf/{robot_model_value}.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_scene_monitor(
            publish_robot_description=True,
            publish_robot_description_semantic=True,
        )
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )

    mock_control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("fanuc_hardware_interface"),
                    "launch",
                    "fanuc_mock_control.launch.py",
                ]
            )
        ),
        launch_arguments={
            "robot_model": robot_model,
            "robot_series": "crx",
            "gpio_configuration": gpio_configuration,
            "ros2_control_config": ros2_control_config,
            "launch_rviz": "false",
        }.items(),
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

    return [mock_control, move_group, rviz, scene_publisher]


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
                description="GPIO configuration passed through to FANUC mock control.",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
```

- [ ] **Step 3: Update bringup README**

Replace `src/crx10ial_bringup/README.md` with:

````markdown
# crx10ial_bringup

Bringup package for M0/M1 mock validation. The mock launch starts FANUC's official mock control path, MoveIt, optional RViz, and a static planning-scene collision publisher for the table, work object, and camera stand.

## Mock Launch

```bash
ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=true publish_scene:=true
```

For headless smoke checks:

```bash
timeout 45s ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=false publish_scene:=true
```

The headless command should remain alive until `timeout` stops it.
````

- [ ] **Step 4: Compile Python files**

Run:

```bash
python3 -m compileall src/crx10ial_bringup
```

Expected: command exits `0`.

- [ ] **Step 5: Build bringup with official FANUC dependencies**

Run:

```bash
source /opt/ros/humble/setup.bash
./scripts/import_dependencies.sh third_party.humble.lock.repos
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
colcon build --symlink-install --packages-up-to crx10ial_bringup
```

Expected: build exits `0`.

- [ ] **Step 6: Run headless mock launch smoke check**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
set +e
timeout 45s ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=false publish_scene:=true 2>&1 | tee /tmp/crx10ial_mock_launch.log
status=${PIPESTATUS[0]}
set -e
test "${status}" -eq 124
! grep -E "Traceback|Exception|ModuleNotFoundError|PackageNotFoundError" /tmp/crx10ial_mock_launch.log
grep -E "move_group|mock_scene_publisher|joint_state_broadcaster|joint_trajectory_controller" /tmp/crx10ial_mock_launch.log
```

Expected:

- `timeout` exits with status `124`.
- no Python traceback or package-not-found error appears.
- launch output includes MoveIt, mock scene publisher, and controller activity.

- [ ] **Step 7: Commit**

Run:

```bash
git add src/crx10ial_bringup
git commit -m "feat: add CRX mock MoveIt launch"
```

Expected: commit succeeds.

## Task 7: Run Full M0/M1 Verification

**Files:**
- No new files.

- [ ] **Step 1: Import locked dependencies**

Run:

```bash
source /opt/ros/humble/setup.bash
./scripts/import_dependencies.sh third_party.humble.lock.repos
```

Expected: `src/fanuc_description` and `src/fanuc_driver` exist. `src/fanuc_driver/fanuc_libs/dependencies` contains initialized submodules.

- [ ] **Step 2: Install dependencies**

Run:

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
```

Expected: command exits `0`.

- [ ] **Step 3: Build the workspace**

Run:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

Expected: command exits `0`.

- [ ] **Step 4: Run package tests**

Run:

```bash
source /opt/ros/humble/setup.bash
colcon test --packages-select crx10ial_cell_description crx10ial_bringup --event-handlers console_direct+
colcon test-result --verbose
```

Expected: test result reports `0` failures.

- [ ] **Step 5: Verify xacro expansion from installed package**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
xacro "$(ros2 pkg prefix --share crx10ial_cell_description)/urdf/crx10ial_cell.urdf.xacro" > /tmp/crx10ial_cell.urdf
grep -q 'name="base_link"' /tmp/crx10ial_cell.urdf
grep -q 'name="table"' /tmp/crx10ial_cell.urdf
grep -q 'name="work_object"' /tmp/crx10ial_cell.urdf
grep -q 'name="camera_stand"' /tmp/crx10ial_cell.urdf
```

Expected: all commands exit `0`.

- [ ] **Step 6: Verify mock launch**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
set +e
timeout 45s ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=false publish_scene:=true 2>&1 | tee /tmp/crx10ial_mock_launch.log
status=${PIPESTATUS[0]}
set -e
test "${status}" -eq 124
! grep -E "Traceback|Exception|ModuleNotFoundError|PackageNotFoundError" /tmp/crx10ial_mock_launch.log
grep -E "move_group|mock_scene_publisher|joint_state_broadcaster|joint_trajectory_controller" /tmp/crx10ial_mock_launch.log
```

Expected: timeout status is `124`, no error pattern appears, and expected launch components appear in logs.

- [ ] **Step 7: Verify named-state joint-space planning through MoveIt**

Run:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
set -euo pipefail

rm -f /tmp/crx10ial_named_plan_launch.log /tmp/crx10ial_named_plan_check.log

ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=false publish_scene:=false \
  > /tmp/crx10ial_named_plan_launch.log 2>&1 &
LAUNCH_PID=$!

cleanup() {
  if kill -0 "${LAUNCH_PID}" >/dev/null 2>&1; then
    kill "${LAUNCH_PID}" >/dev/null 2>&1 || true
    wait "${LAUNCH_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

for _ in $(seq 1 60); do
  if ros2 service list | grep -qx "/plan_kinematic_path"; then
    break
  fi
  sleep 1
done

ros2 service list | grep -qx "/plan_kinematic_path"
sleep 10

python3 - <<'PY' | tee /tmp/crx10ial_named_plan_check.log
import sys

import rclpy
from moveit_msgs.msg import Constraints, JointConstraint, MoveItErrorCodes
from moveit_msgs.srv import GetMotionPlan


SRDF_DEFAULT_NAMED_STATE = {
    "J1": 0.0,
    "J2": 0.0,
    "J3": 0.0,
    "J4": 0.0,
    "J5": -1.5708,
    "J6": 0.0,
}


def build_request() -> GetMotionPlan.Request:
    request = GetMotionPlan.Request()
    motion_request = request.motion_plan_request
    motion_request.group_name = "manipulator"
    motion_request.num_planning_attempts = 5
    motion_request.allowed_planning_time = 5.0
    motion_request.max_velocity_scaling_factor = 0.1
    motion_request.max_acceleration_scaling_factor = 0.1
    motion_request.start_state.is_diff = True

    goal = Constraints()
    goal.name = "srdf_default_named_state"

    for joint_name, joint_value in SRDF_DEFAULT_NAMED_STATE.items():
        constraint = JointConstraint()
        constraint.joint_name = joint_name
        constraint.position = joint_value
        constraint.tolerance_above = 0.01
        constraint.tolerance_below = 0.01
        constraint.weight = 1.0
        goal.joint_constraints.append(constraint)

    motion_request.goal_constraints.append(goal)
    return request


def main() -> int:
    rclpy.init()
    node = rclpy.create_node("check_crx10ial_named_state_plan")
    try:
        client = node.create_client(GetMotionPlan, "/plan_kinematic_path")
        if not client.wait_for_service(timeout_sec=30.0):
            print("ERROR: /plan_kinematic_path service did not become available", file=sys.stderr)
            return 1

        future = client.call_async(build_request())
        rclpy.spin_until_future_complete(node, future, timeout_sec=30.0)

        if not future.done():
            print("ERROR: planning service call timed out", file=sys.stderr)
            return 1

        response = future.result()
        if response is None:
            print("ERROR: planning service returned no response", file=sys.stderr)
            return 1

        error_code = response.motion_plan_response.error_code.val
        if error_code != MoveItErrorCodes.SUCCESS:
            print(f"ERROR: expected MoveIt SUCCESS=1, got {error_code}", file=sys.stderr)
            return 1

        points = response.motion_plan_response.trajectory.joint_trajectory.points
        if not points:
            print("ERROR: planning response trajectory has no points", file=sys.stderr)
            return 1

        print("Motion planning succeeded for SRDF named state default")
        print(f"Trajectory points: {len(points)}")
        return 0
    finally:
        node.destroy_node()
        rclpy.shutdown()


raise SystemExit(main())
PY

grep -q "Motion planning succeeded for SRDF named state default" /tmp/crx10ial_named_plan_check.log
! grep -E "Traceback|Exception|ModuleNotFoundError|PackageNotFoundError" /tmp/crx10ial_named_plan_launch.log

cleanup
trap - EXIT
```

Expected:

- `/plan_kinematic_path` becomes available.
- `publish_scene:=false` keeps this check focused on joint-space planning to the named state; Step 6 already covers `publish_scene:=true` startup.
- Python prints `Motion planning succeeded for SRDF named state default`.
- `Trajectory points:` is greater than `0`.
- launch logs contain no Python traceback or package-not-found error.

- [ ] **Step 8: Check Git state**

Run:

```bash
git status --short --branch
```

Expected:

```text
## main...origin/main [gone]
```

or a clean branch status with no untracked or modified files.

## Self-Review Checklist

- H1 upstream package and xacro/launch name verification is covered by Task 0.
- M0 dependency manifests are covered by Task 1.
- M0 setup notes are covered by Task 2.
- M0 package skeletons are covered by Task 3.
- M1 workcell xacro and RViz visualization are covered by Task 4.
- M1 static planning scene collision objects are covered by Task 5.
- M1 mock MoveIt launch is covered by Task 6.
- M0/M1 build, test, xacro, launch, and named-state planning checks are covered by Task 7.
- Hardware, ROBOGUIDE, Gazebo, iRVision, task construction, and physical gripper behavior are excluded from this plan by scope.
