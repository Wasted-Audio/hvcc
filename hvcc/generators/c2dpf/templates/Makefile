NAME = {{name}}

FILES_DSP = $(wildcard *.cpp)
FILES_DSP += $(wildcard *.c)

DPF_TARGET_DIR = ../../bin
DPF_BUILD_DIR = ../../build
DPF_PATH = ../../{{dpf_path}}dpf

include ../../{{dpf_path}}dpf/Makefile.plugins.mk

LINK_FLAGS += -lpthread
CFLAGS += -Wno-unused-parameter
CXXFLAGS += -Wno-unused-parameter

{% if meta.plugin_formats is defined %}
	{% for format in meta.plugin_formats %}
TARGETS += {{format}}
	{% endfor %}
{% else %}
TARGETS += jack
TARGETS += lv2_dsp
TARGETS += vst
{% endif %}

all: $(TARGETS)
