# import datetime
import jinja2
import os
import shutil
import time
from ..buildjson import buildjson
from ..copyright import copyright_manager
import json2daisy
from . import parameters


class c2daisy:
    """ Generates a Daisy wrapper for a given patch.
    """

    @classmethod
    def compile(clazz, c_src_dir, out_dir, externs,
                patch_name=None, patch_meta: dict = None,
                num_input_channels=0, num_output_channels=0,
                copyright=None, verbose=False):

        tick = time.time()

        if patch_meta:
            patch_name = patch_meta.get("name", patch_name)
            daisy_meta = patch_meta.get("daisy")
        else:
            daisy_meta = {}

        board = daisy_meta.get("board", "seed")

        copyright_c = copyright_manager.get_copyright_for_c(copyright)
        # copyright_plist = copyright or u"Copyright {0} Enzien Audio, Ltd." \
        #     " All Rights Reserved.".format(datetime.datetime.now().year)

        try:
            # ensure that the output directory does not exist
            out_dir = os.path.abspath(out_dir)
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)

            # copy over static files
            shutil.copytree(os.path.join(os.path.dirname(__file__), "static"), out_dir)

            # copy over generated C source files
            source_dir = os.path.join(out_dir, "source")
            shutil.copytree(c_src_dir, source_dir)

            if daisy_meta.get('board_file'):
                header, board_info = json2daisy.generate_header_from_file(daisy_meta['board_file'])
            else:
                header, board_info = json2daisy.generate_header_from_name(board)

            component_glue = parameters.parse_parameters(
                externs['parameters'], board_info['components'], board_info['aliases'], 'hardware')
            component_glue['class_name'] = board_info['name']
            component_glue['patch_name'] = patch_name
            component_glue['header'] = f"HeavyDaisy_{patch_name}.hpp"
            component_glue['max_channels'] = board_info['channels']
            component_glue['num_output_channels'] = num_output_channels

            component_glue['copyright'] = copyright_c

            daisy_h_path = os.path.join(source_dir, f"HeavyDaisy_{patch_name}.hpp")
            with open(daisy_h_path, "w") as f:
                f.write(header)

            loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
            env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
            daisy_cpp_path = os.path.join(source_dir, f"HeavyDaisy_{patch_name}.cpp")

            rendered_cpp = env.get_template('HeavyDaisy.cpp').render(component_glue)
            with open(daisy_cpp_path, 'w') as file:
                file.write(rendered_cpp)

            makefile_replacements = {'name': patch_name}
            makefile_replacements['linker_script'] = daisy_meta.get('linker_script', '')
            if makefile_replacements['linker_script'] != '':
                makefile_replacements['linker_script'] = f'../{daisy_meta["linker_script"]}'
            depth = daisy_meta.get('libdaisy_depth', 2)
            makefile_replacements['libdaisy_path'] = f'{"../" * depth}libdaisy'
            makefile_replacements['bootloader'] = daisy_meta.get('bootloader', False)

            rendered_makefile = env.get_template('Makefile').render(makefile_replacements)
            with open(os.path.join(source_dir, "Makefile"), "w") as f:
                f.write(rendered_makefile)

            # ======================================================================================

            buildjson.generate_json(
                out_dir,
                linux_x64_args=["-j"])

            return {
                "stage": "c2daisy",
                "notifs": {
                    "has_error": False,
                    "exception": None,
                    "warnings": [],
                    "errors": []
                },
                "in_dir": c_src_dir,
                "in_file": "",
                "out_dir": out_dir,
                "out_file": os.path.basename(daisy_h_path),
                "compile_time": time.time() - tick
            }

        except Exception as e:
            return {
                "stage": "c2daisy",
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
