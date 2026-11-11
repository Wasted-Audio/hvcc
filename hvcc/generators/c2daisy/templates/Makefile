# Project Name
TARGET = HeavyDaisy_{{name}}

# Library Locations
LIBDAISY_DIR = {{libdaisy_path}}

{% if linker_script != '' %}
LDSCRIPT = {{linker_script}}
{% endif %}

{% if bootloader != None %}
APP_TYPE = {{bootloader}}
{% endif %}

{% if debug_printing is sameas true %}
LDFLAGS += -u _printf_float
{% endif %}

# Project Source
C_SOURCES = $(wildcard *.c)
CPP_SOURCES = $(wildcard *.cpp)

# Core location, and generic makefile.
SYSTEM_FILES_DIR = $(LIBDAISY_DIR)/core
include $(SYSTEM_FILES_DIR)/Makefile

CFLAGS += -DHV_BARE_METAL

# A2LiteNet Object - TODO: detect if used
NAM_OBJ = $(BUILD_DIR)/A2LiteNet.o
$(NAM_OBJ): CPPFLAGS += \
  -O3 -fmove-loop-invariants -ffp-contract=fast \
  -fno-math-errno -fno-trapping-math \
  -fsingle-precision-constant -DNDEBUG

$(NAM_OBJ): CPPFLAGS += -DNAM_BLOCK_SIZE=4
