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

import datetime
import hashlib
import os
import shutil
import time
import jinja2
from ..buildjson import buildjson
from ..copyright import copyright_manager

class c2vst2:
    """ Generates a VST 2.4 wrapper for a given patch.
    """

    @classmethod
    def filter_uniqueid(clazz, s):
        """ Return a unique id (in hexadcemial) for the VST interface.
        """
        return "0x"+hashlib.md5(s).hexdigest().upper()[0:8]

    @classmethod
    def filter_xcode_build(clazz, s):
        """ Return a build hash suitable for use in an Xcode project file.
        """
        return hashlib.md5(s+"_build").hexdigest().upper()[0:24]

    @classmethod
    def filter_xcode_fileref(clazz, s):
        """ Return a fileref hash suitable for use in an Xcode project file.
        """
        return hashlib.md5(s+"_fileref").hexdigest().upper()[0:24]

    @classmethod
    def compile(clazz, c_src_dir, out_dir, externs,
        patch_name=None, num_input_channels=0, num_output_channels=0,
        copyright=None, verbose=False):

        tick = time.time()

        receiver_list = externs["parameters"]["in"]

        patch_name = patch_name or "heavy"

        copyright_c = copyright_manager.get_copyright_for_c(copyright)
        copyright_plist = copyright or "Copyright {0} Enzien Audio, Ltd. All Rights Reserved.".format(datetime.datetime.now().year)

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

            # initialise the jinja template environment
            env = jinja2.Environment()
            env.filters["uniqueid"] = c2vst2.filter_uniqueid
            env.filters["xcode_build"] = c2vst2.filter_xcode_build
            env.filters["xcode_fileref"] = c2vst2.filter_xcode_fileref
            env.loader = jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

            # generate VST2 wrapper from template
            vst_h_path = os.path.join(source_dir, "HeavyVst2_{0}.hpp".format(patch_name))
            with open(vst_h_path, "w") as f:
                f.write(env.get_template("HeavyVst2.hpp").render(
                    name=patch_name,
                    class_name="HeavyVst2_"+patch_name,
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    copyright=copyright_c))
            vst_cpp_path = os.path.join(source_dir, "HeavyVst2_{0}.cpp".format(patch_name))
            with open(vst_cpp_path, "w") as f:
                f.write(env.get_template("HeavyVst2.cpp").render(
                    name=patch_name,
                    class_name="HeavyVst2_"+patch_name,
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    pool_sizes_kb=externs["memoryPoolSizesKb"],
                    copyright=copyright_c))

            # generate list of Heavy source files
            files = os.listdir(source_dir)



            # ======================================================================================
            # Xcode
            #
            xcode_dir = os.path.join(out_dir, "xcode")
            xcodeproj_path = os.path.join(xcode_dir, "{0}.xcodeproj".format(patch_name))
            os.makedirs(xcodeproj_path) # create the xcode project bundle
            pbxproj_path = os.path.join(xcodeproj_path, "project.pbxproj")
            with open(pbxproj_path, "w") as f:
                f.write(env.get_template("xcode/project.pbxproj").render(
                    name=patch_name,
                    files=files))

            with open(os.path.join(xcode_dir, "Info.plist"), "w") as f:
                f.write(env.get_template("xcode/Info.plist").render(
                    copyright=copyright_plist))



            # ======================================================================================
            # VS2015
            #
            vs_dir = os.path.join(out_dir, "vs2015");
            os.mkdir(vs_dir) # create the vs2015 directory
            sln_path = os.path.join(vs_dir, "{0}.sln".format(patch_name))
            with open(sln_path, "w") as f:
                f.write(env.get_template("vs2015/project.sln").render(
                    name=patch_name))
            vcxproj_path = os.path.join(vs_dir, "{0}.vcxproj".format(patch_name))
            with open(vcxproj_path, "w") as f:
                f.write(env.get_template("vs2015/project.vcxproj").render(
                    name=patch_name,
                    files=files))



            # ======================================================================================
            # Linux
            #
            linux_path = os.path.join(out_dir, "linux")
            os.makedirs(linux_path)

            with open(os.path.join(linux_path, "Makefile"), "w") as f:
                f.write(env.get_template("linux/Makefile").render(
                    name=patch_name))

            buildjson.generate_json(
                out_dir,
                linux_x64_args=["-j"],
                macos_x64_args=["-project", "{0}.xcodeproj".format(patch_name), "-arch", "x86_64", "-alltargets"],
                win_x64_args=["/property:Configuration=Release", "/property:Platform=x64", "/t:Rebuild", "{0}.sln".format(patch_name), "/m"],
                win_x86_args=["/property:Configuration=Release", "/property:Platform=x86", "/t:Rebuild", "{0}.sln".format(patch_name), "/m"])

            return {
                "stage": "c2vst2",
                "notifs": {
                    "has_error": False,
                    "exception": None,
                    "warnings": [],
                    "errors": []
                },
                "in_dir": c_src_dir,
                "in_file": "",
                "out_dir": out_dir,
                "out_file": os.path.basename(vst_h_path),
                "compile_time": time.time()-tick
            }

        except Exception as e:
            return  {
                "stage": "c2vst2",
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
                "compile_time": time.time()-tick
            }
