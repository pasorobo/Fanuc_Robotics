# Fanuc_Robotics

ROS 2 Humble workspace for validating FANUC CRX-10iA/L visualization, MoveIt mock planning, fixed pick-and-place, and later staged integration with simulation, ROBOGUIDE, hardware, and iRVision.

## Target Environment

- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill
- Robot model: FANUC CRX-10iA/L (`crx10ia_l`)
- Primary upstream stack: FANUC official ROS 2 driver and description packages

For background, see [docs/concepts/software_overview.md](docs/concepts/software_overview.md) and [docs/concepts/hardware_overview.md](docs/concepts/hardware_overview.md).

## New here?

- [docs/quickstart.md](docs/quickstart.md) takes you from clone to running the M3 mock pick/place demo.
- [docs/concepts/](docs/concepts/) holds beginner-friendly overviews of the hardware, software stack, and a project glossary.
- [docs/architecture.md](docs/architecture.md) explains the four-layer architecture and the package responsibilities.

## Reference

- [docs/frames.md](docs/frames.md) - canonical frame conventions for the workcell.
- [docs/services_and_launches.md](docs/services_and_launches.md) - every project-defined service and launch file.
- [docs/yaml_schemas.md](docs/yaml_schemas.md) - configuration YAML reference.
- [docs/troubleshooting.md](docs/troubleshooting.md) - symptoms and fixes from M0-M3.

## Decisions

- [docs/decisions/](docs/decisions/) - architecture decision records (ADRs).

## Operations

- [docs/operations/hardware_inputs.md](docs/operations/hardware_inputs.md) - intake form for M6/M7 inputs.
- [docs/operations/roboguide_setup_checklist.md](docs/operations/roboguide_setup_checklist.md) - pre-flight for M6.
- [docs/operations/hardware_bringup_checklist.md](docs/operations/hardware_bringup_checklist.md) - pre-flight for M7.

## Bootstrap

```bash
source /opt/ros/humble/setup.bash
sudo apt update
sudo apt install -y git git-lfs python3-vcstool python3-colcon-common-extensions python3-rosdep
./scripts/import_dependencies.sh third_party.humble.lock.repos
sudo apt install -y ros-humble-moveit-task-constructor-core ros-humble-moveit-task-constructor-msgs ros-humble-moveit-task-constructor-capabilities ros-humble-moveit-task-constructor-visualization
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble --skip-keys ament_python
colcon build --symlink-install
source install/setup.bash
```

## Mock Launch

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=true publish_scene:=true launch_gripper:=true
```

For headless smoke checks:

```bash
timeout 45s ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=false publish_scene:=true launch_gripper:=true
```

The timeout command exits with code `124` after the launch reaches steady state.

## Status

| Milestone | Status |
|---|---|
| M0 Workspace Foundation | Done |
| M1 RViz and MoveIt Mock | Done |
| M2 Workcell and Gripper Model | Done |
| M3 Fixed Pick-and-Place | Done |
| M4 Gazebo Fortress Simulation | Planned |
| M5 Vision Interface (fake/sim) | Planned |
| M6 ROBOGUIDE Integration | Planned |
| M7 Physical Hardware Bringup | Planned |

See `docs/superpowers/specs/2026-04-27-ubuntu22-humble-crx10ial-design.md` for the full design.
