import threading

import rclpy
from moveit_msgs.srv import ApplyPlanningScene
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from crx10ial_gripper.fake_gripper import FakeGripperBackend
from crx10ial_interfaces.srv import (
    AttachObject,
    CommandGripper,
    DetachObject,
    GetGripperState,
)


class FakeGripperNode(Node):
    def __init__(self, start_apply_scene_client: bool = True) -> None:
        super().__init__("fake_gripper")

        self.declare_parameter("attach_link", "grasp_link")
        self.declare_parameter("world_frame", "world")

        self.backend = FakeGripperBackend(
            attach_link=str(self.get_parameter("attach_link").value),
            world_frame=str(self.get_parameter("world_frame").value),
        )
        self._callback_group = ReentrantCallbackGroup()

        self._apply_scene_client = None
        if start_apply_scene_client:
            self._apply_scene_client = self.create_client(
                ApplyPlanningScene,
                "/apply_planning_scene",
                callback_group=self._callback_group,
            )

        self.create_service(
            CommandGripper,
            "command",
            self.handle_command,
            callback_group=self._callback_group,
        )
        self.create_service(
            AttachObject,
            "attach_object",
            self.handle_attach_object,
            callback_group=self._callback_group,
        )
        self.create_service(
            DetachObject,
            "detach_object",
            self.handle_detach_object,
            callback_group=self._callback_group,
        )
        self.create_service(
            GetGripperState,
            "get_state",
            self.handle_get_state,
            callback_group=self._callback_group,
        )

    def handle_command(
        self,
        request: CommandGripper.Request,
        response: CommandGripper.Response,
    ) -> CommandGripper.Response:
        try:
            state = self.backend.command(request.command, request.width_m, request.force_n)
        except ValueError as exc:
            response.success = False
            response.message = str(exc)
            self._copy_state(response)
            return response

        response.success = True
        response.message = "ok"
        self._copy_state(response, state)
        return response

    def handle_attach_object(
        self,
        request: AttachObject.Request,
        response: AttachObject.Response,
    ) -> AttachObject.Response:
        try:
            scene = self.backend.attach_object(request.object_id)
            self.apply_scene(scene)
        except (RuntimeError, ValueError) as exc:
            response.success = False
            response.message = str(exc)
            response.attached_object_id = self.backend.state.attached_object_id
            return response

        response.success = True
        response.message = "ok"
        response.attached_object_id = self.backend.state.attached_object_id
        return response

    def handle_detach_object(
        self,
        request: DetachObject.Request,
        response: DetachObject.Response,
    ) -> DetachObject.Response:
        del request
        detached_object_id = self.backend.state.attached_object_id
        try:
            scene = self.backend.detach_object()
            self.apply_scene(scene)
        except (RuntimeError, ValueError) as exc:
            response.success = False
            response.message = str(exc)
            response.detached_object_id = ""
            return response

        response.success = True
        response.message = "ok"
        response.detached_object_id = detached_object_id
        return response

    def handle_get_state(
        self,
        request: GetGripperState.Request,
        response: GetGripperState.Response,
    ) -> GetGripperState.Response:
        del request
        state = self.backend.state
        response.state = state.state
        response.width_m = state.width_m
        response.force_n = state.force_n
        response.attached_object_id = state.attached_object_id
        response.vacuum_enabled = state.vacuum_enabled
        return response

    def apply_scene(self, scene) -> None:
        if self._apply_scene_client is None:
            return

        if not self._apply_scene_client.wait_for_service(timeout_sec=5.0):
            raise RuntimeError("/apply_planning_scene service is not available")

        request = ApplyPlanningScene.Request()
        request.scene = scene
        future = self._apply_scene_client.call_async(request)
        finished = threading.Event()
        future.add_done_callback(lambda _: finished.set())

        if not finished.wait(timeout=10.0):
            raise RuntimeError("/apply_planning_scene call timed out")

        result = future.result()
        if result is None or not result.success:
            raise RuntimeError("/apply_planning_scene returned failure")

    def _copy_state(self, response, state=None) -> None:
        current = state if state is not None else self.backend.state
        response.state = current.state
        response.width_m = current.width_m
        response.force_n = current.force_n
        response.attached_object_id = current.attached_object_id
        response.vacuum_enabled = current.vacuum_enabled


def main() -> None:
    rclpy.init()
    node = FakeGripperNode()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
