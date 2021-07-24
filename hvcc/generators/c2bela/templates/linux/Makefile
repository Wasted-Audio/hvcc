CC=ccache arm-linux-gnueabihf-gcc
CXX=ccache arm-linux-gnueabihf-g++
MKDIR=mkdir -p
SRCDIR=../source
OUTDIR=../build/linux/armv7a/release
BASEFLAGS=-I$(SRCDIR) -DNDEBUG -O3 -march=armv7-a -mtune=cortex-a8 -mfloat-abi=hard -mfpu=neon -ftree-vectorize -ffast-math -fPIC -Werror -Wno-unused-function -Wno-\#warnings
CFLAGS=$(BASEFLAGS) -std=c11
CXXFLAGS=$(BASEFLAGS) -std=c++11 -fno-exceptions -fno-rtti

HEADERS=$(wildcard $(SRCDIR)/*.h)
HEADERS+=$(wildcard $(SRCDIR)/*.hpp)

CFILES=$(wildcard $(SRCDIR)/*.c)
OBJC=$(CFILES:%.c=%.o)

CXXFILES=$(wildcard $(SRCDIR)/*.cpp)
OBJCXX=$(CXXFILES:%.cpp=%.o)

%.o: %.c $(HEADERS)
	$(CC) -c -o $@ $< $(CFLAGS)

%.o: %.cpp $(HEADERS)
	$(CXX) -c -o $@ $< $(CXXFLAGS)

all: directories objs

directories: $(OUTDIR)

$(OUTDIR):
	$(MKDIR) $(OUTDIR)

objs: $(OBJC) $(OBJCXX)
	cp $(SRCDIR)/* $(OUTDIR)

library: $(OBJC) $(OBJCXX)
	ar rcs $(OUTDIR)/libHv_{{name}}.a $^

zip: $(OBJC) $(OBJCXX)
	zip -j $(OUTDIR)/Hv_{{name}}_objs.zip $(SRCDIR)/*

.PHONY: clean

clean:
	rm -f $(SRCDIR)/*.o $(OUTDIR)/*.a $(OUTDIR)/*.zip

