cmake_minimum_required(VERSION 3.8)
project(crx10ial_tasks)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_pytest REQUIRED)

install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  ament_add_pytest_test(fixed_pick_place_yaml
    test/test_fixed_pick_place_yaml.py
  )
endif()

ament_package()
