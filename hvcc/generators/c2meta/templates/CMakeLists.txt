add_library({{ name }} STATIC)
target_include_directories({{ name }} PRIVATE . )

file(GLOB C_SOURCES "source/*.c")
file(GLOB CPP_SOURCES "source/*.cpp")

target_sources({{ name }} PRIVATE
    compat.cpp
    ${C_SOURCES}
    ${CPP_SOURCES}
)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DHV_SIMD_NONE=1 -DHV_BARE_METAL")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DHV_SIMD_NONE=1 -DHV_BARE_METAL")

# Call this to link and create the plugin file
create_plugin(
    SOURCE_LIB      {{ name }}
    PLUGIN_NAME     {{ name }}
    PLUGIN_JSON     ${CMAKE_CURRENT_LIST_DIR}/plugin.json           # Path to the plugin.json file used by VCV Rack
    SOURCE_ASSETS   ${CMAKE_CURRENT_LIST_DIR}/assets
    DESTINATION     ${CMAKE_CURRENT_LIST_DIR}/../metamodule-plugins/
)
