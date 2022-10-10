CC=clang
CXX=clang++
COMMONFLAGS=-Werror -Wno-unused-function -Wno-\#warnings {{" ".join(simd_flags)}}
CFLAGS=-std=c11 $(COMMONFLAGS)
CXXFLAGS=-std=c++11 -fno-exceptions -fno-rtti $(COMMONFLAGS)

DEPS= \
{%- for f in source_files if f.endswith((".h", ".hpp")) %}
{{f}}{% if not loop.last %} \{% endif %}
{%- endfor %}

OBJ= \
{%- for f in source_files if f.endswith((".c", ".cpp")) %}
{{f.split(".")[0] + ".o"}}{% if not loop.last %} \{% endif %}
{%- endfor %}

all: main

# compile only, C source
%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

# compile only, C++ source
%.o: %.cpp $(DEPS)
	$(CXX) -c -o $@ $< $(CXXFLAGS)

# link
main: $(OBJ)
	$(CXX) -o {{out_path}} $^

.PHONY: clean

clean:
	rm -f $(OBJ)
