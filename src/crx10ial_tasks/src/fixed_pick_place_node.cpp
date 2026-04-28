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

#include <moveit/move_group_interface/move_group_interface.h>

#include <chrono>
#include <future>
#include <memory>
#include <stdexcept>
#include <string>
#include <thread>

#include <crx10ial_interfaces/srv/attach_object.hpp>
#include <crx10ial_interfaces/srv/command_gripper.hpp>
#include <crx10ial_interfaces/srv/detach_object.hpp>
#include <crx10ial_tasks/fixed_pick_place_config.hpp>
#include <crx10ial_tasks/fixed_pick_place_task.hpp>
#include <moveit_msgs/msg/move_it_error_codes.hpp>
#include <moveit_msgs/msg/planning_scene_components.hpp>
#include <moveit_msgs/srv/get_planning_scene.hpp>
#include <rclcpp/rclcpp.hpp>

namespace
{
using namespace std::chrono_literals;

template<typename ServiceT>
typename ServiceT::Response::SharedPtr call_service(
  const rclcpp::Node::SharedPtr & node,
  const std::string & service_name,
  const typename ServiceT::Request::SharedPtr & request,
  std::chrono::seconds timeout = 30s)
{
  auto client = node->create_client<ServiceT>(service_name);
  if (!client->wait_for_service(timeout)) {
    throw std::runtime_error(service_name + " is not available");
  }

  auto future = client->async_send_request(request);
  if (future.wait_for(timeout) != std::future_status::ready) {
    throw std::runtime_error(service_name + " call timed out");
  }
  return future.get();
}

geometry_msgs::msg::Pose translated_pose(
  geometry_msgs::msg::Pose pose,
  const geometry_msgs::msg::Vector3 & direction,
  double distance)
{
  pose.position.x += direction.x * distance;
  pose.position.y += direction.y * distance;
  pose.position.z += direction.z * distance;
  return pose;
}

void move_to_pose(
  moveit::planning_interface::MoveGroupInterface & move_group,
  const geometry_msgs::msg::Pose & pose,
  const std::string & link_name,
  const std::string & label)
{
  move_group.setStartStateToCurrentState();
  move_group.setPoseTarget(pose, link_name);
  const auto result = move_group.move();
  move_group.clearPoseTargets();
  if (result.val != moveit_msgs::msg::MoveItErrorCodes::SUCCESS) {
    throw std::runtime_error(
            label + " motion failed with code " + std::to_string(result.val));
  }
}

void command_gripper(
  const rclcpp::Node::SharedPtr & node,
  const crx10ial_tasks::FixedPickPlaceConfig & config,
  int command)
{
  auto request = std::make_shared<crx10ial_interfaces::srv::CommandGripper::Request>();
  request->command = command;
  if (command == crx10ial_interfaces::srv::CommandGripper::Request::OPEN) {
    request->width_m = config.gripper.open_width_m;
    request->force_n = 0.0;
  } else {
    request->width_m = config.gripper.close_width_m;
    request->force_n = config.gripper.close_force_n;
  }

  const auto response = call_service<crx10ial_interfaces::srv::CommandGripper>(
    node,
    "/crx10ial_gripper/command",
    request);
  if (!response->success) {
    throw std::runtime_error("gripper command failed: " + response->message);
  }
}

void attach_object(
  const rclcpp::Node::SharedPtr & node,
  const crx10ial_tasks::FixedPickPlaceConfig & config)
{
  auto request = std::make_shared<crx10ial_interfaces::srv::AttachObject::Request>();
  request->object_id = config.object.id;

  const auto response = call_service<crx10ial_interfaces::srv::AttachObject>(
    node,
    "/crx10ial_gripper/attach_object",
    request);
  if (!response->success || response->attached_object_id != config.object.id) {
    throw std::runtime_error("attach failed: " + response->message);
  }
}

void detach_object(const rclcpp::Node::SharedPtr & node)
{
  auto request = std::make_shared<crx10ial_interfaces::srv::DetachObject::Request>();

  const auto response = call_service<crx10ial_interfaces::srv::DetachObject>(
    node,
    "/crx10ial_gripper/detach_object",
    request);
  if (!response->success || response->detached_object_id != "work_object") {
    throw std::runtime_error("detach failed: " + response->message);
  }
}

void verify_single_runtime_attachment(
  const rclcpp::Node::SharedPtr & node,
  const std::string & object_id)
{
  auto request = std::make_shared<moveit_msgs::srv::GetPlanningScene::Request>();
  request->components.components =
    moveit_msgs::msg::PlanningSceneComponents::WORLD_OBJECT_GEOMETRY |
    moveit_msgs::msg::PlanningSceneComponents::ROBOT_STATE_ATTACHED_OBJECTS;

  const auto response = call_service<moveit_msgs::srv::GetPlanningScene>(
    node,
    "/get_planning_scene",
    request);

  std::size_t attached_count = 0;
  for (const auto & attached : response->scene.robot_state.attached_collision_objects) {
    if (attached.object.id == object_id) {
      ++attached_count;
    }
  }

  std::size_t world_count = 0;
  for (const auto & object : response->scene.world.collision_objects) {
    if (object.id == object_id) {
      ++world_count;
    }
  }

  if (attached_count != 1 || world_count != 0) {
    throw std::runtime_error(
            "expected one attached object and zero world duplicates for " + object_id);
  }
}

int run_plan_mode(
  const rclcpp::Node::SharedPtr & node,
  const crx10ial_tasks::FixedPickPlaceConfig & config,
  bool negative)
{
  const auto result = crx10ial_tasks::plan_fixed_pick_place(node, config, negative);
  RCLCPP_INFO_STREAM(node->get_logger(), result.diagnostics);

  if (negative) {
    if (result.success || result.diagnostics.empty()) {
      RCLCPP_ERROR(
        node->get_logger(),
        "M3 negative planning was expected to fail with diagnostics");
      return 3;
    }
    RCLCPP_INFO(node->get_logger(), "M3 negative planning produced diagnostics");
    return 0;
  }

  if (!result.success) {
    RCLCPP_ERROR(node->get_logger(), "M3 fixed pick/place planning failed");
    return 2;
  }

  RCLCPP_INFO(
    node->get_logger(),
    "M3 fixed pick/place planning succeeded with %zu solution(s)",
    result.solution_count);
  return 0;
}

int run_execute_mock(
  const rclcpp::Node::SharedPtr & node,
  const crx10ial_tasks::FixedPickPlaceConfig & config)
{
  const int plan_code = run_plan_mode(node, config, false);
  if (plan_code != 0) {
    return plan_code;
  }

  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);
  std::thread spinner([&executor]() {executor.spin();});

