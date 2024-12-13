import jinja2
import os
import shutil
import time
import json2daisy  # type: ignore

from typing import Any, Dict, Optional

from ..copyright import copyright_manager
from . import parameters

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.compiler import Generator, CompilerResp, CompilerNotif, CompilerMsg, ExternInfo
from hvcc.types.meta import Meta, Daisy


hv_midi_messages = {
    "__hv_noteout",
    "__hv_ctlout",
    "__hv_polytouchout",
    "__hv_pgmout",
    "__hv_touchout",
    "__hv_bendout",
    "__hv_midiout",
    "__hv_midioutport"
}


class c2daisy(Generator):
    """ Generates a Daisy wrapper for a given patch.
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

        out_dir = os.path.join(out_dir, "daisy")

        daisy_meta: Daisy = patch_meta.daisy
        board = daisy_meta.board

        copyright_c = copyright_manager.get_copyright_for_c(copyright)

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

            if daisy_meta.board_file is not None:
                header, board_info = json2daisy.generate_header_from_file(daisy_meta.board_file)
            else:
                header, board_info = json2daisy.generate_header_from_name(board)

            # remove heavy out params from externs
            externs.parameters.outParam = [
                t for t in externs.parameters.outParam if not any(x == y for x in hv_midi_messages for y in t)]

            component_glue = parameters.parse_parameters(
                externs.parameters, board_info['components'], board_info['aliases'], 'hardware')
            component_glue['class_name'] = board_info['name']
            component_glue['patch_name'] = patch_name
            component_glue['header'] = f"HeavyDaisy_{patch_name}.hpp"
            component_glue['max_channels'] = board_info['channels']
            component_glue['num_output_channels'] = num_output_channels
            component_glue['has_midi'] = board_info['has_midi']
            component_glue['displayprocess'] = board_info['displayprocess']
            component_glue['debug_printing'] = daisy_meta.debug_printing
            component_glue['usb_midi'] = daisy_meta.usb_midi
            component_glue['pool_sizes_kb'] = externs.memoryPoolSizesKb

            # samplerate
            samplerate = daisy_meta.samplerate
            if samplerate >= 96000:
                component_glue['samplerate'] = 96000
            elif samplerate >= 48000:
                component_glue['samplerate'] = 48000
            elif samplerate >= 32000:
                component_glue['samplerate'] = 32000
            elif samplerate >= 16000:
                component_glue['samplerate'] = 16000
            else:
                component_glue['samplerate'] = 8000

            # blocksize
            blocksize = daisy_meta.blocksize
            if blocksize is not None:
                component_glue['blocksize'] = max(min(256, blocksize), 1)
            else:
                component_glue['blocksize'] = None

            component_glue['copyright'] = copyright_c

            daisy_h_path = os.path.join(source_dir, f"HeavyDaisy_{patch_name}.hpp")
            with open(daisy_h_path, "w") as f:
                f.write(header)

            loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
            env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
            daisy_cpp_path = os.path.join(source_dir, f"HeavyDaisy_{patch_name}.cpp")

            rendered_cpp = env.get_template('HeavyDaisy.cpp').render(component_glue)
            with open(daisy_cpp_path, 'w') as f:
                f.write(rendered_cpp)

            makefile_replacements: Dict[str, Any] = {'name': patch_name}
            makefile_replacements['linker_script'] = daisy_meta.linker_script

            # libdaisy path
            path = daisy_meta.libdaisy_path
            if isinstance(path, int):
                makefile_replacements['libdaisy_path'] = f'{"../" * path}libdaisy'
            elif isinstance(path, str):
                makefile_replacements['libdaisy_path'] = path

            makefile_replacements['bootloader'] = daisy_meta.bootloader
            makefile_replacements['debug_printing'] = daisy_meta.debug_printing

            rendered_makefile = env.get_template('Makefile').render(makefile_replacements)
            with open(os.path.join(source_dir, "Makefile"), "w") as f:
                f.write(rendered_makefile)

            # ======================================================================================

            return CompilerResp(
                stage="c2daisy",
                in_dir=c_src_dir,
                out_dir=out_dir,
                out_file=os.path.basename(daisy_h_path),
                compile_time=time.time() - tick
            )

        except Exception as e:
            return CompilerResp(
                stage="c2daisy",
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
