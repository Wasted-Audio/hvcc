# Project Name
TARGET = HeavyDaisy_{{name}}

# Library Locations
LIBDAISY_DIR = ../../libdaisy
HVCC_DIR = ../../c

# HVCC Sources
CPP_SOURCES = $(wildcard $(HVCC_DIR)/*.cpp)
C_INCLUDES = -I$(HVCC_DIR)/
C_SOURCES = $(wildcard $(HVCC_DIR)/*.c)

# Project Source
CPP_SOURCES += $(TARGET).cpp

# Core location, and generic makefile.
SYSTEM_FILES_DIR = $(LIBDAISY_DIR)/core
include $(SYSTEM_FILES_DIR)/Makefile
