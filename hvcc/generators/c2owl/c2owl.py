# import datetime
import hashlib
import os
import shutil
import time
import jinja2
import json
from ..buildjson import buildjson
from ..copyright import copyright_manager
import hvcc.core.hv2ir.HeavyLangObject as HeavyLangObject


heavy_hash = HeavyLangObject.HeavyLangObject.get_hash
OWL_BUTTONS = ['Push', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']


class c2owl:
    """ Generates a OWL wrapper for a given patch.
    """

    @classmethod
    def filter_uniqueid(clazz, s):
        """ Return a unique id (in hexadcemial) for the VST interface.
        """
        s = hashlib.md5(s.encode('utf-8'))
        s = s.hexdigest().upper()[0:8]
        s = f"0x{s}"
        return s

    @classmethod
    def compile(clazz, c_src_dir, out_dir, externs,
                patch_name=None, num_input_channels=0, num_output_channels=0,
                copyright=None, verbose=False):

        tick = time.time()

        def make_jdata(patch_ir):
            jdata = list()

            with open(patch_ir, mode="r") as f:
                ir = json.load(f)

                for name, v in ir['control']['receivers'].items():
                    # skip __hv_init and similar
                    if name.startswith("__"):
                        continue

                    # If a name has been specified
                    if 'owl' in v['attributes'] and v['attributes']['owl'] is not None:
                        key = v['attributes']['owl']
                        jdata.append((key, name, 'RECV', f"0x{heavy_hash(name)}",
                                      v['attributes']['min'],
                                      v['attributes']['max'],
                                      v['attributes']['default'],
                                      key in OWL_BUTTONS))

                    elif name.startswith('Channel-'):
                        key = name.split('Channel-', 1)[1]
                        jdata.append((key, name, 'RECV', f"0x{heavy_hash(name)}",
                                      0, 1, None, key in OWL_BUTTONS))

                for k, v in ir['objects'].items():
                    try:
                        if v['type'] == '__send':
                            name = v['args']['name']
                            if 'owl' in v['args']['attributes'] and v['args']['attributes']['owl'] is not None:
                                key = v['args']['attributes']['owl']
                                jdata.append((key, f'{name}>', 'SEND', f"0x{heavy_hash(name)}",
                                              v['args']['attributes']['min'],
                                              v['args']['attributes']['max'],
                                              v['args']['attributes']['default'],
                                              key in OWL_BUTTONS))
                            elif name.startswith('Channel-'):
                                key = name.split('Channel-', 1)[1]
                                jdata.append((key, f'{name}>', 'SEND', f"0x{heavy_hash(name)}",
                                              0, 1, None, key in OWL_BUTTONS))
                    except Exception:
                        pass

                return jdata

        patch_name = patch_name or "heavy"
        copyright_c = copyright_manager.get_copyright_for_c(copyright)

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

            # initialize the jinja template environment
            env = jinja2.Environment()
            env.filters["uniqueid"] = c2owl.filter_uniqueid

            env.loader = jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

            # construct jdata from ir
            ir_dir = os.path.join(c_src_dir, "../ir")
            patch_ir = os.path.join(ir_dir, f"{patch_name}.heavy.ir.json")
            jdata = make_jdata(patch_ir)

            # generate OWL wrapper from template
            owl_h_path = os.path.join(source_dir, f"HeavyOWL_{patch_name}.hpp")
            with open(owl_h_path, "w") as f:
                f.write(env.get_template("HeavyOwl.hpp").render(
                    jdata=jdata,
                    name=patch_name,
                    copyright=copyright_c))
            owl_h_path = os.path.join(source_dir, "HeavyOwlConstants.h")
            with open(owl_h_path, "w") as f:
                f.write(env.get_template("HeavyOwlConstants.h").render(
                    jdata=jdata,
                    copyright=copyright_c))

            # generate list of Heavy source files
            # files = os.listdir(source_dir)

            # ======================================================================================
            # Linux
            #
            # linux_path = os.path.join(out_dir, "linux")
            # os.makedirs(linux_path)

            # with open(os.path.join(source_dir, "Makefile"), "w") as f:
            #     f.write(env.get_template("Makefile").render(
            #         name=patch_name,
            #         class_name=f"HeavyOWL_{patch_name}"))

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
                "stage": "c2owl",
                "notifs": {
                    "has_error": False,
                    "exception": None,
                    "warnings": [],
                    "errors": []
                },
                "in_dir": c_src_dir,
                "in_file": "",
                "out_dir": out_dir,
                "out_file": os.path.basename(owl_h_path),
                "compile_time": time.time() - tick
            }

        except Exception as e:
            return {
                "stage": "c2owl",
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
