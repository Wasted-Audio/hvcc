# Project Name
TARGET = HeavyDaisy_{{name}}

# Library Locations
LIBDAISY_DIR = {{libdaisy_path}}

{% if linker_script != '' %}
LDSCRIPT = {{linker_script}}
{% endif %}

{% if bootloader != '' %}
APP_TYPE = {{bootloader}}
{% endif %}

{% if debug_printing %}
LDFLAGS += -u _printf_float
{% endif %}

# Project Source
C_SOURCES = $(wildcard *.c)
CPP_SOURCES = $(wildcard *.cpp)

# Core location, and generic makefile.
SYSTEM_FILES_DIR = $(LIBDAISY_DIR)/core
include $(SYSTEM_FILES_DIR)/Makefile
