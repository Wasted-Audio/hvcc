CC=clang
CXX=clang++
MKDIR=mkdir -p
SRCDIR=../source
OUTDIR=../build/linux/x64/release/Plugins/x64/linux
BASEFLAGS=-I$(SRCDIR) -DNDEBUG -msse4.1 -O3 -ffast-math -fPIC -Werror -Wno-unused-function -Wno-\#warnings
CFLAGS=$(BASEFLAGS) -std=c11
CXXFLAGS=$(BASEFLAGS) -std=c++11 -fno-exceptions -fno-rtti

HEADERS=$(wildcard $(SRCDIR)/heavy/*.h)
HEADERS+=$(wildcard $(SRCDIR)/heavy/*.hpp)

CFILES=$(wildcard $(SRCDIR)/heavy/*.c)
OBJC=$(CFILES:%.c=%.o)

CXXFILES=$(wildcard $(SRCDIR)/heavy/*.cpp)
OBJCXX=$(CXXFILES:%.cpp=%.o)

%.o: %.c $(HEADERS)
	$(CC) -c -o $@ $< $(CFLAGS)

%.o: %.cpp $(HEADERS)
	$(CXX) -c -o $@ $< $(CXXFLAGS)

all: directories lib

directories: $(OUTDIR)

$(OUTDIR):
	$(MKDIR) $(OUTDIR)

lib: $(OBJC) $(OBJCXX)
	$(CXX) -o $(OUTDIR)/lib{{patch_name}}.so $^ -shared

.PHONY: clean

clean:
	rm -f $(SRCDIR)/**/*.o $(OUTDIR)/*.so

