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

#include <memory>
#include <string>

#include <crx10ial_tasks/fixed_pick_place_config.hpp>
#include <crx10ial_tasks/fixed_pick_place_task.hpp>
#include <rclcpp/rclcpp.hpp>

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("fixed_pick_place");

  try {
    const auto mode = node->declare_parameter<std::string>("run_mode", "plan");
    const auto config = crx10ial_tasks::load_fixed_pick_place_config(*node);

    if (mode == "plan") {
      const auto result = crx10ial_tasks::plan_fixed_pick_place(node, config, false);
      RCLCPP_INFO_STREAM(node->get_logger(), result.diagnostics);
      if (!result.success) {
        RCLCPP_ERROR(node->get_logger(), "M3 fixed pick/place planning failed");
        rclcpp::shutdown();
        return 2;
      }
      RCLCPP_INFO(
        node->get_logger(),
        "M3 fixed pick/place planning succeeded with %zu solution(s)",
        result.solution_count);
      rclcpp::shutdown();
      return 0;
    }

    if (mode == "negative_plan") {
      const auto result = crx10ial_tasks::plan_fixed_pick_place(node, config, true);
      RCLCPP_INFO_STREAM(node->get_logger(), result.diagnostics);
      if (result.success || result.diagnostics.empty()) {
        RCLCPP_ERROR(
          node->get_logger(),
          "M3 negative planning was expected to fail with diagnostics");
        rclcpp::shutdown();
        return 3;
      }
      RCLCPP_INFO(node->get_logger(), "M3 negative planning produced diagnostics");
      rclcpp::shutdown();
      return 0;
    }

    RCLCPP_ERROR(node->get_logger(), "unsupported run_mode: %s", mode.c_str());
    rclcpp::shutdown();
    return 4;
  } catch (const std::exception & exc) {
    RCLCPP_ERROR(node->get_logger(), "fixed pick/place failed: %s", exc.what());
    rclcpp::shutdown();
    return 1;
  }
}
