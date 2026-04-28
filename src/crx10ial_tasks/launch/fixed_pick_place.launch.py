# Copyright 2026 Fanuc Robotics Maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
                description="FANUC CRX model to use for MoveIt parameters.",
            ),
            DeclareLaunchArgument(
                "run_mode",
                default_value="plan",
                choices=["plan", "negative_plan", "execute_mock"],
                description="Task node mode.",
            ),
            DeclareLaunchArgument(
                "config_file",
                default_value=default_config,
                description="Fixed pick/place task YAML file.",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
