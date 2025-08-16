cmake_minimum_required(VERSION 3.29.0)

project(Hv_{{name}})
set(TARGET_NAME_LIB ${PROJECT_NAME}_AudioLib)
set(TARGET_NAME_PLUGIN ${PROJECT_NAME}_AudioPlugin)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED 17)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

set(CMAKE_STATIC_LIBRARY_PREFIX "")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/build/$<CONFIG>)

set(CMAKE_SHARED_LIBRARY_PREFIX "")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/build/$<CONFIG>)

include(FetchContent)

FetchContent_Declare(
    unitysdk
    DOWNLOAD_EXTRACT_TIMESTAMP OFF
    URL https://github.com/Unity-Technologies/NativeAudioPlugins/archive/refs/heads/master.zip
    SOURCE_DIR "${CMAKE_SOURCE_DIR}/vendor/UnityAudioSDK"
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/src/PluginList.h ${CMAKE_SOURCE_DIR}/vendor/UnityAudioSDK/NativeCode
)

FetchContent_GetProperties(unitysdk)
if (NOT unitysdk_POPULATED)
    FetchContent_MakeAvailable(unitysdk)
endif()

add_library(
  objlib OBJECT
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
)

add_library(${TARGET_NAME_LIB} SHARED $<TARGET_OBJECTS:objlib>)

add_custom_command(
  TARGET ${TARGET_NAME_LIB}
  POST_BUILD
  COMMAND ${CMAKE_COMMAND}
  ARGS -E copy ${CMAKE_SOURCE_DIR}/src/Hv_{{name}}_AudioLib.cs
  ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/Hv_{{name}}_AudioLib.cs
)

add_library(${TARGET_NAME_PLUGIN} SHARED $<TARGET_OBJECTS:objlib>)

target_sources(
  ${TARGET_NAME_PLUGIN} PRIVATE
  ${CMAKE_SOURCE_DIR}/src/{{name}}.cpp
  ${CMAKE_SOURCE_DIR}/vendor/UnityAudioSDK/NativeCode/AudioPluginUtil.cpp
)

target_include_directories(
  ${TARGET_NAME_PLUGIN} PRIVATE
  ${CMAKE_SOURCE_DIR}/include/Heavy
  ${CMAKE_SOURCE_DIR}/vendor/UnityAudioSDK/NativeCode
)

