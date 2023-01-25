NAME = {{name}}

FILES_DSP = $(filter-out HeavyDPF_{{name}}_UI.cpp, $(wildcard *.cpp))
FILES_DSP += $(wildcard *.c)

FILES_UI = HeavyDPF_{{name}}_UI.cpp
FILES_UI += ../../{{dpf_path}}dpf-widgets/opengl/DearImGui.cpp

DPF_TARGET_DIR = ../../bin
DPF_BUILD_DIR = ../../build
DPF_PATH = ../../{{dpf_path}}dpf

include ../../{{dpf_path}}dpf/Makefile.plugins.mk

BUILD_CXX_FLAGS += -I ../../{{dpf_path}}dpf-widgets/generic
BUILD_CXX_FLAGS += -I ../../{{dpf_path}}dpf-widgets/opengl


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
