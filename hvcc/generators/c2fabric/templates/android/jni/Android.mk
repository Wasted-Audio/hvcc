LOCAL_PATH := $(call my-dir)

# ------------------------------------------------------------------------------
# libwrapper.so
include $(CLEAR_VARS)
LOCAL_MODULE := {{patch_name}}_wrapper
LOCAL_MODULE_FILENAME := lib{{patch_name}}
LOCAL_CFLAGS := -std=c11 -DNDEBUG -O3 -ffast-math -DHV_SIMD_NEON
LOCAL_CPPFLAGS := -std=c++11
LOCAL_C_INCLUDES := $(LOCAL_PATH)/../../source/heavy
LOCAL_SRC_FILES := $(wildcard $(LOCAL_PATH)/../../source/heavy/*.c)
LOCAL_SRC_FILES += $(wildcard $(LOCAL_PATH)/../../source/heavy/*.cpp)
LOCAL_LDLIBS := -latomic
TARGET_ARCH_ABI := armeabi-v7a
LOCAL_ARM_NEON := true
LOCAL_ARM_MODE := arm
include $(BUILD_SHARED_LIBRARY)

all:
	mkdir -p ../libs/$(TARGET_ARCH_ABI)/Plugins/$(TARGET_ARCH_ABI)
	mv ../libs/$(TARGET_ARCH_ABI)/*.so ../libs/$(TARGET_ARCH_ABI)/Plugins/$(TARGET_ARCH_ABI)
	mkdir -p ../libs/$(TARGET_ARCH_ABI)/Editor
	cp -r ../../source/fabric/Hv_{{patch_name}}_FabricDSPEditor.cs ../libs/$(TARGET_ARCH_ABI)/Editor
	cp -r ../../source/fabric/Hv_{{patch_name}}_FabricDSP.cs ../libs/$(TARGET_ARCH_ABI)
