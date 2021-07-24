# Copyright (C) 2014-2018 Enzien Audio, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import time
import jinja2
from ..copyright import copyright_manager


class c2js:
    """Compiles a directory of C source files into javascript. Requires the
    emscripten library to be installed - https://github.com/kripken/emscripten
    """

    __HV_API = [
        "_hv_{0}_new",
        "_hv_{0}_new_with_options",
        "_hv_delete",
        "_hv_processInline",
        "_hv_getNumInputChannels",
        "_hv_getNumOutputChannels",
        "_hv_samplesToMilliseconds",
        "_hv_setPrintHook",
        "_hv_setSendHook",
        "_hv_sendFloatToReceiver",
        "_hv_sendBangToReceiver",
        "_hv_sendSymbolToReceiver",
        "_hv_stringToHash",
        "_hv_msg_getByteSize",
        "_hv_msg_init",
        "_hv_msg_hasFormat",
        "_hv_msg_setFloat",
        "_hv_msg_getFloat",
        "_hv_msg_getTimestamp",
        "_hv_table_getLength",
        "_hv_table_setLength",
        "_hv_table_getBuffer",
        "_hv_sendMessageToReceiverV"
    ]

    @classmethod
    def run_emscripten(clazz, c_src_dir, out_dir, patch_name, post_js_path):
        """Run the emcc command to compile C source files to a javascript library.
        """
        emcc_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "emsdk", "emscripten", "1.37.38", "emcc"))

        emcpp_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "emsdk", "emscripten", "1.37.38", "em++"))

        if not os.path.isfile(emcc_path):
            raise Exception("Emscripten emcc command line tool not installed, should be here: " + emcc_path)

        if not os.path.isfile(emcpp_path):
            raise Exception("Emscripten em++ command line tool not installed, should be here: " + emcpp_path)

        c_flags = [
            "-I" + c_src_dir,
            "-DHV_SIMD_NONE",
            "-ffast-math",
            "-DNDEBUG",
            "-Wall"
        ]

        c_src_paths = [os.path.join(c_src_dir, c) for c in os.listdir(c_src_dir) if c.endswith((".c"))]
        cpp_src_paths = [os.path.join(c_src_dir, cpp) for cpp in os.listdir(c_src_dir) if cpp.endswith((".cpp"))]
        obj_paths = []
        cmd = ""

        # compile C files
        for c in c_src_paths:
            obj_path = os.path.splitext(c)[0] + ".o"
            cmd = [emcc_path] + c_flags + ["-c", "-o", obj_path, c]
            subprocess.check_output(cmd)  # run emscripten
            obj_paths += [obj_path]

        # compile C++ files
        for cpp in cpp_src_paths:
            obj_path = os.path.splitext(cpp)[0] + ".o"
            cmd = [emcpp_path] + c_flags + ["-std=c++11"] + ["-c", "-o", obj_path, cpp]
            subprocess.check_output(cmd)  # run emscripten
            obj_paths += [obj_path]

        # exported heavy api methods
        hv_api_defs = ", ".join(["\"{0}\"".format(x) for x in c2js.__HV_API])

        # output path
        asm_js_path = os.path.join(out_dir, "{0}.asm.js".format(patch_name))
        wasm_js_path = os.path.join(out_dir, "{0}.js".format(patch_name))

        linker_flags = [
            "-O3",
            "--memory-init-file", "0",
            "-s", "RESERVED_FUNCTION_POINTERS=2",
            "-s", "EXPORTED_FUNCTIONS=[" + hv_api_defs.format(patch_name) + "]",
            "-s", "MODULARIZE=1",
            "-s", "BINARYEN_TRAP_MODE='clamp'",
            "--post-js", post_js_path
        ]

        # include C/C++ obj files in js library
        cmd = [emcc_path] + obj_paths + linker_flags

        # run emscripten twice!
        subprocess.check_output(  # fallback asm.js build
            cmd + [
                "-s", "EXPORT_NAME='{0}_AsmModule'".format(patch_name),
                "-o", asm_js_path
            ])

        subprocess.check_output(  # WASM
            cmd + [
                "-s", "WASM=1",
                "-s", "EXPORT_NAME='{0}_Module'".format(patch_name),
                "-o", wasm_js_path
            ])

        # clean up
        for o in obj_paths:
            os.remove(o)

        return wasm_js_path

    @classmethod
    def compile(clazz, c_src_dir, out_dir, externs,
                patch_name=None, num_input_channels=0, num_output_channels=0,
                copyright=None, verbose=False):

        tick = time.time()

        parameter_list = externs["parameters"]["in"]
        event_list = externs["events"]["in"]

        patch_name = patch_name or "heavy"

        copyright_js = copyright_manager.get_copyright_for_c(copyright)
        copyright_html = copyright_manager.get_copyright_for_xml(copyright)

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_dir = os.path.abspath(out_dir)

        try:
            # initialise the jinja template environment
            env = jinja2.Environment()
            env.loader = jinja2.FileSystemLoader(os.path.join(
                os.path.dirname(__file__),
                "template"))

            # generate heavy js wrapper from template
            # Note: this file will be incorporated into the emscripten output
            # and removed afterwards
            post_js_path = os.path.join(out_dir, "hv_wrapper.js")
            with open(post_js_path, "w") as f:
                f.write(env.get_template("hv_wrapper.js").render(
                    name=patch_name,
                    copyright=copyright_js,
                    externs=externs,
                    pool_sizes_kb=externs["memoryPoolSizesKb"]))

            js_path = c2js.run_emscripten(c_src_dir=c_src_dir,
                                          out_dir=out_dir,
                                          patch_name=patch_name,
                                          post_js_path=post_js_path)

            # delete temporary files
            os.remove(post_js_path)

            js_out_file = os.path.basename(js_path)

            # generate index.html from template
            with open(os.path.join(out_dir, "index.html"), "w") as f:
                f.write(env.get_template("index.html").render(
                    name=patch_name,
                    includes=["./{0}".format(js_out_file)],
                    parameters=parameter_list,
                    events=event_list,
                    copyright=copyright_html))

            return {
                "stage": "c2js",
                "notifs": {
                    "has_error": False,
                    "exception": None,
                    "warnings": [],
                    "errors": []
                },
                "in_dir": c_src_dir,
                "in_file": "",
                "out_dir": out_dir,
                "out_file": js_out_file,
                "compile_time": time.time() - tick
            }

        except Exception as e:
            return {
                "stage": "c2js",
                "notifs": {
                    "has_error": True,
                    "exception": e,
                    "warnings": [],
                    "errors": [{
                        "enum": -1,
                        "message": str(e)
                    }]
                },
                "in_dir": c_src_dir,
                "in_file": "",
                "out_dir": out_dir,
                "out_file": "",
                "compile_time": time.time() - tick
            }
