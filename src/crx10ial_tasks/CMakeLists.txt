cmake_minimum_required(VERSION 3.8)
project(crx10ial_tasks)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_gtest REQUIRED)
find_package(ament_cmake_pytest REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)

set(CONFIG_DEPS
  geometry_msgs
  rclcpp
  tf2
  tf2_geometry_msgs
)

add_library(fixed_pick_place_config
  src/fixed_pick_place_config.cpp
)
target_include_directories(fixed_pick_place_config PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(fixed_pick_place_config ${CONFIG_DEPS})

install(TARGETS fixed_pick_place_config
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)
install(DIRECTORY include/
  DESTINATION include
)

install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  ament_add_pytest_test(fixed_pick_place_yaml
    test/test_fixed_pick_place_yaml.py
  )

  ament_add_gtest(test_fixed_pick_place_config
    test/test_fixed_pick_place_config.cpp
  )
  target_link_libraries(test_fixed_pick_place_config fixed_pick_place_config)
  ament_target_dependencies(test_fixed_pick_place_config ${CONFIG_DEPS})
endif()

ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
ament_export_dependencies(${CONFIG_DEPS})
ament_package()
