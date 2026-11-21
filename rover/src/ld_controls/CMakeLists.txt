cmake_minimum_required(VERSION 3.8)
project(ld_controls)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# === Find dependencies ===
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
# Add any other message packages you use

# === Build your node ===
add_executable(ld_mapping scripts/ld_mapping.cpp)
ament_target_dependencies(ld_mapping rclcpp std_msgs sensor_msgs)

# === Install ===
install(TARGETS
  ld_mapping
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()

