# crx10ial_bringup

Bringup package for M0/M1 mock validation. The mock launch starts FANUC's official mock control path, MoveIt, optional RViz, and a planning-scene collision publisher for the attachable work object. Static fixtures such as the table and camera stand live in the cell URDF.

## Mock Launch

Before running the mock launch, import and build the locked FANUC dependencies and source the workspace:

```bash
source /opt/ros/humble/setup.bash
./scripts/import_dependencies.sh third_party.humble.lock.repos
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
colcon build --symlink-install --packages-up-to crx10ial_bringup
source install/setup.bash
```

```bash
ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=true publish_scene:=true
```

For headless smoke checks:

```bash
timeout 45s ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=false publish_scene:=true
```

The headless command should remain alive until `timeout` stops it.
