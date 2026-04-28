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

#include <crx10ial_tasks/fixed_pick_place_task.hpp>

#include <moveit/task_constructor/container.h>
#include <moveit/task_constructor/solvers/cartesian_path.h>
#include <moveit/task_constructor/solvers/pipeline_planner.h>
#include <moveit/task_constructor/stages/connect.h>
#include <moveit/task_constructor/stages/current_state.h>
#include <moveit/task_constructor/stages/modify_planning_scene.h>
#include <moveit/task_constructor/stages/move_relative.h>
#include <moveit/task_constructor/stages/move_to.h>

#include <sstream>
#include <string>
#include <vector>

#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/vector3_stamped.hpp>

namespace crx10ial_tasks
{
namespace mtc = moveit::task_constructor;
namespace stages = moveit::task_constructor::stages;
namespace solvers = moveit::task_constructor::solvers;

namespace
{

geometry_msgs::msg::PoseStamped stamped_pose(
  const std::string & frame_id,
  const geometry_msgs::msg::Pose & pose)
{
  geometry_msgs::msg::PoseStamped stamped;
  stamped.header.frame_id = frame_id;
  stamped.pose = pose;
  return stamped;
}

geometry_msgs::msg::Vector3Stamped stamped_vector(
  const std::string & frame_id,
  const geometry_msgs::msg::Vector3 & vector)
{
  geometry_msgs::msg::Vector3Stamped stamped;
  stamped.header.frame_id = frame_id;
  stamped.vector = vector;
  return stamped;
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

}  // namespace

mtc::Task build_fixed_pick_place_task(
  const rclcpp::Node::SharedPtr & node,
  const FixedPickPlaceConfig & config,
  const geometry_msgs::msg::Pose & place_pose)
{
  mtc::Task task("crx10ial fixed pick place");
  task.loadRobotModel(node);
  task.setProperty("group", config.arm_group_name);
  task.setProperty("eef", config.eef_name);
  task.setProperty("hand", config.eef_name);
  task.setProperty("hand_grasping_frame", config.hand_frame);
  task.setProperty("ik_frame", config.hand_frame);
  task.setTimeout(config.planning.timeout_sec);

  auto sampling_planner = std::make_shared<solvers::PipelinePlanner>(node);
  sampling_planner->setProperty("goal_joint_tolerance", 1e-4);

  auto cartesian_planner = std::make_shared<solvers::CartesianPath>();
  cartesian_planner->setMaxVelocityScalingFactor(0.2);
  cartesian_planner->setMaxAccelerationScalingFactor(0.2);
  cartesian_planner->setStepSize(0.01);

  task.add(std::make_unique<stages::CurrentState>("current state"));

  const auto grasp_world_pose = compose_pose(config.object.pose, config.grasp.pose);
  const auto pregrasp_pose = translated_pose(
    grasp_world_pose,
    config.grasp.approach.direction,
    -config.grasp.approach.max_distance);

  {
    auto stage = std::make_unique<stages::MoveTo>("move to pregrasp pose", sampling_planner);
    stage->setGroup(config.arm_group_name);
    stage->setIKFrame(config.hand_frame);
    stage->setGoal(stamped_pose(config.object.frame_id, pregrasp_pose));
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::MoveRelative>("approach object", cartesian_planner);
    stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
    stage->properties().set("link", config.hand_frame);
    stage->setMinMaxDistance(
      config.grasp.approach.min_distance,
      config.grasp.approach.max_distance);
    stage->setDirection(
      stamped_vector(config.hand_frame, config.grasp.approach.direction));
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::ModifyPlanningScene>(
      "allow collision gripper object");
    stage->allowCollisions(
      config.object.id,
      std::vector<std::string>{
        config.eef_name, "gripper_palm", "left_finger", "right_finger", config.hand_frame},
      true);
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::ModifyPlanningScene>("internal attach object");
    stage->attachObject(config.object.id, config.hand_frame);
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::MoveRelative>("retreat with object", cartesian_planner);
    stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
    stage->properties().set("link", config.hand_frame);
    stage->setMinMaxDistance(
      config.grasp.retreat.min_distance,
      config.grasp.retreat.max_distance);
    stage->setDirection(
      stamped_vector(config.hand_frame, config.grasp.retreat.direction));
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::Connect>(
      "move to place",
      stages::Connect::GroupPlannerVector{{config.arm_group_name, sampling_planner}});
    stage->setTimeout(config.planning.timeout_sec);
    stage->properties().configureInitFrom(mtc::Stage::PARENT);
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::MoveTo>("move to place pose", sampling_planner);
    stage->setGroup(config.arm_group_name);
    stage->setIKFrame(config.hand_frame);
    stage->setGoal(stamped_pose(config.place.frame_id, place_pose));
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::ModifyPlanningScene>("internal detach object");
    stage->detachObject(config.object.id, config.hand_frame);
    task.add(std::move(stage));
  }

  {
    auto stage = std::make_unique<stages::MoveRelative>("retreat after place", cartesian_planner);
    stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
    stage->properties().set("link", config.hand_frame);
    stage->setMinMaxDistance(
      config.grasp.retreat.min_distance,
      config.grasp.retreat.max_distance);
    stage->setDirection(
      stamped_vector(config.hand_frame, config.grasp.retreat.direction));
    task.add(std::move(stage));
  }

  task.init();
  return task;
}

FixedPickPlaceResult plan_fixed_pick_place(
  const rclcpp::Node::SharedPtr & node,
  const FixedPickPlaceConfig & config,
  bool use_failure_place)
{
  const auto & target_place =
    use_failure_place ? config.failure_place.pose : config.place.pose;

  auto task = build_fixed_pick_place_task(node, config, target_place);
  const auto error_code = task.plan(config.planning.max_solutions);

  std::ostringstream diagnostics;
  task.printState(diagnostics);
  if (task.solutions().empty()) {
    task.explainFailure(diagnostics);
  }

  return FixedPickPlaceResult{
    static_cast<bool>(error_code) && !task.solutions().empty(),
    diagnostics.str(),
    task.solutions().size()};
}

}  // namespace crx10ial_tasks
