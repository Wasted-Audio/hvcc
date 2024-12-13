# import datetime
import os
import shutil
import time
import jinja2
import json
from typing import List, Optional

import hvcc.core.hv2ir.HeavyLangObject as HeavyLangObject
from ..copyright import copyright_manager

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.compiler import Generator, CompilerResp, CompilerNotif, CompilerMsg, ExternInfo
from hvcc.types.meta import Meta
from hvcc.types.IR import IRGraph


heavy_hash = HeavyLangObject.HeavyLangObject.get_hash
OWL_BUTTONS = ['Push', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']


class c2owl(Generator):
    """ Generates a OWL wrapper for a given patch.
    """

    @classmethod
    def make_jdata(cls, patch_ir: str) -> List:
        jdata = list()

        with open(patch_ir, mode="r") as f:
            ir = IRGraph(**json.load(f))

            for name, recv in ir.control.receivers.items():
                # skip __hv_init and similar
                if name.startswith("__"):
                    continue

                # If a name has been specified
                if recv.attributes.get('raw'):
                    key = recv.attributes['raw']
                    jdata.append((key, name, 'RECV', f"0x{heavy_hash(name):X}",
                                  recv.attributes['min'],
                                  recv.attributes['max'],
                                  recv.attributes['default'],
                                  key in OWL_BUTTONS))

                elif name.startswith('Channel-'):
                    key = name.split('Channel-', 1)[1]
                    jdata.append((key, name, 'RECV', f"0x{heavy_hash(name):X}",
                                  0, 1, None, key in OWL_BUTTONS))

            for _, obj in ir.objects.items():
                try:
                    if obj.type == '__send':
                        name = obj.args['name']
                        if obj.args['attributes'].get('raw'):
                            key = obj.args['attributes']['raw']
                            jdata.append((key, f'{name}>', 'SEND', f"0x{heavy_hash(name):X}",
                                          obj.args['attributes']['min'],
                                          obj.args['attributes']['max'],
                                          obj.args['attributes']['default'],
                                          key in OWL_BUTTONS))
                        elif name.startswith('Channel-'):
                            key = name.split('Channel-', 1)[1]
                            jdata.append((key, f'{name}>', 'SEND', f"0x{heavy_hash(name):X}",
                                          0, 1, None, key in OWL_BUTTONS))
                except Exception:
                    pass

            return jdata

    @classmethod
    def compile(
        cls,
        c_src_dir: str,
        out_dir: str,
        externs: ExternInfo,
        patch_name: Optional[str] = None,
        patch_meta: Meta = Meta(),
        num_input_channels: int = 0,
        num_output_channels: int = 0,
        copyright: Optional[str] = None,
        verbose: Optional[bool] = False
    ) -> CompilerResp:

        tick = time.time()

        out_dir = os.path.join(out_dir, "Source")
        patch_name = patch_name or "heavy"
        copyright_c = copyright_manager.get_copyright_for_c(copyright)

        try:
            # ensure that the output directory does not exist
            out_dir = os.path.abspath(out_dir)
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)

            # copy over generated C source files
            shutil.copytree(c_src_dir, out_dir)

            # copy over deps
            shutil.copytree(os.path.join(os.path.dirname(__file__), "deps"), out_dir, dirs_exist_ok=True)

            # initialize the jinja template environment
            env = jinja2.Environment()

            env.loader = jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

            # construct jdata from ir
            ir_dir = os.path.join(c_src_dir, "../ir")
            patch_ir = os.path.join(ir_dir, f"{patch_name}.heavy.ir.json")
            jdata = cls.make_jdata(patch_ir)

            # generate OWL wrapper from template
            owl_hpp_path = os.path.join(out_dir, f"HeavyOWL_{patch_name}.hpp")
            with open(owl_hpp_path, "w") as f:
                f.write(env.get_template("HeavyOwl.hpp").render(
                    jdata=jdata,
                    name=patch_name,
                    copyright=copyright_c))
            owl_h_path = os.path.join(out_dir, "HeavyOwlConstants.h")
            with open(owl_h_path, "w") as f:
                f.write(env.get_template("HeavyOwlConstants.h").render(
                    jdata=jdata,
                    copyright=copyright_c))

            # ======================================================================================

            return CompilerResp(
                stage="c2owl",
                in_dir=c_src_dir,
                out_dir=out_dir,
                out_file=os.path.basename(owl_h_path),
                compile_time=time.time() - tick
            )

        except Exception as e:
            return CompilerResp(
                stage="c2owl",
                notifs=CompilerNotif(
                    has_error=True,
                    exception=e,
                    warnings=[],
                    errors=[CompilerMsg(
                        enum=NotificationEnum.ERROR_EXCEPTION,
                        message=str(e)
                    )]
                ),
                in_dir=c_src_dir,
                out_dir=out_dir,
                compile_time=time.time() - tick
            )
