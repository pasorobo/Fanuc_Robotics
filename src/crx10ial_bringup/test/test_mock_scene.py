from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive

import math

import pytest

from crx10ial_bringup.mock_scene import build_collision_objects
from crx10ial_bringup.mock_scene_node import validate_publish_period


def test_build_collision_objects_returns_expected_ids_and_frame():
    objects = build_collision_objects(frame_id="world")

    assert [obj.id for obj in objects] == ["work_object"]
    assert all(obj.header.frame_id == "world" for obj in objects)
    assert all(obj.operation == CollisionObject.ADD for obj in objects)


def test_work_object_dimensions_are_stable():
    objects = {obj.id: obj for obj in build_collision_objects(frame_id="world")}
    work_object = objects["work_object"]

    assert work_object.primitives[0].type == SolidPrimitive.BOX
    assert list(work_object.primitives[0].dimensions) == [0.08, 0.08, 0.05]
    assert work_object.primitive_poses[0].position.x == 0.55
    assert work_object.primitive_poses[0].position.y == 0.0
    assert work_object.primitive_poses[0].position.z == 0.745


def test_all_collision_objects_have_stable_geometry_and_identity_orientation():
    expected = {
        "work_object": ((0.08, 0.08, 0.05), (0.55, 0.0, 0.745)),
    }
    objects = {obj.id: obj for obj in build_collision_objects(frame_id="world")}

    assert set(objects) == set(expected)
    for object_id, (dimensions, xyz) in expected.items():
        obj = objects[object_id]

        assert len(obj.primitives) == 1
        assert len(obj.primitive_poses) == 1
        assert obj.primitives[0].type == SolidPrimitive.BOX
        assert tuple(obj.primitives[0].dimensions) == dimensions
        assert obj.operation == CollisionObject.ADD

        pose = obj.primitive_poses[0]
        assert (pose.position.x, pose.position.y, pose.position.z) == xyz
        assert pose.orientation.x == 0.0
        assert pose.orientation.y == 0.0
        assert pose.orientation.z == 0.0
        assert pose.orientation.w == 1.0


def test_build_collision_objects_defaults_to_world_frame():
    objects = build_collision_objects()

    assert all(obj.header.frame_id == "world" for obj in objects)


def test_validate_publish_period_rejects_non_positive_or_non_finite_values():
    for value in (0.0, -0.1, math.inf, math.nan):
        with pytest.raises(ValueError):
            validate_publish_period(value)


def test_validate_publish_period_accepts_positive_finite_value():
    assert validate_publish_period(2.0) == 2.0


import ast
from pathlib import Path


def _mock_launch_source_tree() -> ast.AST:
    launch_path = Path(__file__).parents[1] / "launch" / "mock.launch.py"
    return ast.parse(launch_path.read_text(encoding="utf-8"))


def test_mock_launch_uses_local_cell_description_xacro():
    tree = _mock_launch_source_tree()
    constants = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }

    assert "crx10ial_cell_description" in constants
    assert "crx10ial_cell.urdf.xacro" in constants


def test_mock_launch_starts_robot_state_publisher_and_fake_gripper():
    tree = _mock_launch_source_tree()
    node_packages = []
    node_executables = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or getattr(node.func, "id", None) != "Node":
            continue
        for keyword in node.keywords:
            if keyword.arg == "package" and isinstance(keyword.value, ast.Constant):
                node_packages.append(keyword.value.value)
            if keyword.arg == "executable" and isinstance(keyword.value, ast.Constant):
                node_executables.append(keyword.value.value)

    assert "robot_state_publisher" in node_packages
    assert "crx10ial_gripper" in node_packages
    assert "fake_gripper" in node_executables
