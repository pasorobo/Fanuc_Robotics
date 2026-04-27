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
