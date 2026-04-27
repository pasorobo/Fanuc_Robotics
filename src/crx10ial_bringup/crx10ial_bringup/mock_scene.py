from dataclasses import dataclass
from typing import Iterable, List

from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive


@dataclass(frozen=True)
class BoxSpec:
    object_id: str
    dimensions: tuple[float, float, float]
    xyz: tuple[float, float, float]


SCENE_BOXES: tuple[BoxSpec, ...] = (
    BoxSpec(
        object_id="work_table",
        dimensions=(1.0, 0.7, 0.04),
        xyz=(0.75, 0.0, 0.70),
    ),
    BoxSpec(
        object_id="work_object",
        dimensions=(0.08, 0.08, 0.05),
        xyz=(0.55, 0.0, 0.745),
    ),
    BoxSpec(
        object_id="camera_stand",
        dimensions=(0.05, 0.05, 0.70),
        xyz=(0.35, -0.55, 0.35),
    ),
)


def _identity_pose(x: float, y: float, z: float) -> Pose:
    pose = Pose()
    pose.position.x = x
    pose.position.y = y
    pose.position.z = z
    pose.orientation.w = 1.0
    return pose


def build_collision_object(spec: BoxSpec, frame_id: str) -> CollisionObject:
    primitive = SolidPrimitive()
    primitive.type = SolidPrimitive.BOX
    primitive.dimensions = list(spec.dimensions)

    obj = CollisionObject()
    obj.header.frame_id = frame_id
    obj.id = spec.object_id
    obj.primitives.append(primitive)
    obj.primitive_poses.append(_identity_pose(*spec.xyz))
    obj.operation = CollisionObject.ADD
    return obj


def build_collision_objects(frame_id: str = "world") -> List[CollisionObject]:
    return [build_collision_object(spec, frame_id) for spec in SCENE_BOXES]


def iter_collision_objects(frame_id: str = "world") -> Iterable[CollisionObject]:
    return iter(build_collision_objects(frame_id=frame_id))
