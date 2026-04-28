// Copyright 2026 Fanuc Robotics Maintainers
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once

#include <moveit/task_constructor/task.h>

#include <cstddef>
#include <string>

#include <crx10ial_tasks/fixed_pick_place_config.hpp>
#include <rclcpp/node.hpp>

namespace crx10ial_tasks
{

struct FixedPickPlaceResult
{
  bool success;
  std::string diagnostics;
  std::size_t solution_count;
};

moveit::task_constructor::Task build_fixed_pick_place_task(
  const rclcpp::Node::SharedPtr & node,
  const FixedPickPlaceConfig & config,
  const geometry_msgs::msg::Pose & place_pose);

FixedPickPlaceResult plan_fixed_pick_place(
  const rclcpp::Node::SharedPtr & node,
  const FixedPickPlaceConfig & config,
  bool use_failure_place);

}  // namespace crx10ial_tasks
