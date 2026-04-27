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

import ast
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


def _source_dir() -> Path:
    return Path(os.environ["CRX10IAL_CELL_DESCRIPTION_SOURCE_DIR"])


def _expanded_cell_urdf() -> ET.Element:
    xacro_path = _source_dir() / "urdf" / "crx10ial_cell.urdf.xacro"

    result = subprocess.run(
        ["xacro", str(xacro_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    return ET.fromstring(result.stdout)


def test_cell_xacro_expands_and_contains_static_workcell_links():
    root = _expanded_cell_urdf()
    links = {link.attrib["name"] for link in root.findall("link")}
    joints = {joint.attrib["name"] for joint in root.findall("joint")}

    assert root.attrib["name"] == "crx10ia_l"
    assert "world" in links
    assert "base_link" in links
    assert "table" in links
    assert "work_object" in links
    assert "camera_stand" in links
    assert "tool_link" in links
    assert "gripper_palm" in links
    assert "left_finger" in links
    assert "right_finger" in links
    assert "grasp_link" in links

    assert "world_to_table" in joints
    assert "table_to_work_object" in joints
    assert "world_to_camera_stand" in joints
    assert "end_effector_to_tool_link" in joints
    assert "tool_link_to_gripper_palm" in joints
    assert "tool_link_to_left_finger" in joints
    assert "tool_link_to_right_finger" in joints
    assert "tool_link_to_grasp_link" in joints


def test_cell_urdf_has_single_root_and_valid_joint_references():
    root = _expanded_cell_urdf()
    link_names = [link.attrib["name"] for link in root.findall("link")]
    joint_names = [joint.attrib["name"] for joint in root.findall("joint")]

    assert len(link_names) == len(set(link_names))
    assert len(joint_names) == len(set(joint_names))

    links = set(link_names)
    child_links = set()
    parent_child_pairs = set()

    for joint in root.findall("joint"):
        parent = joint.find("parent").attrib["link"]
        child = joint.find("child").attrib["link"]

        assert parent in links
        assert child in links

        child_links.add(child)
        parent_child_pairs.add((parent, child))

    assert links - child_links == {"world"}
    assert ("end_effector", "tool_link") in parent_child_pairs
    assert ("tool_link", "grasp_link") in parent_child_pairs


def _joint_origin(root: ET.Element, joint_name: str) -> ET.Element:
    joint = next(
        joint
        for joint in root.findall("joint")
        if joint.attrib["name"] == joint_name
    )
    return joint.find("origin")


def test_cell_xacro_contains_documented_gripper_frames():
    root = _expanded_cell_urdf()
    links = {link.attrib["name"] for link in root.findall("link")}
    joints = {joint.attrib["name"] for joint in root.findall("joint")}

    assert "tool_link" in links
    assert "gripper_palm" in links
    assert "left_finger" in links
    assert "right_finger" in links
    assert "grasp_link" in links

    assert "end_effector_to_tool_link" in joints
    assert "tool_link_to_gripper_palm" in joints
    assert "tool_link_to_left_finger" in joints
    assert "tool_link_to_right_finger" in joints
    assert "tool_link_to_grasp_link" in joints

    grasp_origin = _joint_origin(root, "tool_link_to_grasp_link")
    assert grasp_origin.attrib["xyz"] == "0.18 0 0"
    assert grasp_origin.attrib["rpy"] == "0 0 0"


def test_gripper_fingers_are_forward_of_palm_collision():
    root = _expanded_cell_urdf()

    left_origin = _joint_origin(root, "tool_link_to_left_finger")
    right_origin = _joint_origin(root, "tool_link_to_right_finger")

    assert left_origin.attrib["xyz"] == "0.17 0.055 0"
    assert right_origin.attrib["xyz"] == "0.17 -0.055 0"


def test_cell_xacro_includes_ros2_control_for_mock_moveit_bringup():
    root = _expanded_cell_urdf()
    ros2_control_names = {
        control.attrib["name"]
        for control in root.findall("ros2_control")
    }

    assert "crx10ia_l" in ros2_control_names


def test_joint_state_publisher_gui_is_not_unconditional():
    source_dir = Path(os.environ["CRX10IAL_CELL_DESCRIPTION_SOURCE_DIR"])
    launch_path = source_dir / "launch" / "view_cell.launch.py"
    tree = ast.parse(launch_path.read_text(encoding="utf-8"))

    gui_nodes = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or getattr(node.func, "id", None) != "Node":
            continue

        package = next(
            (
                keyword.value.value
                for keyword in node.keywords
                if keyword.arg == "package" and isinstance(keyword.value, ast.Constant)
            ),
            None,
        )
        if package == "joint_state_publisher_gui":
            gui_nodes.append(node)

    assert len(gui_nodes) == 1
    gui_condition = next(
        (keyword.value for keyword in gui_nodes[0].keywords if keyword.arg == "condition"),
        None,
    )

    assert isinstance(gui_condition, ast.Call)
    assert getattr(gui_condition.func, "id", None) == "IfCondition"
