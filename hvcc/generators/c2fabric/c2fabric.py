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

import jinja2
import os
import shutil
import time
from typing import Dict, Optional

from ..buildjson import buildjson
from ..copyright import copyright_manager
from ..filters import filter_templates, filter_xcode_build, filter_xcode_copy, filter_xcode_fileref


class c2fabric:
    """Generates a DSP component for Fabric.
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

        in_parameter_list = externs["parameters"]["in"]
        out_parameter_list = externs["parameters"]["out"]
        in_event_list = externs["events"]["in"]
        out_event_list = externs["events"]["out"]

        out_dir = os.path.join(out_dir, "fabric")
        patch_name = patch_name or "heavy"

        copyright = copyright_manager.get_copyright_for_c(copyright)

        # initialise the jinja template environment
        env = jinja2.Environment()
        env.filters["xcode_build"] = filter_xcode_build
        env.filters["xcode_copy"] = filter_xcode_copy
        env.filters["xcode_fileref"] = filter_xcode_fileref
        env.loader = jinja2.FileSystemLoader(
            encoding="utf-8-sig",
            searchpath=[os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")])

        src_out_dir = os.path.join(out_dir, "source")

        try:
            # ensure that the output directory does not exist
            out_dir = os.path.abspath(out_dir)
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)

            # copy over generated C source files
            src_out_dir = os.path.join(out_dir, "source", "heavy")
            shutil.copytree(c_src_dir, src_out_dir)

            files_to_copy = [f"Hv_{patch_name}_FabricDSP.cs", f"Hv_{patch_name}_FabricDSPEditor.cs"]

            # generate files from templates
            for f in env.list_templates(filter_func=filter_templates):
                file_path = os.path.join(out_dir, f)
                file_path = file_path.replace("{{name}}", patch_name)

                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))

                with open(file_path, "w") as g:
                    g.write(env.get_template(f).render(
                        patch_name=patch_name,
                        project_name=f"Hv_{patch_name}_Fabric",
                        lib_name=patch_name,
                        num_input_channels=num_input_channels,
                        num_output_channels=num_output_channels,
                        in_parameters=in_parameter_list,
                        out_parameters=out_parameter_list,
                        in_events=in_event_list,
                        out_events=out_event_list,
                        compile_files=os.listdir(src_out_dir),
                        copy_files=files_to_copy,
                        copyright=copyright))

            buildjson.generate_json(
                out_dir,
                android_armv7a_args=["APP_ABI=armeabi-v7a", "-j"],
                linux_x64_args=["-j"],
                macos_x64_args=["-project", f"Hv_{patch_name}_Fabric.xcodeproj",
                                "-arch", "x86_64", "-alltargets"],
                win_x64_args=["/property:Configuration=Release", "/property:Platform=x64",
                              "/t:Rebuild", f"Hv_{patch_name}_Fabric.sln", "/m"],
                win_x86_args=["/property:Configuration=Release", "/property:Platform=x86",
                              "/t:Rebuild", f"Hv_{patch_name}_Fabric.sln", "/m"])

            return {
                "stage": "c2fabric",
                "notifs": {
                    "has_error": False,
                    "exception": None,
                    "warnings": [],
                    "errors": []
                },
                "in_dir": c_src_dir,
                "in_file": "",
                "out_dir": out_dir,
                "out_file": "",
                "compile_time": time.time() - tick
            }

        except Exception as e:
            return {
                "stage": "c2fabric",
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
