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

import shutil
import time
import jinja2

from typing import Optional
from pathlib import Path

from ..copyright import copyright_manager
from ..filters import filter_plugin_id

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.compiler import Generator, CompilerResp, CompilerNotif, CompilerMsg, ExternInfo
from hvcc.types.meta import Meta


class c2wwise(Generator):
    """Generates a plugin wrapper for Audiokinetic's Wwise game audio middleware
    platform.
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

        in_parameter_list = externs.parameters.inParam
        out_parameter_list = externs.parameters.outParam
        event_list = externs.events.inEvent
        out_event_list = externs.events.outEvent
        table_list = externs.tables
        patch_name = patch_name or "heavy"
        copyright_c = copyright_manager.get_copyright_for_c(copyright)
        copyright_xml = copyright_manager.get_copyright_for_xml(copyright)

        templates_dir = Path(__file__).parent / "templates"
        is_source_plugin = num_input_channels == 0
        plugin_type = "Source" if is_source_plugin else "FX"
        plugin_id = filter_plugin_id(patch_name)

        out_dir = Path(out_dir, "wwise")
        if not out_dir.exists():
            out_dir.mkdir()

        env = jinja2.Environment()
        env.loader = jinja2.FileSystemLoader(
            encoding="utf-8-sig",
            searchpath=[templates_dir])
        try:
            channel_config = None
            if num_output_channels == 0:
                # Workaround to support patches that don't have any outputs,
                # e.g. that only ever set RTPCs or post events
                channel_config = "AK_SPEAKER_SETUP_MONO"
            elif num_output_channels == 1:
                channel_config = "AK_SPEAKER_SETUP_MONO"
            elif num_output_channels == 2:
                channel_config = "AK_SPEAKER_SETUP_STEREO"
            elif num_output_channels == 6:
                channel_config = "AK_SPEAKER_SETUP_5POINT1"
            elif num_output_channels == 8:
                channel_config = "AK_SPEAKER_SETUP_7POINT1"
            elif num_output_channels == 12:
                channel_config = "AK_SPEAKER_SETUP_DOLBY_7_1_4"
            else:
                raise Exception("Wwise plugins support only mono, stereo, 5.1, 7.1, "
                                "and 7.1.4 (Atmos) configurations, number of [dac~] channels should be appropriate")

            if plugin_type == "FX":
                if num_input_channels != num_output_channels:
                    raise Exception("Wwise FX plugins require the same input/output channel"
                                    "configuration (i.e. [adc~ 1] -> [dac~ 1]).")

            patch_src_dir = Path(out_dir, "SoundEnginePlugin", "Heavy")
            if patch_src_dir.exists():
                shutil.rmtree(patch_src_dir)
            shutil.copytree(c_src_dir, patch_src_dir)

            src_ext_list = ["h", "hpp", "c", "cpp", "xml", "def", "rc", "lua", "json"]
            for f in env.list_templates(extensions=src_ext_list):
                file = Path(f)
                file_dir = Path(out_dir, file.parent)

                file_name = file.name.replace("{{name}}", patch_name)
                file_name = file_name.replace("{{plugin_type}}", plugin_type)
                file_path = Path(file_dir, file_name)

                if not file_path.parent.exists():
                    file_path.parent.mkdir(parents=True)

                with open(file_path, "w") as g:
                    g.write(env.get_template(f).render(
                        name=patch_name,
                        parameters=in_parameter_list,
                        out_params=out_parameter_list,
                        out_events=out_event_list,
                        events=event_list,
                        tables=table_list,
                        pool_sizes_kb=externs.memoryPoolSizesKb,
                        is_source=is_source_plugin,
                        num_input_channels=num_input_channels,
                        num_output_channels=num_output_channels,
                        channel_config=channel_config,
                        plugin_type=plugin_type,
                        plugin_id=plugin_id,
                        copyright=copyright_xml if file_name.endswith(".xml") else copyright_c))

            return CompilerResp(
                stage="c2wwise",
                in_dir=c_src_dir,
                out_dir=out_dir,
                compile_time=time.time() - tick
            )

        except Exception as e:
            return CompilerResp(
                stage="c2wwise",
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
