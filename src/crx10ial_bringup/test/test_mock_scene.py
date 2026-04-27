from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive

import math

import pytest

from crx10ial_bringup.mock_scene import build_collision_objects
from crx10ial_bringup.mock_scene_node import validate_publish_period


def test_build_collision_objects_returns_expected_ids_and_frame():
    objects = build_collision_objects(frame_id="world")

    assert [obj.id for obj in objects] == [
        "work_table",
        "work_object",
        "camera_stand",
    ]
    assert all(obj.header.frame_id == "world" for obj in objects)
    assert all(obj.operation == CollisionObject.ADD for obj in objects)


def test_work_table_dimensions_are_stable():
    objects = {obj.id: obj for obj in build_collision_objects(frame_id="world")}
    table = objects["work_table"]

    assert table.primitives[0].type == SolidPrimitive.BOX
    assert list(table.primitives[0].dimensions) == [1.0, 0.7, 0.04]
    assert table.primitive_poses[0].position.x == 0.75
    assert table.primitive_poses[0].position.y == 0.0
    assert table.primitive_poses[0].position.z == 0.70


def test_all_collision_objects_have_stable_geometry_and_identity_orientation():
    expected = {
        "work_table": ((1.0, 0.7, 0.04), (0.75, 0.0, 0.70)),
        "work_object": ((0.08, 0.08, 0.05), (0.55, 0.0, 0.745)),
        "camera_stand": ((0.05, 0.05, 0.70), (0.35, -0.55, 0.35)),
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
