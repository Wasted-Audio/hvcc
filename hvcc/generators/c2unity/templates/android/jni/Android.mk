LOCAL_PATH := $(call my-dir)

# ------------------------------------------------------------------------------
# static heavy library
include $(CLEAR_VARS)
LOCAL_MODULE := hv_static
LOCAL_CFLAGS := -std=c11 -DNDEBUG -DHV_SIMD_NEON -O3 -ffast-math -fPIC
LOCAL_CPPFLAGS := -std=c++11
LOCAL_C_INCLUDES := $(LOCAL_PATH)/../../source/heavy
LOCAL_SRC_FILES := $(wildcard $(LOCAL_PATH)/../../source/heavy/*.c)
LOCAL_SRC_FILES += $(wildcard $(LOCAL_PATH)/../../source/heavy/*.cpp)
LOCAL_ARM_NEON := true
LOCAL_ARM_MODE := arm
include $(BUILD_STATIC_LIBRARY)

# ------------------------------------------------------------------------------
# audiolib.so
include $(CLEAR_VARS)
LOCAL_MODULE := {{patch_name}}_lib
LOCAL_MODULE_FILENAME := libHv_{{patch_name}}_AudioLib
LOCAL_CFLAGS := -std=c11 -DNDEBUG -DHV_SIMD_NEON -O3 -ffast-math -fPIC
LOCAL_CPPFLAGS := -std=c++11
# there are no additional source files for the library wrapper,
# just build a shared library version of it
LOCAL_WHOLE_STATIC_LIBRARIES := hv_static
LOCAL_LDLIBS := -latomic
LOCAL_ARM_NEON := true
LOCAL_ARM_MODE := arm
include $(BUILD_SHARED_LIBRARY)

# ------------------------------------------------------------------------------
# libplugin.so
include $(CLEAR_VARS)
LOCAL_MODULE := {{patch_name}}_plugin
LOCAL_MODULE_FILENAME := AudioPlugin_Hv_{{patch_name}}
LOCAL_CFLAGS := -std=c11 -DNDEBUG -DHV_SIMD_NEON -O3 -ffast-math -fPIC
LOCAL_CPPFLAGS := -std=c++11
LOCAL_C_INCLUDES := $(LOCAL_PATH)/../../source
LOCAL_SRC_FILES := $(wildcard $(LOCAL_PATH)/../../source/unity/*.c)
LOCAL_SRC_FILES += $(wildcard $(LOCAL_PATH)/../../source/unity/*.cpp)
LOCAL_LDLIBS := -latomic
LOCAL_STATIC_LIBRARIES := hv_static
LOCAL_ARM_NEON := true
LOCAL_ARM_MODE := arm
include $(BUILD_SHARED_LIBRARY)
