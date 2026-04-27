import math

import rclpy
from moveit_msgs.msg import CollisionObject
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from crx10ial_bringup.mock_scene import build_collision_objects


def validate_publish_period(value: float) -> float:
    period = float(value)
    if not math.isfinite(period) or period <= 0.0:
        raise ValueError("publish_period_sec must be a positive finite value")
    return period


class MockScenePublisher(Node):
    def __init__(self) -> None:
        super().__init__("mock_scene_publisher")

        self.declare_parameter("frame_id", "world")
        self.declare_parameter("publish_period_sec", 2.0)

        qos = QoSProfile(depth=10)
        qos.reliability = ReliabilityPolicy.RELIABLE
        qos.durability = DurabilityPolicy.TRANSIENT_LOCAL

        self._publisher = self.create_publisher(CollisionObject, "/collision_object", qos)
        period = validate_publish_period(self.get_parameter("publish_period_sec").value)
        self._timer = self.create_timer(period, self.publish_scene)
        self.publish_scene()

    def publish_scene(self) -> None:
        frame_id = str(self.get_parameter("frame_id").value)
        for obj in build_collision_objects(frame_id=frame_id):
            self._publisher.publish(obj)
            self.get_logger().debug(
                f"Published collision object '{obj.id}' in frame '{frame_id}'"
            )


def main() -> None:
    rclpy.init()
    node = MockScenePublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
