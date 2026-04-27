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
