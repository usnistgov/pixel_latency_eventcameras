cmake_minimum_required(VERSION 3.16)
project(event_camera_latency_program)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)
set(CMAKE_VERBOSE_MAKEFILE TRUE)
set(CMAKE_BUILD_TYPE Release) # warn: temporary

add_compile_options(-Wall -Wextra -O3)

find_package(MetavisionSDK COMPONENTS core driver ui analytics REQUIRED)

add_executable(event_camera_latency_program src/main.cpp src/latency.cpp)
target_include_directories(event_camera_latency_program PUBLIC
    lib
    lib/argparse/include/)
target_link_libraries(event_camera_latency_program MetavisionSDK::core MetavisionSDK::driver MetavisionSDK::ui MetavisionSDK::analytics)

if (DEFINED CUSTOM_LIB_DIR)
    message("Add custom lib link and include directories.")
    target_include_directories(event_camera_latency_program PUBLIC ${CUSTOM_LIB_DIR}/include/)
    target_link_directories(event_camera_latency_program PUBLIC ${CUSTOM_LIB_DIR}/lib/)
endif()
