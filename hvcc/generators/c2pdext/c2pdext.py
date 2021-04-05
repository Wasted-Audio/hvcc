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
import os
import shutil
import time
import jinja2
from ..copyright import copyright_manager


class c2pdext:
    """Generates a Pure Data external wrapper for a given patch.
    """

    @classmethod
    def filter_max(clazz, i, j):
        """Calculate the maximum of two integers.
        """
        return max(int(i), int(j))

    @classmethod
    def filter_xcode_build(clazz, s):
        """Return a build hash suitable for use in an Xcode project file.
        """
        s = f"{s}_build"
        s = hashlib.md5(s.encode('utf-8'))
        s = s.hexdigest().upper()[0:24]
        return s

    @classmethod
    def filter_xcode_fileref(clazz, s):
        """Return a fileref hash suitable for use in an Xcode project file.
        """
        s = f"{s}_fileref"
        s = hashlib.md5(s.encode('utf-8'))
        s = s.hexdigest().upper()[0:24]
        return s

    @classmethod
    def compile(clazz, c_src_dir, out_dir, externs,
                patch_name=None, ext_name=None,
                num_input_channels=0, num_output_channels=0,
                copyright=None, verbose=False):

        tick = time.time()
        receiver_list = externs["parameters"]["in"]

        copyright = copyright_manager.get_copyright_for_c(copyright)

        patch_name = patch_name or "heavy"
        ext_name = ext_name or (patch_name + "~")
        struct_name = patch_name + "_tilde"

        # ensure that the output directory does not exist
        out_dir = os.path.abspath(out_dir)
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        # copy over generated C source files
        shutil.copytree(c_src_dir, out_dir)

        # copy over static files
        shutil.copy(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "m_pd.h"),
            out_dir)

        try:
            # initialise the jinja template environment
            env = jinja2.Environment()
            env.filters["max"] = c2pdext.filter_max
            env.filters["xcode_build"] = c2pdext.filter_xcode_build
            env.filters["xcode_fileref"] = c2pdext.filter_xcode_fileref
            env.loader = jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

            # generate Pd external wrapper from template
            pdext_path = os.path.join(out_dir, "{0}.c".format(struct_name))
            with open(pdext_path, "w") as f:
                f.write(env.get_template("pd_external.c").render(
                    name=patch_name,
                    struct_name=struct_name,
                    display_name=ext_name,
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    copyright=copyright))

            # generate Xcode project
            xcode_path = os.path.join(out_dir, "{0}.xcodeproj".format(struct_name))
            os.mkdir(xcode_path)  # create the xcode project bundle
            pbxproj_path = os.path.join(xcode_path, "project.pbxproj")

            # generate list of source files
            files = [g for g in os.listdir(out_dir) if g.endswith((".h", ".hpp", ".c", ".cpp"))]

            # render the pbxproj file
            with open(pbxproj_path, "w") as f:
                f.write(env.get_template("project.pbxproj").render(
                    name=ext_name,
                    files=files))

            return {
                "stage": "c2pdext",
                "notifs": {
                    "has_error": False,
                    "exception": None,
                    "warnings": [],
                    "errors": []
                },
                "in_dir": c_src_dir,
                "in_file": "",
                "out_dir": out_dir,
                "out_file": os.path.basename(pdext_path),
                "compile_time": time.time() - tick
            }

        except Exception as e:
            return {
                "stage": "c2pdext",
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
                "out_file": os.path.basename(pdext_path),
                "compile_time": time.time() - tick
            }
