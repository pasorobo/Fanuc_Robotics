#!/usr/bin/env python3
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

import argparse
import sys

from moveit_msgs.msg import PlanningSceneComponents
from moveit_msgs.srv import GetPlanningScene
import rclpy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-attached", type=int, required=True)
    parser.add_argument("--expected-world", type=int, required=True)
    args = parser.parse_args()

    rclpy.init()
    node = rclpy.create_node("check_single_attached_object")
    client = node.create_client(GetPlanningScene, "/get_planning_scene")
    if not client.wait_for_service(timeout_sec=30.0):
        print("ERROR: /get_planning_scene unavailable", file=sys.stderr)
        node.destroy_node()
        rclpy.shutdown()
        return 1

    request = GetPlanningScene.Request()
    request.components.components = (
        PlanningSceneComponents.WORLD_OBJECT_GEOMETRY
        | PlanningSceneComponents.ROBOT_STATE_ATTACHED_OBJECTS
    )
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future, timeout_sec=30.0)
    if not future.done() or future.result() is None:
        print("ERROR: /get_planning_scene call failed", file=sys.stderr)
        node.destroy_node()
        rclpy.shutdown()
        return 1

    scene = future.result().scene
    attached = [
        obj.object.id
        for obj in scene.robot_state.attached_collision_objects
        if obj.object.id == "work_object"
    ]
    world = [
        obj.id
        for obj in scene.world.collision_objects
        if obj.id == "work_object"
    ]

    print(f"attached_work_object_count={len(attached)}")
    print(f"world_work_object_count={len(world)}")

    node.destroy_node()
    rclpy.shutdown()
    if len(attached) == args.expected_attached and len(world) == args.expected_world:
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
