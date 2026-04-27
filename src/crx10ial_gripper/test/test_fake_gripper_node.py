import rclpy

from crx10ial_gripper.fake_gripper import (
    COMMAND_CLOSE,
    GRIPPER_STATE_CLOSED,
    GRIPPER_STATE_HOLDING,
)
from crx10ial_gripper.fake_gripper_node import FakeGripperNode
from crx10ial_interfaces.srv import AttachObject, CommandGripper, DetachObject, GetGripperState


def _init_rclpy():
    if not rclpy.ok():
        rclpy.init()


def test_command_callback_maps_request_to_backend_state():
    _init_rclpy()
    node = FakeGripperNode(start_apply_scene_client=False)
    try:
        request = CommandGripper.Request()
        request.command = COMMAND_CLOSE
        request.width_m = 0.02
        request.force_n = 30.0
        response = node.handle_command(request, CommandGripper.Response())

        assert response.success is True
        assert response.state == GRIPPER_STATE_CLOSED
        assert response.width_m == 0.02
        assert response.force_n == 30.0
        assert response.attached_object_id == ""
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_attach_and_detach_callbacks_apply_scene_and_update_state():
    _init_rclpy()
    node = FakeGripperNode(start_apply_scene_client=False)
    applied_scenes = []
    node.apply_scene = applied_scenes.append
    try:
        attach_request = AttachObject.Request()
        attach_request.object_id = "work_object"
        attach_response = node.handle_attach_object(
            attach_request,
            AttachObject.Response(),
        )

        assert attach_response.success is True
        assert attach_response.attached_object_id == "work_object"
        assert node.backend.state.state == GRIPPER_STATE_HOLDING
        assert len(applied_scenes) == 1

        state_response = node.handle_get_state(
            GetGripperState.Request(),
            GetGripperState.Response(),
        )
        assert state_response.attached_object_id == "work_object"

        detach_response = node.handle_detach_object(
            DetachObject.Request(),
            DetachObject.Response(),
        )
        assert detach_response.success is True
        assert detach_response.detached_object_id == "work_object"
        assert node.backend.state.attached_object_id == ""
        assert len(applied_scenes) == 2
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_attach_callback_returns_failure_for_unknown_object():
    _init_rclpy()
    node = FakeGripperNode(start_apply_scene_client=False)
    try:
        request = AttachObject.Request()
        request.object_id = "missing"
        response = node.handle_attach_object(request, AttachObject.Response())

        assert response.success is False
        assert "unknown object_id" in response.message
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_attach_callback_rolls_back_state_when_apply_scene_fails():
    _init_rclpy()
    node = FakeGripperNode(start_apply_scene_client=False)

    def fail_apply_scene(scene):
        raise RuntimeError("apply failed")

    node.apply_scene = fail_apply_scene
    try:
        request = AttachObject.Request()
        request.object_id = "work_object"
        response = node.handle_attach_object(request, AttachObject.Response())

        assert response.success is False
        assert "apply failed" in response.message
        assert response.attached_object_id == ""
        assert node.backend.state.attached_object_id == ""
    finally:
        node.destroy_node()
        rclpy.shutdown()
