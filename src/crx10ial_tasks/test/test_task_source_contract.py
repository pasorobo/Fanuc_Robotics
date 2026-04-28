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

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_mtc_task_uses_internal_attach_and_detach_stages():
    source = _read("src/fixed_pick_place_task.cpp")

    assert 'ModifyPlanningScene>("internal attach object"' in source
    assert "->attachObject(config.object.id, config.hand_frame)" in source
    assert 'ModifyPlanningScene>("internal detach object"' in source
    assert "->detachObject(config.object.id, config.hand_frame)" in source


def test_m3_does_not_call_mtc_task_execute():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "src" / "fixed_pick_place_task.cpp",
            ROOT / "src" / "fixed_pick_place_node.cpp",
        ]
        if path.exists()
    )

    assert ".execute(" not in combined
    assert "execute_task_solution" not in combined


def test_mtc_failure_diagnostics_are_reported():
    source = _read("src/fixed_pick_place_task.cpp")

    assert "task.explainFailure" in source
    assert "task.printState" in source
    assert "solutions().empty()" in source


def test_mtc_moves_to_pregrasp_before_approach():
    source = _read("src/fixed_pick_place_task.cpp")

    assert 'MoveTo>("move to pregrasp pose"' in source
    assert "const auto pregrasp_pose = translated_pose(" in source
    assert "stage->setGoal(stamped_pose(config.object.frame_id, pregrasp_pose));" in source


def test_execute_mock_attaches_before_grasp_motion_when_node_exists():
    node_path = ROOT / "src" / "fixed_pick_place_node.cpp"
    if not node_path.exists():
        return

    source = node_path.read_text(encoding="utf-8")
    if '"execute_mock"' not in source:
        return

    attach_index = source.index("attach_object(node, config);")
    grasp_index = source.index(
        'move_to_pose(move_group, grasp_world_pose, config.hand_frame, "grasp");'
    )

    assert attach_index < grasp_index
