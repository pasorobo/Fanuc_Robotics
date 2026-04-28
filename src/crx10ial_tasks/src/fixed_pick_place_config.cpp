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

#include <crx10ial_tasks/fixed_pick_place_config.hpp>

#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Transform.h>

#include <stdexcept>
#include <vector>

#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

namespace crx10ial_tasks
{
namespace
{

std::vector<double> declare_double_array(rclcpp::Node & node, const std::string & name)
{
  node.declare_parameter<std::vector<double>>(name);
  auto values = node.get_parameter(name).as_double_array();
  if (values.size() != 3) {
    throw std::runtime_error(name + " must contain exactly 3 values");
  }
  return values;
}

std::array<double, 3> to_array3(const std::vector<double> & values)
{
  return {values[0], values[1], values[2]};
}

geometry_msgs::msg::Pose pose_from_parameters(
  rclcpp::Node & node,
  const std::string & prefix)
{
  const auto xyz = declare_double_array(node, prefix + ".xyz");
  const auto rpy = declare_double_array(node, prefix + ".rpy");

  tf2::Quaternion q;
  q.setRPY(rpy[0], rpy[1], rpy[2]);
  q.normalize();

  geometry_msgs::msg::Pose pose;
  pose.position.x = xyz[0];
  pose.position.y = xyz[1];
  pose.position.z = xyz[2];
  pose.orientation = tf2::toMsg(q);
  return pose;
}

geometry_msgs::msg::Vector3 vector_from_parameters(
  rclcpp::Node & node,
  const std::string & name)
{
  const auto values = declare_double_array(node, name);
  geometry_msgs::msg::Vector3 vector;
  vector.x = values[0];
  vector.y = values[1];
  vector.z = values[2];
  return vector;
}

double positive_double(rclcpp::Node & node, const std::string & name)
{
  node.declare_parameter<double>(name);
  const double value = node.get_parameter(name).as_double();
  if (value <= 0.0) {
    throw std::runtime_error(name + " must be positive");
  }
  return value;
}

}  // namespace

FixedPickPlaceConfig load_fixed_pick_place_config(rclcpp::Node & node)
{
  FixedPickPlaceConfig config;

  config.arm_group_name = node.declare_parameter<std::string>("arm_group_name");
  config.eef_name = node.declare_parameter<std::string>("eef_name");
  config.hand_frame = node.declare_parameter<std::string>("hand_frame");
  config.world_frame = node.declare_parameter<std::string>("world_frame");

  config.object.id = node.declare_parameter<std::string>("object.id");
  config.object.frame_id = node.declare_parameter<std::string>("object.frame_id");
  config.object.dimensions = to_array3(declare_double_array(node, "object.dimensions"));
  config.object.pose = pose_from_parameters(node, "object.pose");

  config.grasp.frame_id = node.declare_parameter<std::string>("grasp.frame_id");
  config.grasp.pose = pose_from_parameters(node, "grasp.pose");
  config.grasp.approach.direction =
    vector_from_parameters(node, "grasp.approach.direction");
  config.grasp.approach.min_distance =
    positive_double(node, "grasp.approach.min");
  config.grasp.approach.max_distance =
    positive_double(node, "grasp.approach.max");
  config.grasp.retreat.direction =
    vector_from_parameters(node, "grasp.retreat.direction");
  config.grasp.retreat.min_distance =
    positive_double(node, "grasp.retreat.min");
  config.grasp.retreat.max_distance =
    positive_double(node, "grasp.retreat.max");

  if (config.grasp.approach.min_distance > config.grasp.approach.max_distance) {
    throw std::runtime_error("grasp.approach.min must be <= grasp.approach.max");
  }
  if (config.grasp.retreat.min_distance > config.grasp.retreat.max_distance) {
    throw std::runtime_error("grasp.retreat.min must be <= grasp.retreat.max");
  }

  config.place.frame_id = node.declare_parameter<std::string>("place.frame_id");
  config.place.pose = pose_from_parameters(node, "place.pose");
  config.failure_place.frame_id = config.place.frame_id;
  config.failure_place.pose = pose_from_parameters(node, "failure.place.pose");

  config.gripper.open_width_m = positive_double(node, "gripper.open_width_m");
  config.gripper.close_width_m = positive_double(node, "gripper.close_width_m");
  config.gripper.close_force_n = positive_double(node, "gripper.close_force_n");

  node.declare_parameter<int>("planning.max_solutions");
  const int max_solutions = node.get_parameter("planning.max_solutions").as_int();
  if (max_solutions <= 0) {
    throw std::runtime_error("planning.max_solutions must be positive");
  }
  config.planning.max_solutions = static_cast<std::size_t>(max_solutions);
  config.planning.timeout_sec = positive_double(node, "planning.timeout_sec");
  config.execution_enabled = node.declare_parameter<bool>("execution.enabled");

  return config;
}

geometry_msgs::msg::Pose compose_pose(
  const geometry_msgs::msg::Pose & base,
  const geometry_msgs::msg::Pose & offset)
{
  tf2::Transform base_tf;
  tf2::Transform offset_tf;
  tf2::fromMsg(base, base_tf);
  tf2::fromMsg(offset, offset_tf);
  const tf2::Transform composed = base_tf * offset_tf;

  geometry_msgs::msg::Pose pose;
  pose.position.x = composed.getOrigin().x();
  pose.position.y = composed.getOrigin().y();
  pose.position.z = composed.getOrigin().z();
  pose.orientation = tf2::toMsg(composed.getRotation());
  return pose;
}

}  // namespace crx10ial_tasks
