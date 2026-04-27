cmake_minimum_required(VERSION 3.8)
project(crx10ial_cell_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch rviz urdf
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  find_package(ament_lint_auto REQUIRED)

  ament_add_pytest_test(
    test_cell_description
    test/test_cell_description.py
    ENV CRX10IAL_CELL_DESCRIPTION_SOURCE_DIR=${CMAKE_CURRENT_SOURCE_DIR}
  )

  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
