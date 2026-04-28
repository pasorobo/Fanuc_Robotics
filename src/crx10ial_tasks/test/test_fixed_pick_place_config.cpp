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

#include <gtest/gtest.h>
#include <rclcpp/rclcpp.hpp>

#include <crx10ial_tasks/fixed_pick_place_config.hpp>

namespace
{
rclcpp::NodeOptions options_with_overrides()
{
  rclcpp::NodeOptions options;
  options.parameter_overrides(
    {
      rclcpp::Parameter("arm_group_name", "manipulator"),
      rclcpp::Parameter("eef_name", "tool_link"),
      rclcpp::Parameter("hand_frame", "grasp_link"),
      rclcpp::Parameter("world_frame", "world"),
      rclcpp::Parameter("object.id", "work_object"),
      rclcpp::Parameter("object.frame_id", "world"),
      rclcpp::Parameter("object.dimensions", std::vector<double>{0.08, 0.08, 0.05}),
      rclcpp::Parameter("object.pose.xyz", std::vector<double>{0.55, 0.0, 0.745}),
      rclcpp::Parameter("object.pose.rpy", std::vector<double>{0.0, 0.0, 0.0}),
      rclcpp::Parameter("grasp.frame_id", "grasp_link"),
      rclcpp::Parameter("grasp.pose.xyz", std::vector<double>{-0.10, 0.0, 0.255}),
      rclcpp::Parameter("grasp.pose.rpy", std::vector<double>{0.0, 0.0, 0.0}),
      rclcpp::Parameter("grasp.approach.direction", std::vector<double>{1.0, 0.0, 0.0}),
      rclcpp::Parameter("grasp.approach.min", 0.05),
      rclcpp::Parameter("grasp.approach.max", 0.10),
      rclcpp::Parameter("grasp.retreat.direction", std::vector<double>{-1.0, 0.0, 0.0}),
      rclcpp::Parameter("grasp.retreat.min", 0.05),
      rclcpp::Parameter("grasp.retreat.max", 0.10),
      rclcpp::Parameter("place.frame_id", "world"),
      rclcpp::Parameter("place.pose.xyz", std::vector<double>{0.45, 0.20, 1.00}),
      rclcpp::Parameter("place.pose.rpy", std::vector<double>{0.0, 0.0, 0.0}),
      rclcpp::Parameter("failure.place.pose.xyz", std::vector<double>{2.0, 0.0, 1.00}),
      rclcpp::Parameter("failure.place.pose.rpy", std::vector<double>{0.0, 0.0, 0.0}),
      rclcpp::Parameter("gripper.open_width_m", 0.08),
      rclcpp::Parameter("gripper.close_width_m", 0.02),
      rclcpp::Parameter("gripper.close_force_n", 30.0),
      rclcpp::Parameter("planning.max_solutions", 1),
      rclcpp::Parameter("planning.timeout_sec", 10.0),
      rclcpp::Parameter("execution.enabled", false),
    });
  return options;
}
}  // namespace

TEST(FixedPickPlaceConfig, LoadsTypedParameters) {
  rclcpp::init(0, nullptr);
  auto node = std::make_shared<rclcpp::Node>("config_test", options_with_overrides());

  const auto config = crx10ial_tasks::load_fixed_pick_place_config(*node);

  EXPECT_EQ(config.arm_group_name, "manipulator");
  EXPECT_EQ(config.object.id, "work_object");
  EXPECT_EQ(config.hand_frame, "grasp_link");
  EXPECT_DOUBLE_EQ(config.place.pose.position.y, 0.20);
  EXPECT_DOUBLE_EQ(config.gripper.close_force_n, 30.0);
  EXPECT_EQ(config.planning.max_solutions, 1u);
  EXPECT_FALSE(config.execution_enabled);

  rclcpp::shutdown();
}

TEST(FixedPickPlaceConfig, RejectsInvalidVectorLength) {
  rclcpp::init(0, nullptr);
  auto options = options_with_overrides();
  options.parameter_overrides().push_back(
    rclcpp::Parameter("object.pose.xyz", std::vector<double>{0.55, 0.0}));
  auto node = std::make_shared<rclcpp::Node>("invalid_config_test", options);

  EXPECT_THROW(
    static_cast<void>(crx10ial_tasks::load_fixed_pick_place_config(*node)),
    std::runtime_error);

  rclcpp::shutdown();
}
