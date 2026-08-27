# Heavy Compiler Collection
# Copyright (C) 2024-2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import jinja2
import os
import shutil
import time

from typing import Optional
from pathlib import Path

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.compiler import Generator, CompilerResp, CompilerNotif, CompilerMsg, ExternInfo
from hvcc.types.meta import Meta

from ..copyright import copyright_manager


class c2fmod(Generator):
    """Generates a FMOD plugin wrapper for a given patch."""

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
        verbose: Optional[bool] = False,
    ) -> CompilerResp:
        tick = time.time()

        patch_name = patch_name.lower() if patch_name is not None else "heavy"

        in_parameter_list = externs.parameters.inParam
        out_parameter_list = externs.parameters.outParam
        event_list = externs.events.inEvent
        out_event_list = externs.events.outEvent
        table_list = externs.tables

        copyright_c = copyright_manager.get_copyright_for_c(copyright)

        templates_dir = Path(__file__).parent / "templates"
        is_source_plugin = num_input_channels == 0

        out_dir = Path(out_dir, "fmod")
        if not out_dir.exists():
            out_dir.mkdir(parents=True)

        env = jinja2.Environment()
        env.loader = jinja2.FileSystemLoader(
            encoding="utf-8-sig", searchpath=[templates_dir]
        )

        try:

            patch_src_dir = Path(out_dir, "include", "Heavy")
            if patch_src_dir.exists():
                shutil.rmtree(patch_src_dir)
            shutil.copytree(c_src_dir, patch_src_dir)

            heavy_src_files = [f for f in os.listdir(c_src_dir) if f.endswith(".c") or f.endswith(".cpp")]

            src_ext_list = ["h", "hpp", "c", "cpp", "js", "md", "txt"]

            for f in env.list_templates(extensions=src_ext_list):
                file = Path(f)
                file_dir = Path(out_dir, file.parent)

                file_name = file.name.replace("{{name}}", patch_name)
                file_path = Path(file_dir, file_name)

                if not file_path.parent.exists():
                    file_path.parent.mkdir(parents=True)

                with open(file_path, "w") as g:
                    g.write(env.get_template(f).render(
                        name=patch_name,
                        in_params=in_parameter_list,
                        out_params=out_parameter_list,
                        out_events=out_event_list,
                        events=event_list,
                        tables=table_list,
                        pool_sizes_kb=externs.memoryPoolSizesKb,
                        is_source_plugin=is_source_plugin,
                        num_input_channels=num_input_channels,
                        num_output_channels=num_output_channels,
                        heavy_src_files=heavy_src_files,
                        copyright=copyright_c))

            return CompilerResp(
                stage="c2fmod",
                in_dir=c_src_dir,
                out_dir=out_dir,
                compile_time=time.time() - tick
            )

        except Exception as e:
            return CompilerResp(
                stage="c2fmod",
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
