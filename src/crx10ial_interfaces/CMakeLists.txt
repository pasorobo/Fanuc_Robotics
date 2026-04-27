cmake_minimum_required(VERSION 3.8)
project(crx10ial_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/AttachObject.srv"
  "srv/CommandGripper.srv"
  "srv/DetachObject.srv"
  "srv/GetGripperState.srv"
)

ament_export_dependencies(rosidl_default_runtime)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
