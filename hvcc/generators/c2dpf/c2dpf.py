# Copyright (C) 2021-2023 Wasted Audio
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
import shutil
import time
import jinja2
from typing import Dict, Optional

from ..copyright import copyright_manager
from ..filters import filter_uniqueid


class c2dpf:
    """ Generates a DPF wrapper for a given patch.
    """

    @classmethod
    def compile(
        cls,
        c_src_dir: str,
        out_dir: str,
        externs: Dict,
        patch_name: Optional[str] = None,
        patch_meta: Optional[Dict] = None,
        num_input_channels: int = 0,
        num_output_channels: int = 0,
        copyright: Optional[str] = None,
        verbose: Optional[bool] = False
    ) -> Dict:

        tick = time.time()

        out_dir = os.path.join(out_dir, "plugin")
        receiver_list = externs['parameters']['in']

        if patch_meta:
            patch_name = patch_meta.get("name", patch_name)
            dpf_meta = patch_meta.get("dpf", {})
        else:
            dpf_meta = {}

        dpf_path = dpf_meta.get('dpf_path', '')

        copyright_c = copyright_manager.get_copyright_for_c(copyright)

        try:
            # ensure that the output directory does not exist
            out_dir = os.path.abspath(out_dir)
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)

            # copy over static files
            shutil.copytree(os.path.join(os.path.dirname(__file__), "static"), out_dir)
            shutil.copy(os.path.join(os.path.dirname(__file__), "static/README.md"), f'{out_dir}/../')

            # copy over generated C source files
            source_dir = os.path.join(out_dir, "source")
            shutil.copytree(c_src_dir, source_dir)

            # initialize the jinja template environment
            env = jinja2.Environment()
            env.filters["uniqueid"] = filter_uniqueid

            env.loader = jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

            # generate DPF wrapper from template
            dpf_h_path = os.path.join(source_dir, f"HeavyDPF_{patch_name}.hpp")
            with open(dpf_h_path, "w") as f:
                f.write(env.get_template("HeavyDPF.hpp").render(
                    name=patch_name,
                    meta=dpf_meta,
                    class_name=f"HeavyDPF_{patch_name}",
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    copyright=copyright_c))
            dpf_cpp_path = os.path.join(source_dir, f"HeavyDPF_{patch_name}.cpp")
            with open(dpf_cpp_path, "w") as f:
                f.write(env.get_template("HeavyDPF.cpp").render(
                    name=patch_name,
                    meta=dpf_meta,
                    class_name=f"HeavyDPF_{patch_name}",
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    pool_sizes_kb=externs["memoryPoolSizesKb"],
                    copyright=copyright_c))
            if dpf_meta.get("enable_ui"):
                dpf_ui_path = os.path.join(source_dir, f"HeavyDPF_{patch_name}_UI.cpp")
                with open(dpf_ui_path, "w") as f:
                    f.write(env.get_template("HeavyDPF_UI.cpp").render(
                        name=patch_name,
                        meta=dpf_meta,
                        class_name=f"HeavyDPF_{patch_name}",
                        num_input_channels=num_input_channels,
                        num_output_channels=num_output_channels,
                        receivers=receiver_list,
                        copyright=copyright_c))
            dpf_h_path = os.path.join(source_dir, "DistrhoPluginInfo.h")
            with open(dpf_h_path, "w") as f:
                f.write(env.get_template("DistrhoPluginInfo.h").render(
                    name=patch_name,
                    meta=dpf_meta,
                    class_name=f"HeavyDPF_{patch_name}",
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    pool_sizes_kb=externs["memoryPoolSizesKb"],
                    copyright=copyright_c))

            # plugin makefile
            with open(os.path.join(source_dir, "Makefile"), "w") as f:
                f.write(env.get_template("Makefile_plugin").render(
                    name=patch_name,
                    meta=dpf_meta,
                    dpf_path=dpf_path))

            # project makefile
            with open(os.path.join(source_dir, "../../Makefile"), "w") as f:
                f.write(env.get_template("Makefile_project").render(
                    name=patch_name,
                    meta=dpf_meta,
                    dpf_path=dpf_path))

            return {
                "stage": "c2dpf",
                "notifs": {
                    "has_error": False,
                    "exception": None,
                    "warnings": [],
                    "errors": []
                },
                "in_dir": c_src_dir,
                "in_file": "",
                "out_dir": out_dir,
                "out_file": os.path.basename(dpf_h_path),
                "compile_time": time.time() - tick
            }

        except Exception as e:
            return {
                "stage": "c2dpf",
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
