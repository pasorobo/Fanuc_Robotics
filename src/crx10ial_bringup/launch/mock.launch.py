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
        # Mirrors FANUC's upstream MoveIt mock-control include for CRX robots.
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
                description="GPIO configuration passed through to FANUC xacro and mock control.",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
