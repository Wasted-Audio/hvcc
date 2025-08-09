cmake_minimum_required(VERSION 3.29.0)

project({{name}})

if(NOT IS_DIRECTORY ${CMAKE_SOURCE_DIR}/include/fmod)
  message(FATAL_ERROR "FMOD SDK MISSING: ${CMAKE_SOURCE_DIR}/include/fmod")
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED 17)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

set(CMAKE_STATIC_LIBRARY_PREFIX "")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/build/$<CONFIG>)

set(CMAKE_SHARED_LIBRARY_PREFIX "")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/build/$<CONFIG>)

add_library(
  objlib OBJECT
  ${CMAKE_SOURCE_DIR}/src/{{name}}.cpp
)

set_target_properties(
  objlib PROPERTIES
  POSITION_INDEPENDENT_CODE True
)

target_sources(
  objlib PRIVATE
  {%- for file in heavy_src_files %}
  ${CMAKE_SOURCE_DIR}/include/Heavy/{{file}}
  {%- endfor %}
)

target_include_directories(
  objlib PRIVATE
  ${CMAKE_SOURCE_DIR}/include/Heavy
  ${CMAKE_SOURCE_DIR}/include/fmod/core/inc
  ${CMAKE_SOURCE_DIR}/include/fmod/studio/inc
)

add_library(${PROJECT_NAME} SHARED $<TARGET_OBJECTS:objlib>)
add_library(lib${PROJECT_NAME} STATIC $<TARGET_OBJECTS:objlib>)

add_custom_command(
  TARGET ${PROJECT_NAME}
  POST_BUILD
  COMMAND ${CMAKE_COMMAND}
  ARGS -E copy ${CMAKE_SOURCE_DIR}/src/{{name}}.plugin.js
  ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/{{name}}.plugin.js
)