  try {
    moveit::planning_interface::MoveGroupInterface move_group(node, config.arm_group_name);
    move_group.setPlanningTime(config.planning.timeout_sec);
    move_group.setMaxVelocityScalingFactor(0.2);
    move_group.setMaxAccelerationScalingFactor(0.2);

    const auto grasp_world_pose =
      crx10ial_tasks::compose_pose(config.object.pose, config.grasp.pose);
    const auto pregrasp_pose = translated_pose(
      grasp_world_pose,
      config.grasp.approach.direction,
      -config.grasp.approach.max_distance);
    const auto retreat_pose = translated_pose(
      grasp_world_pose,
      config.grasp.retreat.direction,
      config.grasp.retreat.max_distance);
    const auto post_place_pose = translated_pose(
      config.place.pose,
      config.grasp.retreat.direction,
      config.grasp.retreat.max_distance);

    command_gripper(
      node,
      config,
      crx10ial_interfaces::srv::CommandGripper::Request::OPEN);
    move_to_pose(move_group, pregrasp_pose, config.hand_frame, "pregrasp");
    command_gripper(
      node,
      config,
      crx10ial_interfaces::srv::CommandGripper::Request::CLOSE);
    attach_object(node, config);
    verify_single_runtime_attachment(node, config.object.id);
    RCLCPP_INFO(node->get_logger(), "M3 single attached object verified");
    move_to_pose(move_group, grasp_world_pose, config.hand_frame, "grasp");
    move_to_pose(move_group, retreat_pose, config.hand_frame, "retreat");
    move_to_pose(move_group, config.place.pose, config.hand_frame, "place");
    detach_object(node);
    move_to_pose(move_group, post_place_pose, config.hand_frame, "post place retreat");
    RCLCPP_INFO(node->get_logger(), "M3 mock pick/place execution succeeded");
  } catch (...) {
    executor.cancel();
    if (spinner.joinable()) {
      spinner.join();
    }
    throw;
  }

  executor.cancel();
  if (spinner.joinable()) {
    spinner.join();
  }
  return 0;
}

}  // namespace

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("fixed_pick_place");

  try {
    const auto mode = node->declare_parameter<std::string>("run_mode", "plan");
    const auto config = crx10ial_tasks::load_fixed_pick_place_config(*node);

    int exit_code = 0;
    if (mode == "plan") {
      exit_code = run_plan_mode(node, config, false);
    } else if (mode == "negative_plan") {
      exit_code = run_plan_mode(node, config, true);
    } else if (mode == "execute_mock") {
      exit_code = run_execute_mock(node, config);
    } else {
      RCLCPP_ERROR(node->get_logger(), "unsupported run_mode: %s", mode.c_str());
      exit_code = 4;
    }

    rclcpp::shutdown();
    return exit_code;
  } catch (const std::exception & exc) {
    RCLCPP_ERROR(node->get_logger(), "fixed pick/place failed: %s", exc.what());
    rclcpp::shutdown();
    return 1;
  }
}
