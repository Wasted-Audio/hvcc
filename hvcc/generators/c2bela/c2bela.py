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
from ..buildjson import buildjson


class c2bela:
    """ Generates a makefile to compile source to object files suitable for the
        bela platform.
    """

    @classmethod
    def compile(clazz, c_src_dir, out_dir, externs,
                patch_name=None, num_input_channels=0, num_output_channels=0,
                copyright=None, verbose=False):

        tick = time.time()
        patch_name = patch_name or "heavy"

        try:
            # ensure that the output directory does not exist
            out_dir = os.path.abspath(out_dir)
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)

            # copy over generated C source files
            shutil.copytree(c_src_dir, os.path.join(out_dir, "source"))

            # initialise the jinja template environment
            env = jinja2.Environment()
            env.loader = jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

            # make sure directories exist
            makefile_path = os.path.join(out_dir, "linux", "Makefile")
            if not os.path.exists(os.path.dirname(makefile_path)):
                os.makedirs(os.path.dirname(makefile_path))

            # generate linux makefile
            with open(makefile_path, "w") as f:
                f.write(env.get_template("linux/Makefile").render(name=patch_name))

            # generate build json file
            buildjson.generate_json(
                out_dir,
                linux_armv7a_args=["-j"])

            return {
                "stage": "c2bela",
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
                "stage": "c2bela",
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
