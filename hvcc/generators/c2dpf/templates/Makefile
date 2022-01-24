NAME = {{name}}

FILES_DSP = $(wildcard *.cpp)
FILES_DSP += $(wildcard *.c)

include ../../dpf/Makefile.plugins.mk

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
