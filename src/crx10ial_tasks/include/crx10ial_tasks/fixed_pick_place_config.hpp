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

#include <array>
#include <cstddef>
#include <string>

#include <geometry_msgs/msg/pose.hpp>
#include <geometry_msgs/msg/vector3.hpp>
#include <rclcpp/node.hpp>

namespace crx10ial_tasks
{

struct ObjectConfig
{
  std::string id;
  std::string frame_id;
  std::array<double, 3> dimensions;
  geometry_msgs::msg::Pose pose;
};

struct ApproachConfig
{
  geometry_msgs::msg::Vector3 direction;
  double min_distance;
  double max_distance;
};

struct GraspConfig
{
  std::string frame_id;
  geometry_msgs::msg::Pose pose;
  ApproachConfig approach;
  ApproachConfig retreat;
};

struct PlaceConfig
{
  std::string frame_id;
  geometry_msgs::msg::Pose pose;
};

struct GripperConfig
{
  double open_width_m;
  double close_width_m;
  double close_force_n;
};

struct PlanningConfig
{
  std::size_t max_solutions;
  double timeout_sec;
};

struct FixedPickPlaceConfig
{
  std::string arm_group_name;
  std::string eef_name;
  std::string hand_frame;
  std::string world_frame;
  ObjectConfig object;
  GraspConfig grasp;
  PlaceConfig place;
  PlaceConfig failure_place;
  GripperConfig gripper;
  PlanningConfig planning;
  bool execution_enabled;
};

FixedPickPlaceConfig load_fixed_pick_place_config(rclcpp::Node & node);
geometry_msgs::msg::Pose compose_pose(
  const geometry_msgs::msg::Pose & base,
  const geometry_msgs::msg::Pose & offset);

}  // namespace crx10ial_tasks
