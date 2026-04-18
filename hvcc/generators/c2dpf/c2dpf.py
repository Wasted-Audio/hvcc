# Copyright (C) 2021-2026 Wasted Audio
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
import shutil
import time

from typing import Optional
from pathlib import Path

from ..copyright import copyright_manager
from ..filters import filter_uniqueid

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.compiler import Generator, CompilerResp, CompilerMsg, CompilerNotif, ExternInfo
from hvcc.types.meta import Meta, DPF


class c2dpf(Generator):
    """ Generates a DPF wrapper for a given patch.
    """

    @classmethod
    def compile(
        cls,
        c_src_dir: Path,
        out_dir: Path,
        externs: ExternInfo,
        patch_name: Optional[str] = None,
        patch_meta: Meta = Meta(),
        num_input_channels: int = 0,
        num_output_channels: int = 0,
        copyright: Optional[str] = None,
        verbose: Optional[bool] = False
    ) -> CompilerResp:

        tick = time.time()

        out_dir = Path(out_dir, "plugin")
        receiver_list = externs.parameters.inParam
        sender_list = externs.parameters.outParam

        dpf_meta: DPF = patch_meta.dpf
        dpf_path = dpf_meta.dpf_path

        copyright_c = copyright_manager.get_copyright_for_c(copyright)

        try:
            # ensure that the output directory does not exist
            out_dir = out_dir.absolute()
            if out_dir.exists():
                shutil.rmtree(out_dir)

            # copy over static files
            shutil.copytree(Path(Path(__file__).parent, "static"), out_dir)
            shutil.copy(Path(Path(__file__).parent, "static/README.md"), f'{out_dir}/../')

            # copy over generated C source files
            source_dir = Path(out_dir, "source")
            shutil.copytree(c_src_dir, source_dir)

            # initialize the jinja template environment
            env = jinja2.Environment()
            env.filters["uniqueid"] = filter_uniqueid

            env.loader = jinja2.FileSystemLoader(
                Path(Path(__file__).parent, "templates"))

            # generate DPF wrapper from template
            dpf_h_path = Path(source_dir, f"HeavyDPF_{patch_name}.hpp")
            with open(dpf_h_path, "w") as f:
                f.write(env.get_template("HeavyDPF.hpp").render(
                    name=patch_name,
                    meta=dpf_meta,
                    class_name=f"HeavyDPF_{patch_name}",
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    senders=sender_list,
                    copyright=copyright_c))
            dpf_cpp_path = Path(source_dir, f"HeavyDPF_{patch_name}.cpp")
            with open(dpf_cpp_path, "w") as f:
                f.write(env.get_template("HeavyDPF.cpp").render(
                    name=patch_name,
                    meta=dpf_meta,
                    class_name=f"HeavyDPF_{patch_name}",
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    senders=sender_list,
                    pool_sizes_kb=externs.memoryPoolSizesKb,
                    copyright=copyright_c))
            if dpf_meta.enable_ui:
                dpf_ui_path = Path(source_dir, f"HeavyDPF_{patch_name}_UI.cpp")
                with open(dpf_ui_path, "w") as f:
                    f.write(env.get_template("HeavyDPF_UI.cpp").render(
                        name=patch_name,
                        meta=dpf_meta,
                        class_name=f"HeavyDPF_{patch_name}",
                        receivers=receiver_list,
                        senders=sender_list,
                        copyright=copyright_c))
            dpf_h_path = Path(source_dir, "DistrhoPluginInfo.h")
            with open(dpf_h_path, "w") as f:
                f.write(env.get_template("DistrhoPluginInfo.h").render(
                    name=patch_name,
                    meta=dpf_meta,
                    class_name=f"HeavyDPF_{patch_name}",
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    pool_sizes_kb=externs.memoryPoolSizesKb,
                    copyright=copyright_c))

            # plugin makefile
            with open(Path(source_dir, "Makefile"), "w") as f:
                f.write(env.get_template("Makefile_plugin").render(
                    name=patch_name,
                    meta=dpf_meta,
                    nosimd=patch_meta.nosimd,
                    dpf_path=dpf_path))

            # project makefile
            with open(Path(source_dir, "../../Makefile"), "w") as f:
                f.write(env.get_template("Makefile_project").render(
                    name=patch_name,
                    meta=dpf_meta,
                    dpf_path=dpf_path))

            return CompilerResp(
                stage="c2dpf",
                in_dir=c_src_dir,
                out_dir=out_dir,
                out_file=dpf_h_path,
                compile_time=time.time() - tick
            )

        except Exception as e:
            return CompilerResp(
                stage="c2dpf",
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
