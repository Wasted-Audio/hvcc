# Makefile to build class '{name}' for Pure Data.
# Needs Makefile.pdlibbuilder as helper makefile for platform-dependent build
# settings and rules.

# library name
lib.name = {{name}}

# input source file (class name == source file basename)
class.sources = pdext/{{name}}~.c

# all extra files to be included in binary distribution of the library
#datafiles = helloworld-help.pd helloworld-meta.pd README.md

# include Makefile.pdlibbuilder from submodule directory 'pd-lib-builder'
PDLIBBUILDER_DIR=pd-lib-builder/
include $(PDLIBBUILDER_DIR)/Makefile.pdlibbuilder
