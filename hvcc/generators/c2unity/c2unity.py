# Copyright (C) 2014-2018 Enzien Audio, Ltd.
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
import os
import shutil
import time

from typing import Optional
from pathlib import Path

from ..copyright import copyright_manager
from ..filters import filter_templates

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.compiler import Generator, CompilerResp, CompilerNotif, CompilerMsg, ExternInfo
from hvcc.types.meta import Meta


class c2unity(Generator):
    """Generates a Audio Native Plugin wrapper for Unity 5.
    """

    @classmethod
    def compile(
        cls,
        c_src_dir: Path,
        out_dir: Path,
        externs: ExternInfo,
        patch_name: str,
        patch_meta: Meta = Meta(),
        num_input_channels: int = 0,
        num_output_channels: int = 0,
        copyright: Optional[str] = None,
        verbose: Optional[bool] = False
    ) -> CompilerResp:

        tick = time.time()

        in_parameter_list = externs.parameters.inParam
        out_parameter_list = externs.parameters.outParam
        event_list = externs.events.inEvent
        out_event_list = externs.events.outEvent
        table_list = externs.tables

        out_dir = Path(out_dir, "unity")
        patch_name = patch_name.lower() if patch_name is not None else "heavy"

        copyright_c = copyright_manager.get_copyright_for_c(copyright)

        templates_dir = Path(Path(__file__).parent, "templates")

        # initialise the jinja template environment
        env = jinja2.Environment()

        env.loader = jinja2.FileSystemLoader(
            encoding="utf-8-sig", searchpath=[templates_dir]
        )

        try:
            # ensure that the output directory does not exist
            out_dir = out_dir.absolute()
            if out_dir.exists():
                shutil.rmtree(out_dir)

            patch_src_dir = Path(out_dir, "include", "Heavy")
            if patch_src_dir.exists():
                shutil.rmtree(patch_src_dir)
            shutil.copytree(c_src_dir, patch_src_dir)

            heavy_src_files = [f for f in os.listdir(c_src_dir) if f.endswith(".c") or f.endswith(".cpp")]

            # generate files from templates
            for f in env.list_templates(filter_func=filter_templates):
                file_path = Path(out_dir, f)
                file_path = Path(str(file_path).replace("{{name}}", patch_name))

                if not file_path.parent.exists():
                    os.makedirs(file_path.parent)

                with open(file_path, "w") as g:
                    g.write(env.get_template(f).render(
                        name=patch_name,
                        in_params=in_parameter_list,
                        out_params=out_parameter_list,
                        out_events=out_event_list,
                        events=event_list,
                        tables=table_list,
                        pool_sizes_kb=externs.memoryPoolSizesKb,
                        num_input_channels=num_input_channels,
                        num_output_channels=num_output_channels,
                        heavy_src_files=heavy_src_files,
                        copyright=copyright_c))

            return CompilerResp(
                stage="c2unity",
                in_dir=c_src_dir,
                out_dir=out_dir,
                compile_time=time.time() - tick
            )

        except Exception as e:
            return CompilerResp(
                stage="c2unity",
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
