cmake_minimum_required(VERSION 3.8)
project(crx10ial_tasks)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_gtest REQUIRED)
find_package(ament_cmake_pytest REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(moveit_core REQUIRED)
find_package(moveit_ros_planning REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(moveit_task_constructor_core REQUIRED)
find_package(moveit_task_constructor_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)

set(CONFIG_DEPS
  geometry_msgs
  rclcpp
  tf2
  tf2_geometry_msgs
)

set(MTC_DEPS
  moveit_core
  moveit_ros_planning
  moveit_ros_planning_interface
  moveit_task_constructor_core
  moveit_task_constructor_msgs
)

add_library(fixed_pick_place_config
  src/fixed_pick_place_config.cpp
)
target_include_directories(fixed_pick_place_config PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(fixed_pick_place_config ${CONFIG_DEPS})

add_library(fixed_pick_place_task
  src/fixed_pick_place_task.cpp
)
target_include_directories(fixed_pick_place_task PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
target_link_libraries(fixed_pick_place_task fixed_pick_place_config)
ament_target_dependencies(fixed_pick_place_task ${CONFIG_DEPS} ${MTC_DEPS})

add_executable(fixed_pick_place
  src/fixed_pick_place_node.cpp
)
target_link_libraries(fixed_pick_place
  fixed_pick_place_config
  fixed_pick_place_task
)
ament_target_dependencies(fixed_pick_place ${CONFIG_DEPS} ${MTC_DEPS})

install(TARGETS fixed_pick_place_config
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)
install(TARGETS fixed_pick_place_task
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)
install(TARGETS fixed_pick_place
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)
install(DIRECTORY include/
  DESTINATION include
)

install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  ament_add_pytest_test(fixed_pick_place_yaml
    test/test_fixed_pick_place_yaml.py
  )

  ament_add_pytest_test(task_source_contract
    test/test_task_source_contract.py
  )

  ament_add_gtest(test_fixed_pick_place_config
    test/test_fixed_pick_place_config.cpp
  )
  target_link_libraries(test_fixed_pick_place_config fixed_pick_place_config)
  ament_target_dependencies(test_fixed_pick_place_config ${CONFIG_DEPS})
endif()

ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
ament_export_dependencies(${CONFIG_DEPS} ${MTC_DEPS})
ament_package()
