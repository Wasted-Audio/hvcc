NAME = {{name}}
{%- if meta.enable_modgui is defined %}
MODGUI_CLASS_NAME = hv_{{name}}
{%- endif %}
{%- if meta.enable_ui is defined %}
FILES_DSP = $(filter-out HeavyDPF_{{name}}_UI.cpp, $(wildcard *.cpp))
{%- else %}
FILES_DSP = $(wildcard *.cpp)
{%- endif %}
FILES_DSP += $(wildcard *.c)

{%- if meta.enable_ui is defined %}
FILES_UI = HeavyDPF_{{name}}_UI.cpp
FILES_UI += ../../{{dpf_path}}dpf-widgets/opengl/DearImGui.cpp
{%- endif %}

DPF_TARGET_DIR = ../../bin
DPF_BUILD_DIR = ../../build
DPF_PATH = ../../{{dpf_path}}dpf

include ../../{{dpf_path}}dpf/Makefile.plugins.mk

{%- if meta.enable_ui is defined %}
BUILD_CXX_FLAGS += -I ../../{{dpf_path}}dpf-widgets/generic
BUILD_CXX_FLAGS += -I ../../{{dpf_path}}dpf-widgets/opengl
{%- endif %}

LINK_FLAGS += -lpthread
CFLAGS += -Wno-unused-parameter
CXXFLAGS += -Wno-unused-parameter

{% if meta.plugin_formats is defined %}
	{%- for format in meta.plugin_formats %}
TARGETS += {{format}}
	{%- endfor %}
{% else %}
TARGETS += jack
TARGETS += lv2_dsp
TARGETS += vst
{%- endif %}

all: $(TARGETS)
