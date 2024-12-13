# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2021-2024 Wasted Audio
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
from typing import Optional

from ..copyright import copyright_manager
from ..filters import filter_max

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.compiler import Generator, CompilerResp, CompilerNotif, CompilerMsg, ExternInfo
from hvcc.types.meta import Meta


class c2pdext(Generator):
    """Generates a Pure Data external wrapper for a given patch.
    """

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

        out_dir = os.path.join(out_dir, "pdext")
        receiver_list = externs.parameters.inParam

        copyright = copyright_manager.get_copyright_for_c(copyright)

        patch_name = patch_name or "heavy"
        ext_name = f"{patch_name}~"
        struct_name = f"{patch_name}_tilde"

        # ensure that the output directory does not exist
        out_dir = os.path.abspath(out_dir)
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        # copy over generated C source files
        shutil.copytree(c_src_dir, out_dir)

        # copy over static files
        shutil.copy(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "m_pd.h"),
            f"{out_dir}/")
        shutil.copy(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "Makefile.pdlibbuilder"),
            f"{out_dir}/../")

        try:
            # initialise the jinja template environment
            env = jinja2.Environment()
            env.filters["max"] = filter_max
            env.loader = jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

            # generate Pd external wrapper from template
            pdext_path = os.path.join(out_dir, f"{ext_name}.c")
            with open(pdext_path, "w") as f:
                f.write(env.get_template("pd_external.c").render(
                    name=patch_name,
                    struct_name=struct_name,
                    display_name=ext_name,
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    copyright=copyright))

            # generate Makefile from template
            pdext_path = os.path.join(out_dir, "../Makefile")
            with open(pdext_path, "w") as f:
                f.write(env.get_template("Makefile").render(
                    name=patch_name))

            return CompilerResp(
                stage="c2pdext",
                in_dir=c_src_dir,
                out_dir=out_dir,
                out_file=os.path.basename(pdext_path),
                compile_time=time.time() - tick
            )

        except Exception as e:
            return CompilerResp(
                stage="c2pdext",
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
