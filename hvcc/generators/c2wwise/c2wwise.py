# Copyright (C) 2014-2018 Enzien Audio, Ltd.
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

from ..buildjson import buildjson
from ..copyright import copyright_manager
from ..filters import filter_plugin_id, filter_xcode_build, filter_xcode_fileref


class c2wwise:
    """Generates a plugin wrapper for Audiokinetic's Wwise game audio middleware
    platform.
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
        event_list = externs["events"]["in"]
        table_list = externs["tables"]

        out_dir = os.path.join(out_dir, "wwise")
        patch_name = patch_name or "heavy"

        copyright_c = copyright_manager.get_copyright_for_c(copyright)
        copyright_xml = copyright_manager.get_copyright_for_xml(copyright)

        wwise_sdk_version = "2017.2.2.6553"

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        plugin_type = "Source" if num_input_channels == 0 else "FX"
        plugin_id = filter_plugin_id(patch_name)

        env = jinja2.Environment()
        env.filters["xcode_build"] = filter_xcode_build
        env.filters["xcode_fileref"] = filter_xcode_fileref
        env.loader = jinja2.FileSystemLoader(
            encoding="utf-8-sig",
            searchpath=[templates_dir])

        try:
            if plugin_type == "FX":
                if num_input_channels > 2:
                    raise Exception("Wwise FX plugins support a maximum of 2 channels (i.e. [adc~ 1] or [adc~ 1 2]).")
                if num_input_channels != num_output_channels:
                    raise Exception("Wwise FX plugins require the same input/output channel"
                                    "configuration (i.e. [adc~ 1] -> [dac~ 1]).")

            # copy over generated C source files
            patch_src_dir = os.path.join(out_dir, "source", "heavy")
            if os.path.exists(patch_src_dir):
                shutil.rmtree(patch_src_dir)
            shutil.copytree(c_src_dir, patch_src_dir)

            # template all source files
            src_extns = ["h", "hpp", "c", "cpp", "xml", "def", "rc", "plist"]
            for f in env.list_templates(extensions=src_extns):
                file_dir = os.path.join(out_dir, os.path.dirname(f))
                file_name = os.path.basename(f)

                # ignore source plugin files if type is FX
                if (file_dir.endswith("plugin_source") and plugin_type != "Source"):
                    continue

                # ignore fx plugin files if type is Source
                elif (file_dir.endswith("plugin_fx") and plugin_type != "FX"):
                    continue

                # static files
                if file_name in ["stdafx.h", "Info.plist"]:
                    file_path = os.path.join(file_dir, file_name)

                    if not os.path.exists(os.path.dirname(file_path)):
                        os.makedirs(os.path.dirname(file_path))

                    shutil.copyfile(os.path.join(templates_dir, f), file_path)

                # templated files
                else:
                    file_name = file_name.replace("{{name}}", patch_name)
                    file_name = file_name.replace("{{type}}", plugin_type)
                    file_path = os.path.join(file_dir, file_name)

                    if not os.path.exists(os.path.dirname(file_path)):
                        os.makedirs(os.path.dirname(file_path))

                    with open(file_path, "w") as g:
                        g.write(env.get_template(f).render(
                            name=patch_name,
                            parameters=in_parameter_list,
                            sends=out_parameter_list,
                            events=event_list,
                            tables=table_list,
                            pool_sizes_kb=externs["memoryPoolSizesKb"],
                            plugin_type=plugin_type,
                            plugin_id=plugin_id,
                            copyright=copyright_xml if file_name.endswith(".xml") else copyright_c))

            files = [f for f in os.listdir(patch_src_dir)]

            # template all ide project files
            for f in env.list_templates(extensions=["vcxproj", "sln", "pbxproj", "xcconfig"]):

                # xcode projects are structured differently to visual studio projects
                if f.endswith("pbxproj"):
                    xcode_proj_dir = os.path.splitext(os.path.dirname(f))
                    file_path = os.path.join(
                        out_dir,
                        os.path.dirname(xcode_proj_dir[0]),
                        f"Hv_ {patch_name}_Wwise {plugin_type}"
                        f" {os.path.basename(xcode_proj_dir[0])} {xcode_proj_dir[1]}",
                        os.path.basename(f))
                else:
                    file_path = f.replace("{{name}}", patch_name)
                    file_path = file_path.replace("{{type}}", plugin_type)
                    file_path = os.path.join(out_dir, file_path.replace("{{type}}", plugin_type))

                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))

                with open(file_path, "w") as g:
                    g.write(env.get_template(f).render(
                        name=patch_name,
                        parameters=in_parameter_list,
                        sends=out_parameter_list,
                        events=event_list,
                        tables=table_list,
                        plugin_type=plugin_type,
                        plugin_id=plugin_id,
                        wwise_version=wwise_sdk_version,
                        msbuild_version="140",
                        files=files))

            # linux makefile
            linux_makefile = os.path.join(out_dir, "linux", "Makefile")

            if not os.path.exists(os.path.dirname(linux_makefile)):
                os.makedirs(os.path.dirname(linux_makefile))

            with open(linux_makefile, "w") as g:
                g.write(env.get_template("linux/Makefile").render(
                    name=patch_name,
                    plugin_type=plugin_type,
                    plugin_id=plugin_id,
                    files=files,
                    wwise_version=wwise_sdk_version))

            proj_name = f"Hv_{patch_name}_Wwise{plugin_type}Plugin"

            buildjson.generate_json(
                out_dir,
                ios_armv7a_args=[
                    "-arch", "armv7s",
                    "-target", f"{proj_name}_iOS",
                    "-project", f"{proj_name}.xcodeproj"],
                linux_x64_args=["-j"],
                macos_x64_args=[
                    "-arch", "x86_64",
                    "-target", f"{proj_name}",
                    "-project", f"{proj_name}.xcodeproj"],
                win_x64_args=[
                    "/property:Configuration=Release",
                    "/property:Platform=x64",
                    "/t:Rebuild", "/m",
                    f"{proj_name}.sln"],
                win_x86_args=[
                    "/property:Configuration=Release",
                    "/property:Platform=x86",
                    "/t:Rebuild", "/m",
                    f"{proj_name}.sln"])

            return {
                "stage": "c2wwise",
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
                "stage": "c2wwise",
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
