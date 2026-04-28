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

import yaml


def _config_path() -> Path:
    return Path(__file__).resolve().parents[1] / "config" / "fixed_pick_place.yaml"


def _params():
    data = yaml.safe_load(_config_path().read_text(encoding="utf-8"))
    return data["fixed_pick_place"]["ros__parameters"]


def test_fixed_pick_place_yaml_has_required_sections():
    params = _params()

    assert params["object.id"] == "work_object"
    assert params["object.frame_id"] == "world"
    assert params["grasp.frame_id"] == "grasp_link"
    assert params["place.frame_id"] == "world"
    assert params["gripper.open_width_m"] == 0.08
    assert params["gripper.close_width_m"] == 0.02
    assert params["gripper.close_force_n"] == 30.0


def test_pose_and_vector_lengths_are_fixed():
    params = _params()

    for key in [
        "object.pose.xyz",
        "object.pose.rpy",
        "grasp.pose.xyz",
        "grasp.pose.rpy",
        "grasp.approach.direction",
        "grasp.retreat.direction",
        "place.pose.xyz",
        "place.pose.rpy",
        "failure.place.pose.xyz",
        "failure.place.pose.rpy",
    ]:
        assert len(params[key]) == 3


def test_grasp_distances_are_positive_and_ordered():
    params = _params()

    assert 0.0 < params["grasp.approach.min"] <= params["grasp.approach.max"]
    assert 0.0 < params["grasp.retreat.min"] <= params["grasp.retreat.max"]
    assert params["failure.place.pose.xyz"][0] >= 2.0
