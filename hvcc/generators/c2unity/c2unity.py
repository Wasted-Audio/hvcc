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

import hashlib
import jinja2
import os
import shutil
import time
from ..copyright import copyright_manager
from ..buildjson import buildjson


class c2unity:
    """Generates a Audio Native Plugin wrapper for Unity 5.
    """

    @classmethod
    def filter_xcode_build(clazz, s):
        """Return a build hash suitable for use in an Xcode project file.
        """
        return hashlib.md5(s + "_build").hexdigest().upper()[0:24]

    @classmethod
    def filter_xcode_fileref(clazz, s):
        """Return a fileref hash suitable for use in an Xcode project file.
        """
        return hashlib.md5(s + "_fileref").hexdigest().upper()[0:24]

    @classmethod
    def filter_string_cap(clazz, s, li):
        """Returns a truncated string with ellipsis if it exceeds a certain length.
        """
        return s if (len(s) <= li) else s[0:li - 3] + "..."

    @classmethod
    def filter_templates(clazz, template_name):
        return False if os.path.basename(template_name) in [".DS_Store"] else True

    @classmethod
    def compile(clazz, c_src_dir, out_dir, externs,
                patch_name=None, num_input_channels=0, num_output_channels=0,
                copyright=None, verbose=False):

        tick = time.time()

        parameter_list = externs["parameters"]["in"]
        event_list = externs["events"]["in"]
        table_list = externs["tables"]

        patch_name = patch_name or "heavy"

        copyright = copyright_manager.get_copyright_for_c(copyright)

        # initialise the jinja template environment
        env = jinja2.Environment()
        env.filters["xcode_build"] = c2unity.filter_xcode_build
        env.filters["xcode_fileref"] = c2unity.filter_xcode_fileref
        env.filters["cap"] = c2unity.filter_string_cap
        env.loader = jinja2.FileSystemLoader(
            encoding="utf-8-sig",
            searchpath=[os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")])

        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        src_out_dir = os.path.join(out_dir, "source")

        try:
            # ensure that the output directory does not exist
            out_dir = os.path.abspath(out_dir)
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)

            # copy over static files
            shutil.copytree(static_dir, out_dir)

            # copy over generated C source files
            src_out_dir = os.path.join(out_dir, "source", "heavy")
            shutil.copytree(c_src_dir, src_out_dir)

            # generate files from templates
            for f in env.list_templates(filter_func=c2unity.filter_templates):
                file_path = os.path.join(out_dir, f)
                file_path = file_path.replace("{{name}}", patch_name)

                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))

                with open(file_path, "w") as g:
                    g.write(env.get_template(f).render(
                        patch_name=patch_name,
                        files=os.listdir(src_out_dir),
                        num_input_channels=num_input_channels,
                        num_output_channels=num_output_channels,
                        parameters=parameter_list,
                        events=event_list,
                        tables=table_list,
                        pool_sizes_kb=externs["memoryPoolSizesKb"],
                        compile_files=os.listdir(src_out_dir),
                        copyright=copyright))

            buildjson.generate_json(
                out_dir,
                android_armv7a_args=["APP_ABI=armeabi-v7a", "-j"],
                linux_x64_args=["-j"],
                macos_x64_args=["-project", "Hv_{0}_Unity.xcodeproj".format(patch_name),
                                "-arch", "x86_64", "-alltargets"],
                win_x64_args=["/property:Configuration=Release", "/property:Platform=x64",
                              "/t:Rebuild", "Hv_{0}_Unity.sln".format(patch_name), "/m"],
                win_x86_args=["/property:Configuration=Release", "/property:Platform=x86",
                              "/t:Rebuild", "Hv_{0}_Unity.sln".format(patch_name), "/m"])

            return {
                "stage": "c2unity",
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
                "stage": "c2unity",
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
