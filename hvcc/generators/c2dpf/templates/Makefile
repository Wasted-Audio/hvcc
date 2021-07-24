NAME = {{name}}

FILES_DSP = $(wildcard *.cpp)
FILES_DSP += $(wildcard *.c)

include ../../dpf/Makefile.plugins.mk

LINK_FLAGS += -lpthread

TARGETS += jack
TARGETS += lv2_dsp
TARGETS += vst

all: $(TARGETS)
