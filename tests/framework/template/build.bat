@echo off

set CC=clang
set CXX=clang++
set COMMONFLAGS=-Werror -Wno-deprecated-declarations -Wno-unused-function -Wno-#warnings {{" ".join(simd_flags)}}
set CFLAGS=-std=c11 %COMMONFLAGS%
set CXXFLAGS=-std=c++14 -fno-exceptions -fno-rtti %COMMONFLAGS%

del *.o > NUL 2> NUL
del *.exe > NUL 2> NUL

set HEADERS= ^
{%- for f in source_files if f.endswith((".h", ".hpp")) %}
{{f}}{% if not loop.last %} ^{% endif %}
{%- endfor %}

set CFILES= ^
{%- for f in source_files if f.endswith((".c")) %}
{{f}}{% if not loop.last %} ^{% endif %}
{%- endfor %}

set CXXFILES= ^
{%- for f in source_files if f.endswith((".cpp")) %}
{{f}}{% if not loop.last %} ^{% endif %}
{%- endfor %}

set OBJ= ^
{%- for f in source_files if f.endswith((".c", ".cpp")) %}
{{f.split(".")[0] + ".o"}}{% if not loop.last %} ^{% endif %}
{%- endfor %}

REM Compiling C files
{%- for f in source_files if f.endswith((".c")) %}
%CC% -c -o {{f.split(".")[0] + ".o"}} {{f}} %COMMONFLAGS% %CFLAGS%
{%- endfor %}

REM Compiling C++ files
{%- for f in source_files if f.endswith((".cpp")) %}
%CXX% -c -o {{f.split(".")[0] + ".o"}} {{f}} %COMMONFLAGS% %CXXFLAGS%
{%- endfor %}

REM Making executable
%CXX% -o {{out_path}}.exe %OBJ%

REM Test {{out_path}}