# Makefile to build class '{name}' for Pure Data.
# Needs Makefile.pdlibbuilder as helper makefile for platform-dependent build
# settings and rules.

# library name
lib.name = {{name}}

ldlibs += -lstdc++

# input source file (class name == source file basename)
class.sources = pdext/{{name}}~.c
common.sources = $(filter-out pdext/{{name}}~.c, $(wildcard pdext/*.c))
common.sources += $(wildcard pdext/*.cpp)

# all extra files to be included in binary distribution of the library
#datafiles = helloworld-help.pd helloworld-meta.pd README.md

include Makefile.pdlibbuilder
