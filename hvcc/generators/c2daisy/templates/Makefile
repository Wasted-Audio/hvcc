# Project Name
TARGET = HeavyDaisy_{{name}}

# Library Locations
LIBDAISY_DIR = {{libdaisy_path}}

{% if linker_script != '' %}
LDSCRIPT = {{linker_script}}
{% endif %}

{% if bootloader != '' %}
BOOTLOADER = {{bootloader}}
{% endif %}

# Project Source
C_SOURCES = $(wildcard *.c)
CPP_SOURCES = $(wildcard *.cpp)

# Core location, and generic makefile.
SYSTEM_FILES_DIR = $(LIBDAISY_DIR)/core
include $(SYSTEM_FILES_DIR)/Makefile

{% if bootloader != '' %}
program-boot:
	$(OCD) -s $(OCD_DIR) $(OCDFLAGS) \
		-c "program $(BOOTLOADER) verify reset exit $(FLASH_ADDRESS)"

program-boot-dfu:
	dfu-util -a 0 -s $(FLASH_ADDRESS):leave -D $(BOOTLOADER) -d ,0483:df11
{% endif %}