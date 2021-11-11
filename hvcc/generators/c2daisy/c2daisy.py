# import datetime
import os
import shutil
import time
from ..buildjson import buildjson
from ..copyright import copyright_manager
from json2daisy import board_gen


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

            # supply a custom board description file, if it exists
            if daisy_meta.get('board_file', {}):
                board_description_file = daisy_meta['board_file']
            else:
                board_description_file = ''

            # call the json2daisy module function
            hpp, cpp, makefile = board_gen.generate_board(
                board,
                board_description_file, 
                parameters=externs['parameters'],
                name=patch_name,
                class_name=f"HeavyDaisy_{patch_name}", 
                copyright=copyright_c,
                meta=patch_meta
            )

            daisy_h_path = os.path.join(source_dir, f"HeavyDaisy_{patch_name}.hpp")
            with open(daisy_h_path, "w") as f:
                f.write(hpp)
            
            daisy_cpp_path = os.path.join(source_dir, f"HeavyDaisy_{patch_name}.cpp")
            with open(daisy_cpp_path, "w") as f:
                f.write(cpp)

            with open(os.path.join(source_dir, "Makefile"), "w") as f:
                f.write(makefile)
            # generate list of Heavy source files
            # files = os.listdir(source_dir)

            # ======================================================================================
            # Linux
            #
            # linux_path = os.path.join(out_dir, "linux")
            # os.makedirs(linux_path)

            buildjson.generate_json(
                out_dir,
                linux_x64_args=["-j"])
            # macos_x64_args=["-project", "{0}.xcodeproj".format(patch_name), "-arch",
            #                 "x86_64", "-alltargets"],
            # win_x64_args=["/property:Configuration=Release", "/property:Platform=x64",
            #               "/t:Rebuild", "{0}.sln".format(patch_name), "/m"],
            # win_x86_args=["/property:Configuration=Release", "/property:Platform=x86",
            #               "/t:Rebuild", "{0}.sln".format(patch_name), "/m"])

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
