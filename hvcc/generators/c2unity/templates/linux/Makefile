CC=clang
CXX=clang++
MKDIR=mkdir -p
SRCDIR=../source
OUTDIR=../build/linux/x64/release
BASEFLAGS=-I$(SRCDIR) -DNDEBUG -msse4.1 -O3 -ffast-math -fPIC -Werror -Wno-unused-function -Wno-\#warnings
CFLAGS=$(BASEFLAGS) -std=c11
CXXFLAGS=$(BASEFLAGS) -std=c++11 -Wno-writable-strings -fno-exceptions -fno-rtti

# AudioLib
HEADERS_LIB=$(wildcard $(SRCDIR)/heavy/*.h)
HEADERS_LIB+=$(wildcard $(SRCDIR)/heavy/*.hpp)

CFILES_LIB=$(wildcard $(SRCDIR)/heavy/*.c)
OBJC_LIB=$(CFILES_LIB:%.c=%.o)

CXXFILES_LIB=$(wildcard $(SRCDIR)/heavy/*.cpp)
OBJCXX_LIB=$(CXXFILES_LIB:%.cpp=%.o)

# AudioPlugin
HEADERS_PLUG=$(HEADERS_LIB)
HEADERS_PLUG+=$(wildcard $(SRCDIR)/unity/*.hpp)

CFILES_PLUG=$(CFILES_LIB)
CFILES_PLUG+=$(wildcard $(SRCDIR)/unity/*.c)
OBJC_PLUG=$(CFILES_PLUG:%.c=%.o)

CXXFILES_PLUG=$(CXXFILES_LIB)
CXXFILES_PLUG+=$(wildcard $(SRCDIR)/unity/*.cpp)
OBJCXX_PLUG=$(CXXFILES_PLUG:%.cpp=%.o)

%.o: %.c $(HEADERS)
	$(CC) -c -o $@ $< $(CFLAGS)

%.o: %.cpp $(HEADERS)
	$(CXX) -c -o $@ $< $(CXXFLAGS)

all: directories audiolib audioplugin

directories: $(OUTDIR)

$(OUTDIR):
	$(MKDIR) $(OUTDIR)

audiolib: $(OBJC_LIB) $(OBJCXX_LIB)
	$(CXX) -o $(OUTDIR)/Hv_{{patch_name}}_AudioLib.so $^ -shared
	cp $(SRCDIR)/unity/Hv_{{patch_name}}_AudioLib.cs $(OUTDIR)

audioplugin: $(OBJC_PLUG) $(OBJCXX_PLUG)
	$(CXX) -o $(OUTDIR)/AudioPlugin_Hv_{{patch_name}}.so $^ -shared

.PHONY: clean

clean:
	rm -f $(SRCDIR)/**/*.o $(OUTDIR)/*.so $(OUTDIR)/Hv_{{patch_name}}_AudioLib.cs

