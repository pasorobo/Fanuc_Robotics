# Quickstart

This page takes a contributor from a fresh Ubuntu 22.04 machine to a running mock pick/place demo. It does not cover Gazebo, ROBOGUIDE, hardware, or iRVision; those are separate milestones.

## Prerequisites

- Ubuntu 22.04 LTS, x86-64.
- ROS 2 Humble desktop install. See `docs/setup/ubuntu22_humble.md` for the long form.
- Network access for git clones and apt installs.
- A user account with `sudo`.

If you do not yet have ROS 2 Humble:

```bash
sudo apt update
sudo apt install -y software-properties-common curl gnupg lsb-release
# Follow https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
sudo apt install -y ros-humble-desktop python3-colcon-common-extensions \
  python3-rosdep python3-vcstool git git-lfs
sudo rosdep init || true
rosdep update
```

## Clone and build

```bash
mkdir -p ~/Develop/Fanuc
cd ~/Develop/Fanuc
git clone <this-repo-url> Fanuc_Robotics
cd Fanuc_Robotics

source /opt/ros/humble/setup.bash
./scripts/import_dependencies.sh third_party.humble.lock.repos
sudo apt install -y ros-humble-moveit ros-humble-moveit-task-constructor-core \
  ros-humble-moveit-task-constructor-msgs \
  ros-humble-moveit-task-constructor-capabilities \
  ros-humble-moveit-task-constructor-visualization
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble \
  --skip-keys ament_python
colcon build --symlink-install
source install/setup.bash
```

## Mock launch

```bash
ros2 launch crx10ial_bringup mock.launch.py \
  launch_rviz:=true publish_scene:=true launch_gripper:=true
```

You should see RViz open with the CRX-10iA/L, table, work object, camera stand, and gripper. The fake gripper services are available under `/crx10ial_gripper/`.

For headless verification (no display):

```bash
timeout 45s ros2 launch crx10ial_bringup mock.launch.py \
  launch_rviz:=false publish_scene:=true launch_gripper:=true
```

The command exits with status 124 after 45 s. That is expected; it means the launch reached steady state.

## Run the fixed pick/place demo (M3)

In one terminal, start the mock cell:

```bash
ros2 launch crx10ial_bringup mock.launch.py \
  launch_rviz:=false publish_scene:=true launch_gripper:=true
```

In a second terminal:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch crx10ial_tasks fixed_pick_place.launch.py run_mode:=execute_mock
```

Expected log lines:

- `M3 fixed pick/place planning succeeded with 1 solution(s)`
- `M3 single attached object verified`
- `M3 mock pick/place execution succeeded`

To see actionable failure diagnostics for a deliberately unreachable goal:

```bash
ros2 launch crx10ial_tasks fixed_pick_place.launch.py run_mode:=negative_plan
```

Expected: the task reports `M3 negative planning produced diagnostics` plus a Failing stage breakdown.

## Where to go next

- Concepts: `docs/concepts/software_overview.md`, `docs/concepts/hardware_overview.md`.
- Architecture: `docs/architecture.md`.
- Frame conventions: `docs/frames.md`.
- When something does not work: `docs/troubleshooting.md`.
- Decision rationale: `docs/decisions/`.
