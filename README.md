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
