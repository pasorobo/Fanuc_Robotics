import pytest
from moveit_msgs.msg import CollisionObject

from crx10ial_gripper.fake_gripper import (
    COMMAND_CLOSE,
    COMMAND_OPEN,
    COMMAND_VACUUM_OFF,
    COMMAND_VACUUM_ON,
    FakeGripperBackend,
    GRIPPER_STATE_CLOSED,
    GRIPPER_STATE_HOLDING,
    GRIPPER_STATE_OPEN,
)


def test_command_open_and_close_update_state():
    backend = FakeGripperBackend()

    opened = backend.command(COMMAND_OPEN, width_m=0.08, force_n=0.0)
    assert opened.state == GRIPPER_STATE_OPEN
    assert opened.width_m == 0.08
    assert opened.force_n == 0.0

    closed = backend.command(COMMAND_CLOSE, width_m=0.02, force_n=40.0)
    assert closed.state == GRIPPER_STATE_CLOSED
    assert closed.width_m == 0.02
    assert closed.force_n == 40.0


def test_vacuum_commands_toggle_fake_state():
    backend = FakeGripperBackend()

    state = backend.command(COMMAND_VACUUM_ON, width_m=0.0, force_n=0.0)
    assert state.vacuum_enabled is True

    state = backend.command(COMMAND_VACUUM_OFF, width_m=0.0, force_n=0.0)
    assert state.vacuum_enabled is False


def test_rejects_invalid_width_force_and_command():
    backend = FakeGripperBackend()

    with pytest.raises(ValueError, match="width_m"):
        backend.command(COMMAND_OPEN, width_m=-0.01, force_n=0.0)

    with pytest.raises(ValueError, match="width_m"):
        backend.command(COMMAND_OPEN, width_m=0.20, force_n=0.0)

    with pytest.raises(ValueError, match="force_n"):
        backend.command(COMMAND_CLOSE, width_m=0.02, force_n=-1.0)

    with pytest.raises(ValueError, match="command"):
        backend.command(99, width_m=0.02, force_n=1.0)


def test_attach_scene_diff_removes_world_object_and_attaches_to_grasp_link():
    backend = FakeGripperBackend()

    scene = backend.attach_object("work_object")

    assert backend.state.attached_object_id == "work_object"
    assert backend.state.state == GRIPPER_STATE_HOLDING
    assert scene.is_diff is True
    assert scene.robot_state.is_diff is True
    assert len(scene.world.collision_objects) == 1
    assert scene.world.collision_objects[0].id == "work_object"
    assert scene.world.collision_objects[0].operation == CollisionObject.REMOVE

    attached = scene.robot_state.attached_collision_objects[0]
    assert attached.link_name == "grasp_link"
    assert attached.object.id == "work_object"
    assert attached.object.header.frame_id == "grasp_link"
    assert attached.object.operation == CollisionObject.ADD
    assert set(attached.touch_links) == {
        "end_effector",
        "tool_link",
        "gripper_palm",
        "left_finger",
        "right_finger",
        "grasp_link",
    }


def test_detach_scene_diff_removes_attached_object_and_restores_world_object():
    backend = FakeGripperBackend()
    backend.attach_object("work_object")

    scene = backend.detach_object()

    assert backend.state.attached_object_id == ""
    assert scene.robot_state.attached_collision_objects[0].object.id == "work_object"
    assert scene.robot_state.attached_collision_objects[0].object.operation == CollisionObject.REMOVE

    restored = scene.world.collision_objects[0]
    assert restored.id == "work_object"
    assert restored.header.frame_id == "world"
    assert restored.operation == CollisionObject.ADD
    assert restored.primitive_poses[0].position.x == 0.55
    assert restored.primitive_poses[0].position.y == 0.0
    assert restored.primitive_poses[0].position.z == 0.745


def test_attach_rejects_unknown_or_duplicate_object_and_detach_requires_object():
    backend = FakeGripperBackend()

    with pytest.raises(ValueError, match="unknown object_id"):
        backend.attach_object("missing")

    backend.attach_object("work_object")
    with pytest.raises(ValueError, match="already attached"):
        backend.attach_object("work_object")

    backend.detach_object()
    with pytest.raises(ValueError, match="no object attached"):
        backend.detach_object()
