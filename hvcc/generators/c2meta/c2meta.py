# Copyright (C) 2026 Wasted Audio
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

import shutil
import time
import jinja2

from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from hvcc.generators.copyright import copyright_manager
from hvcc.generators.filters import filter_uniqueid

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.compiler import Generator, CompilerResp, CompilerMsg, CompilerNotif, ExternInfo
from hvcc.types.meta import Meta


class mmJson(BaseModel):
    MetaModulePluginMaintainer: str
    MetaModulePluginMaintainerEmail: str
    MetaModulePluginMaintainerUrl: str
    MetaModuleDescription: str


class c2meta(Generator):
    """ Generates a Meta wrapper for a given patch.
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

        out_dir = Path(out_dir, "plugin")
        receiver_list = externs.parameters.inParam
        sender_list = externs.parameters.outParam

        mm_meta = patch_meta.meta

        copyright_c = copyright_manager.get_copyright_for_c(copyright)

        try:
            # ensure that the output directory does not exist
            out_dir = out_dir.absolute()
            if out_dir.exists():
                shutil.rmtree(out_dir)

            # copy over static files
            shutil.copytree(Path(Path(__file__).parent, "static"), out_dir)

            # copy over generated C source files
            source_dir = Path(out_dir, "source")
            shutil.copytree(c_src_dir, source_dir)

            # initialize the jinja template environment
            env = jinja2.Environment()
            env.filters["uniqueid"] = filter_uniqueid

            env.loader = jinja2.FileSystemLoader(
                Path(Path(__file__).parent, "templates"))

            # generate Meta wrapper from template
            mm_h_path = Path(source_dir, f"HeavyMetaModule_{patch_name}.hpp")
            with open(mm_h_path, "w") as f:
                f.write(env.get_template("HeavyMetaModule.hpp").render(
                    name=patch_name,
                    meta=mm_meta,
                    class_name=f"HeavyMetaModule_{patch_name}",
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    senders=sender_list,
                    copyright=copyright_c))

            # generate Meta wrapper from template
            mm_c_path = Path(source_dir, f"HeavyMetaModule_{patch_name}.cpp")
            with open(mm_c_path, "w") as f:
                f.write(env.get_template("HeavyMetaModule.cpp").render(
                    name=patch_name,
                    meta=mm_meta,
                    class_name=f"HeavyMetaModule_{patch_name}",
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    senders=sender_list,
                    copyright=copyright_c))

            # generate plugin.cpp
            plugin_cpp = Path(source_dir, "plugin.cpp")
            with open(plugin_cpp, "w") as f:
                f.write(env.get_template("plugin.cpp").render(
                    name=patch_name
                ))

            # generate elements.cpp
            elements_cpp = Path(source_dir, f"{patch_name.lower()}_elements.cpp")
            with open(elements_cpp, "w") as f:
                f.write(env.get_template("elements.cpp").render(
                    name=patch_name,
                    meta=mm_meta
                ))

            # generate plugin CMakeLists.txt
            mm_cmake_path = Path(out_dir, "CMakeLists.txt")
            with open(mm_cmake_path, "w") as f:
                f.write(env.get_template("CMakeLists.txt").render(
                    name=patch_name,
                    meta=mm_meta))

            # generate root CMakeLists.txt
            root_cmake_path = Path(out_dir, "../CMakeLists.txt")
            with open(root_cmake_path, "w") as f:
                f.write(env.get_template("CMakeLists_root.txt").render(
                    name=patch_name,
                    meta=mm_meta))

            plugin_json_path = Path(out_dir, "plugin.json")
            plugin_json = mm_meta

            with open(plugin_json_path, "w") as f:
                f.write(plugin_json.model_dump_json(indent=4))


            mm_json_path = Path(out_dir, "plugin-mm.json")
            mm_json = mmJson(
                MetaModulePluginMaintainer="Wasted Audio",
                MetaModulePluginMaintainerEmail="developer@wasted.audio",
                MetaModulePluginMaintainerUrl="https://wasted.audio",
                MetaModuleDescription=mm_meta.description
            )

            with open(mm_json_path, "w") as f:
                f.write(mm_json.model_dump_json(indent=4))

            asset_dir = Path(out_dir, "assets")
            shutil.copytree(Path(Path(__file__).parent, "assets"), asset_dir)

            return CompilerResp(
                stage="c2meta",
                in_dir=c_src_dir,
                out_dir=out_dir,
                out_file=mm_h_path.absolute().parent,
                compile_time=time.time() - tick
            )

        except Exception as e:
            return CompilerResp(
                stage="c2meta",
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
