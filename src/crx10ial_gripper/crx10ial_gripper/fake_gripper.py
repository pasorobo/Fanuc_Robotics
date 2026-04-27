from dataclasses import dataclass
from typing import Dict, Sequence

from geometry_msgs.msg import Pose
from moveit_msgs.msg import AttachedCollisionObject, CollisionObject, PlanningScene
from shape_msgs.msg import SolidPrimitive


COMMAND_OPEN = 1
COMMAND_CLOSE = 2
COMMAND_VACUUM_ON = 3
COMMAND_VACUUM_OFF = 4

GRIPPER_STATE_IDLE = 0
GRIPPER_STATE_OPEN = 1
GRIPPER_STATE_CLOSED = 2
GRIPPER_STATE_HOLDING = 3

MAX_WIDTH_M = 0.12


@dataclass(frozen=True)
class ObjectSpec:
    object_id: str
    dimensions: tuple[float, float, float]
    world_xyz: tuple[float, float, float]


@dataclass
class GripperState:
    state: int = GRIPPER_STATE_IDLE
    width_m: float = MAX_WIDTH_M
    force_n: float = 0.0
    attached_object_id: str = ""
    vacuum_enabled: bool = False


WORK_OBJECT = ObjectSpec(
    object_id="work_object",
    dimensions=(0.08, 0.08, 0.05),
    world_xyz=(0.55, 0.0, 0.745),
)


def _identity_pose(x: float, y: float, z: float) -> Pose:
    pose = Pose()
    pose.position.x = x
    pose.position.y = y
    pose.position.z = z
    pose.orientation.w = 1.0
    return pose


def _box_primitive(dimensions: Sequence[float]) -> SolidPrimitive:
    primitive = SolidPrimitive()
    primitive.type = SolidPrimitive.BOX
    primitive.dimensions = list(dimensions)
    return primitive


def _collision_object_add(spec: ObjectSpec, frame_id: str, pose: Pose) -> CollisionObject:
    obj = CollisionObject()
    obj.header.frame_id = frame_id
    obj.id = spec.object_id
    obj.primitives.append(_box_primitive(spec.dimensions))
    obj.primitive_poses.append(pose)
    obj.operation = CollisionObject.ADD
    return obj


def _collision_object_remove(object_id: str, frame_id: str) -> CollisionObject:
    obj = CollisionObject()
    obj.header.frame_id = frame_id
    obj.id = object_id
    obj.operation = CollisionObject.REMOVE
    return obj


class FakeGripperBackend:
    def __init__(
        self,
        attach_link: str = "grasp_link",
        world_frame: str = "world",
        touch_links: Sequence[str] | None = None,
        object_specs: Sequence[ObjectSpec] = (WORK_OBJECT,),
    ) -> None:
        self.attach_link = attach_link
        self.world_frame = world_frame
        self.touch_links = list(
            touch_links
            if touch_links is not None
            else (
                "end_effector",
                "tool_link",
                "gripper_palm",
                "left_finger",
                "right_finger",
                "grasp_link",
            )
        )
        self.object_specs: Dict[str, ObjectSpec] = {
            spec.object_id: spec for spec in object_specs
        }
        self.state = GripperState()

    def command(self, command: int, width_m: float, force_n: float) -> GripperState:
        self._validate_width(width_m)
        self._validate_force(force_n)

        if command == COMMAND_OPEN:
            self.state.state = GRIPPER_STATE_OPEN
            self.state.width_m = width_m
            self.state.force_n = force_n
        elif command == COMMAND_CLOSE:
            self.state.state = GRIPPER_STATE_CLOSED
            self.state.width_m = width_m
            self.state.force_n = force_n
        elif command == COMMAND_VACUUM_ON:
            self.state.vacuum_enabled = True
        elif command == COMMAND_VACUUM_OFF:
            self.state.vacuum_enabled = False
        else:
            raise ValueError(f"unsupported command: {command}")

        return self.state

    def attach_object(self, object_id: str) -> PlanningScene:
        if object_id not in self.object_specs:
            raise ValueError(f"unknown object_id: {object_id}")
        if self.state.attached_object_id:
            raise ValueError(f"object already attached: {self.state.attached_object_id}")

        spec = self.object_specs[object_id]
        scene = PlanningScene()
        scene.is_diff = True
        scene.robot_state.is_diff = True

        scene.world.collision_objects.append(
            _collision_object_remove(spec.object_id, self.world_frame)
        )

        attached = AttachedCollisionObject()
        attached.link_name = self.attach_link
        attached.touch_links = list(self.touch_links)
        attached.object = _collision_object_add(
            spec,
            self.attach_link,
            _identity_pose(0.0, 0.0, 0.0),
        )
        scene.robot_state.attached_collision_objects.append(attached)

        self.state.attached_object_id = object_id
        self.state.state = GRIPPER_STATE_HOLDING
        return scene

    def detach_object(self) -> PlanningScene:
        if not self.state.attached_object_id:
            raise ValueError("no object attached")

        object_id = self.state.attached_object_id
        spec = self.object_specs[object_id]

        scene = PlanningScene()
        scene.is_diff = True
        scene.robot_state.is_diff = True

        attached_remove = AttachedCollisionObject()
        attached_remove.link_name = self.attach_link
        attached_remove.object.id = object_id
        attached_remove.object.operation = CollisionObject.REMOVE
        scene.robot_state.attached_collision_objects.append(attached_remove)

        scene.world.collision_objects.append(
            _collision_object_add(
                spec,
                self.world_frame,
                _identity_pose(*spec.world_xyz),
            )
        )

        self.state.attached_object_id = ""
        if self.state.state == GRIPPER_STATE_HOLDING:
            self.state.state = GRIPPER_STATE_OPEN
        return scene

    @staticmethod
    def _validate_width(width_m: float) -> None:
        if width_m < 0.0 or width_m > MAX_WIDTH_M:
            raise ValueError(f"width_m must be between 0.0 and {MAX_WIDTH_M}")

    @staticmethod
    def _validate_force(force_n: float) -> None:
        if force_n < 0.0:
            raise ValueError("force_n must be non-negative")
